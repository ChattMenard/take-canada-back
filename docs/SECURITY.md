# Security Policy

## Scope

Veritas preserves potentially sensitive public-record evidence. Two security
surfaces matter most:

1. **Integrity** — can stored evidence or the custody log be altered without
   detection? (See [INTEGRITY.md](./INTEGRITY.md).)
2. **Confidentiality / access** — who can read or modify the vault.

## Current security posture (be aware)

- **No authentication** is implemented yet. The backend is intended for local or
  trusted-network use only. **Do not expose it directly to the public internet.**
- **Tamper-detection, not tamper-proof.** Ordinary handling that alters a file is
  detectable via verification, but a privileged attacker with write access to
  both the database and the object store could rewrite both. Hash-chaining and
  external anchoring are on the [roadmap](./ROADMAP.md).
- **SQLite is single-writer.** Concurrent uploads will serialize on the write
  lock. For multi-user or production use, move to PostgreSQL (also on the
  roadmap).
- **Data at rest is not encrypted** by the application. Use full-disk or
  filesystem encryption on the host if confidentiality is required.

## Hardening recommendations for operators

- Run behind a VPN, SSH tunnel, or an authenticating reverse proxy.
- Restrict OS permissions on `backend/data/`.
- Keep encrypted, off-machine backups of `backend/data/`.
- Verify evidence integrity on a schedule and before relying on items.

## Reporting a vulnerability

Please **do not** open a public issue for security/integrity vulnerabilities.
Instead, report privately to the repository owner via GitHub (e.g., a private
security advisory on `ChattMenard/Veritas`, or direct contact).

Include:

- a description of the issue and its impact,
- steps to reproduce or a proof of concept,
- any suggested remediation.

We aim to acknowledge reports promptly and will credit reporters who wish to be
named once a fix is available.

## Responsible use

This is an accountability tool. Use it for lawful collection and preservation of
public-record evidence with accurate sourcing. Do not use it to harass
individuals or to publish unverified or defamatory claims.
