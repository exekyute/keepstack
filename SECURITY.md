# Security

Keepstack is a young project. This document is an honest description of its current
security posture, so you can deploy it with the right expectations rather than
assumptions.

## The authentication model

- **Passwords** are hashed with scrypt (`hashlib.scrypt`, from the standard
  library) with a per-user random salt. Plaintext passwords are never stored.
- **Sessions are stateless.** A successful login returns a token that is a
  base64url payload (user id, role, expiry) signed with HMAC-SHA256 using a
  server secret, a minimal JWT-style scheme built on the standard library. There
  is no session store to compromise, and tampering invalidates the signature.
- **The server secret** comes from `KEEPSTACK_SECRET_KEY`. If you do not set one, a
  random secret is generated and persisted so tokens survive a restart in
  development. **Set an explicit, long, random `KEEPSTACK_SECRET_KEY` in
  production.** Rotating it invalidates all existing tokens.

## Access control

Four roles (viewer, contributor, editor, admin) are enforced on the server for
every mutating route, not just hidden in the UI. The role hierarchy lives in
`auth.py` and is applied through a `require_role` dependency in `app.py`. Every
state change is written to the audit log with the acting user and client IP.

## Share links

Public share links are unguessable tokens (`secrets.token_urlsafe`). Each link
can carry an expiry, a maximum download count, and a view-only-versus-download
permission, and can be revoked. A revoked or expired link returns an error and
serves nothing.

## What is not hardened yet

Deploy behind a reverse proxy with TLS, and be aware of the current limits:

- No rate limiting on login or share endpoints yet, so put Keepstack behind a proxy
  that provides it for internet-facing use.
- The default bootstrap admin is `admin` / `admin`. Change
  `KEEPSTACK_ADMIN_PASSWORD` before first run, or change the password immediately.
- Uploaded files are stored and served as-is. If you accept untrusted uploads,
  serve downloads from a separate origin and set a strict `Content-Security-Policy`
  at your proxy.
- There is no SSO, MFA, or account lockout yet. These are on the
  [roadmap](ROADMAP.md).

## Reporting a vulnerability

Please open a private security advisory on the repository rather than a public
issue, or contact the maintainer directly. A clear description and a reproduction
are enough to get started; there is no bounty program.
