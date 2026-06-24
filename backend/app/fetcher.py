"""Server-side URL fetcher for one-click evidence collection.

Fetches a public web resource, captures retrieval metadata (final URL after
redirects, HTTP status, content type), and returns the raw bytes for hashing
and storage. Includes an SSRF guard so the collector cannot be tricked into
reaching internal/private network addresses.
"""

import ipaddress
import socket
from dataclasses import dataclass, field
from datetime import datetime, timezone
from urllib.parse import unquote, urlparse

import httpx

from .config import settings


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
        if candidate:
            return candidate
    ext = {
        "application/pdf": ".pdf",
        "text/html": ".html",
        "application/json": ".json",
        "image/png": ".png",
        "image/jpeg": ".jpg",
    }.get(content_type.split(";")[0].strip(), "")
    return f"collected{ext}"


async def fetch_url(url: str) -> FetchedResource:
    """Fetch a URL with manual, validated redirect handling and a size cap."""
    max_bytes = settings.max_upload_mb * 1024 * 1024
    current = url
    _validate_url(current)

    async with httpx.AsyncClient(
        follow_redirects=False,
        timeout=settings.collect_timeout_seconds,
        headers={"User-Agent": "Veritas-Collector/0.1 (+evidence-preservation)"},
    ) as client:
        for _ in range(settings.collect_max_redirects + 1):
            resp = await client.get(current)
            if resp.is_redirect:
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
