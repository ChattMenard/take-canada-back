"""Server-side URL fetcher for one-click evidence collection.

Fetches a public web resource, captures retrieval metadata (final URL after
redirects, HTTP status, content type), and returns the raw bytes for hashing
and storage. Includes an SSRF guard so the collector cannot be tricked into
reaching internal/private network addresses.

Uses httpx for simple pages, falls back to Playwright (headless Chromium) for
sites behind CDN/Akamai bot protection (e.g. canada.ca).
"""

import ipaddress
import logging
import socket
from dataclasses import dataclass, field
from datetime import datetime, timezone
from urllib.parse import unquote, urlparse

import httpx

from .config import settings

logger = logging.getLogger(__name__)


class FetchError(Exception):
    """Raised when a URL cannot be safely or successfully fetched."""


@dataclass
class FetchedResource:
    content: bytes
    content_type: str
    final_url: str
    status_code: int
    filename: str
    fetched_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    screenshot: bytes | None = None  # PNG screenshot bytes for visual evidence


_NAT64_PREFIX = ipaddress.IPv6Network("64:ff9b::/96")


def _canonical_ip(ip: ipaddress._BaseAddress) -> ipaddress._BaseAddress:
    """Translate IPv4-mapped / NAT64 IPv6 addresses to their embedded IPv4.

    Networks running DNS64/NAT64 return IPv6 addresses (e.g. in 64:ff9b::/96)
    that embed a real, public IPv4 destination. We must judge the embedded IPv4,
    not the synthetic IPv6 wrapper.
    """
    if isinstance(ip, ipaddress.IPv6Address):
        if ip.ipv4_mapped is not None:
            return ip.ipv4_mapped
        if ip in _NAT64_PREFIX:
            return ipaddress.IPv4Address(int(ip) & 0xFFFFFFFF)
    return ip


def _is_blocked_ip(ip: ipaddress._BaseAddress) -> bool:
    ip = _canonical_ip(ip)
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


def _validate_host(host: str) -> None:
    """Reject hosts that resolve to private/loopback/reserved addresses."""
    if settings.allow_private_collect:
        return
    if not host:
        raise FetchError("URL has no host.")
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise FetchError(f"Could not resolve host {host!r}: {exc}") from exc
    for info in infos:
        addr = info[4][0]
        try:
            ip = ipaddress.ip_address(addr)
        except ValueError:
            continue
        if _is_blocked_ip(ip):
            raise FetchError(
                f"Refusing to fetch {host!r}: resolves to non-public address {addr}."
            )


def _validate_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise FetchError("Only http(s) URLs can be collected.")
    _validate_host(parsed.hostname or "")
    return parsed.hostname or ""


def _filename_from(url: str, content_type: str, headers: httpx.Headers) -> str:
    # Prefer Content-Disposition filename, then URL path, then a typed default.
    disp = headers.get("content-disposition", "")
    if "filename=" in disp:
        name = disp.split("filename=", 1)[1].strip().strip('"').split(";")[0]
        if name:
            return unquote(name)
    path = urlparse(url).path
    if path and "/" in path:
        candidate = unquote(path.rsplit("/", 1)[-1])
        if candidate and "." in candidate:
            return candidate
        # If path has no extension, use the last non-empty segment as base
        if candidate:
            ext = {
                "application/pdf": ".pdf",
                "text/html": ".html",
                "application/json": ".json",
                "image/png": ".png",
                "image/jpeg": ".jpg",
            }.get(content_type.split(";")[0].strip(), "")
            return f"{candidate}{ext}" if ext else candidate
    # Fallback: use domain name as base
    domain = urlparse(url).netloc.replace("www.", "")
    ext = {
        "application/pdf": ".pdf",
        "text/html": ".html",
        "application/json": ".json",
        "image/png": ".png",
        "image/jpeg": ".jpg",
    }.get(content_type.split(";")[0].strip(), "")
    return f"{domain}{ext}"


async def _fetch_with_httpx(url: str) -> FetchedResource:
    """Fetch a URL with httpx — manual, validated redirect handling and a size cap."""
    max_bytes = settings.max_upload_mb * 1024 * 1024
    current = url
    _validate_url(current)

    cookies = httpx.Cookies()

    async with httpx.AsyncClient(
        follow_redirects=False,
        timeout=httpx.Timeout(
            settings.collect_timeout_seconds,
            connect=15.0,
            read=45.0,
        ),
        http2=False,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json;q=0.8,*/*;q=0.7",
            "Accept-Language": "en-CA,en;q=0.9,fr-CA;q=0.8,fr;q=0.7",
        },
        cookies=cookies,
    ) as client:
        for _ in range(settings.collect_max_redirects + 1):
            resp = await client.get(current)

            # Catch all redirect status codes explicitly (301-308)
            if resp.status_code in (301, 302, 303, 307, 308):
                location = resp.headers.get("location")
                if not location:
                    raise FetchError("Redirect without a Location header.")
                current = str(resp.url.join(location))
                _validate_url(current)  # re-check every hop (SSRF on redirect)
                continue

            if resp.status_code >= 400:
                raise FetchError(f"Source returned HTTP {resp.status_code}.")

            content = resp.content
            if len(content) == 0:
                raise FetchError("Source returned an empty body.")
            if len(content) > max_bytes:
                raise FetchError(
                    f"Resource exceeds {settings.max_upload_mb} MB limit."
                )

            content_type = resp.headers.get("content-type", "application/octet-stream")
            return FetchedResource(
                content=content,
                content_type=content_type,
                final_url=str(resp.url),
                status_code=resp.status_code,
                filename=_filename_from(str(resp.url), content_type, resp.headers),
            )

    raise FetchError("Too many redirects.")


async def _fetch_with_playwright(url: str) -> FetchedResource:
    """Fallback: stealth headless Chromium — bypasses Cloudflare/CDN bot detection.
    
    Captures both the rendered DOM (HTML) and a screenshot for comprehensive evidence.
    """
    from playwright.async_api import async_playwright
    from playwright_stealth import Stealth

    max_bytes = settings.max_upload_mb * 1024 * 1024

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ],
        )
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="en-CA",
            viewport={"width": 1920, "height": 1080},
            java_script_enabled=True,
        )
        page = await context.new_page()
        await Stealth().apply_stealth_async(page)

        try:
            resp = await page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # Wait for Cloudflare JS challenge to complete
            if resp and resp.status in (403, 429, 503):
                logger.info("CF/bot challenge detected (HTTP %s), waiting...", resp.status)
                try:
                    await page.wait_for_load_state("networkidle", timeout=25000)
                except Exception:
                    pass
                await page.wait_for_timeout(4000)

            # Read post-JS-render content from DOM (not raw response bytes)
            final_url = page.url
            html = await page.content()
            content = html.encode("utf-8")

            # Capture screenshot for visual evidence
            screenshot = await page.screenshot(full_page=True, type="png")

            if len(content) < 500 or "Please enable JS" in html or "Verification Required" in html:
                raise FetchError("Cloudflare bot challenge not resolved.")

            if len(content) > max_bytes:
                raise FetchError(f"Resource exceeds {settings.max_upload_mb} MB limit.")

            content_type = (resp.headers.get("content-type") if resp else None) or "text/html; charset=utf-8"
            filename = _filename_from(final_url, content_type, resp.headers if resp else {})
            status_code = resp.status if resp else 200

            return FetchedResource(
                content=content,
                content_type=content_type,
                final_url=final_url,
                status_code=status_code,
                filename=filename,
                screenshot=screenshot,
            )
        finally:
            await browser.close()


async def fetch_url(url: str) -> FetchedResource:
    """Fetch a URL. Tries httpx first, falls back to Playwright for CDN sites."""
    try:
        return await _fetch_with_httpx(url)
    except FetchError as exc:
        logger.info("httpx fetch failed (%s), trying Playwright fallback...", exc)
        return await _fetch_with_playwright(url)
    except Exception as exc:
        logger.info("httpx fetch error (%s), trying Playwright fallback...", exc)
        return await _fetch_with_playwright(url)
