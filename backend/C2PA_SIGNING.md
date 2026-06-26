# C2PA Signing with Certificates

This guide explains how to configure C2PA manifest signing for cryptographic provenance verification.

## Overview

C2PA manifests can be unsigned (current default) or cryptographically signed. Signed manifests provide stronger provenance guarantees as the signature can be verified against a trusted certificate chain.

## Certificate Requirements

To sign C2PA manifests, you need:

1. **Signing certificate** (PEM format): Public key certificate
2. **Private key** (PEM format): Corresponding private key for signing

The certificate should be from a trusted CA or a self-signed certificate you control.

## Generating a Self-Signed Certificate

For development/testing, generate a self-signed certificate:

```bash
# Generate ECDSA private key (P-256 curve)
openssl ecparam -name prime256v1 -genkey -noout -out c2pa_key.pem

# Generate self-signed certificate
openssl req -new -x509 -key c2pa_key.pem -out c2pa_cert.pem -days 365 \
  -subj "/CN=Veritas Evidence/O=Proofstacked/C=CA"
```

## Configuration

Set the following environment variables:

```bash
export VERITAS_C2PA_CERT_PATH="/path/to/c2pa_cert.pem"
export VERITAS_C2PA_KEY_PATH="/path/to/c2pa_key.pem"
```

Or add to `.env` file:

```text
VERITAS_C2PA_CERT_PATH=/path/to/c2pa_cert.pem
VERITAS_C2PA_KEY_PATH=/path/to/c2pa_key.pem
```

## Signing Algorithm

The implementation uses ES256 (ECDSA with SHA-256) by default, which is the recommended algorithm for C2PA v2.2.

## Verification

Signed manifests can be verified using C2PA tools:

```bash
# Install c2patool
pip install c2patool

# Verify a manifest
c2patool <file> --manifest
```

## Production Considerations

For production use:

1. **Use a certificate from a trusted CA** - This enables verification by third parties
2. **Protect the private key** - Store securely, use hardware security modules (HSM) if available
3. **Certificate rotation** - Plan for certificate expiration and rotation
4. **Certificate chain** - Include intermediate certificates if needed

## Current Behavior

- If certificates are not configured, manifests are generated unsigned
- Unsigned manifests still provide provenance metadata but cannot be cryptographically verified
- This is acceptable for development and internal use cases
