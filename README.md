This repository implements a secure, practical file encryption and decryption tool built with modern cryptographic best practices. It is suitable for protecting files before uploading them to cloud storage or sharing via untrusted channels. The implementation uses a hybrid approach combining an authenticated symmetric cipher (AES-256-GCM) for file content with asymmetric key-wrapping (RSA-4096) for secure key transport. Password-based encryption (Argon2id KDF + AES-GCM) is supported for cases without public-key infrastructure.

Key goals:

Confidentiality (AES-256-GCM)

Integrity/authenticity (AEAD built into GCM)

Secure key derivation (Argon2id)

Hybrid mode for sharing between users (RSA wrapping)

Clear file format for portability

Features

Encrypt / decrypt files from the command-line

Generate RSA key pairs (4096-bit recommended)

Password-based encryption with Argon2id-derived keys

Hybrid encryption mode: AES key encrypted with RSA (PKCS#1 OAEP)

Authenticated encryption with AES-256-GCM

Portable encrypted file format containing metadata (version, key-wrap info, nonce)

Minimal dependencies (Python + cryptography and/or pyca/cryptography)

Security notes (read carefully)

This tool aims to implement secure defaults. Do not disable authentication or use weak keys.

Always verify recipients' RSA public keys out-of-band before using them.

Keep private keys offline where possible and protect them with strong passphrases.

Use sufficiently long, high-entropy passwords if using password-based encryption; consider using a password manager.

Follow your organisation's key-rotation and backup policies.

File format (high level)

Encrypted file (binary) layout (version 1):

MAGIC (8 bytes): b'SFEV1.0\0'       # magic + version
HEADER (variable): JSON metadata length + JSON
    JSON includes: {"mode":"hybrid"|"password","kdf":"argon2id"|null,"wrap":"rsa-oaep"|null,
                     "enc":"aes-gcm","rsa_pub_key_id":..., "salt":base64, "argon_params":{...}}
KEY BLOB (variable): if hybrid -> RSA-wrapped AES key; if password -> AES key encrypted via KDF
NONCE (12 bytes for GCM)
CIPHERTEXT (remaining bytes)
AUTH TAG (16 bytes appended by AES-GCM)

This arrangement lets the tool store all required metadata to decrypt the file (except secret keys or passwords).

Requirements

Python 3.10+ (recommended)

cryptography library (pip install cryptography)

argon2-cffi for Argon2id KDF when using password-based mode (pip install argon2-cffi)

Optional (for packaging/tests): pytest

Installation

Clone the repository and install dependencies:

git clone <your-repo-url>
cd secure-file-encryptor
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -r requirements.txt

requirements.txt should include at least:

cryptography>=40.0
argon2-cffi>=21.3
Usage
1) Generate RSA key pair
# Generate a 4096-bit RSA keypair (private.pem and public.pem)
python -m secure_encryptor.cli gen-rsa --out-private private.pem --out-public public.pem --bits 4096


# Protect private key with passphrase (interactive prompt) or supply --passphrase-file
2) Encrypt a file (hybrid mode, for a recipient with RSA public key)
python -m secure_encryptor.cli encrypt \
  --in-file secret.docx \
  --out-file secret.docx.sfe \
  --recipient-pub public.pem \
  --label "project-x"

What happens:

A random 256-bit AES key is generated.

AES-256-GCM encrypts the file using a random 96-bit nonce.

The AES key is wrapped using the recipient's RSA public key with RSA-OAEP (SHA-256).

A small JSON header containing metadata and the base64-encoded wrapped key is prepended to the ciphertext.

3) Decrypt (hybrid mode)
python -m secure_encryptor.cli decrypt \
  --in-file secret.docx.sfe \
  --out-file secret.docx \
  --private-key private.pem

If the private key is encrypted with a passphrase, the CLI will prompt for it or accept --passphrase-file.

4) Password-based encryption
python -m secure_encryptor.cli encrypt \
  --in-file notes.txt \
  --out-file notes.txt.sfe \
  --password
# The CLI prompts for a password (with confirmation)


# Decrypt
python -m secure_encryptor.cli decrypt --in-file notes.txt.sfe --out-file notes.txt --password

Password mode uses Argon2id with conservative parameters (time_cost=4, memory_cost=2**18 KB, parallelism=2) to derive a 256-bit key.

API / Library usage (Python)

Example usage as a library:

from secure_encryptor import crypto


# encrypt to recipient public key
crypto.encrypt_file_hybrid(
    in_path='confidential.zip',
    out_path='confidential.zip.sfe',
    recipient_public_key_path='alice_pub.pem',
    header_info={"filename":"confidential.zip"}
)


# decrypt using private key
crypto.decrypt_file_hybrid(
    in_path='confidential.zip.sfe',
    out_path='confidential.zip',
    private_key_path='alice_priv.pem',
    private_key_passphrase=b'my passphrase'  # or None
)

Library functions exposed (recommended):

generate_rsa_keypair(bits=4096, private_out, public_out, passphrase=None)

encrypt_file_hybrid(in_path, out_path, recipient_public_key_path, header_info=None)

decrypt_file_hybrid(in_path, out_path, private_key_path, passphrase=None)

encrypt_file_password(in_path, out_path, password, argon_options=None)

decrypt_file_password(in_path, out_path, password)

Implementation notes (recommended approach)

Use cryptography.hazmat.primitives.ciphers.aead.AESGCM for AES-GCM.

Use cryptography.hazmat.primitives.asymmetric.rsa for key generation, and padding.OAEP with MGF1 and hashes.SHA256() for wrapping.

For Argon2id, use argon2.low_level.hash_secret_raw to derive a 32-byte key; store the salt and Argon2 parameters in the file header.

Never reuse nonces with the same key. Use securely generated 12-byte (96-bit) nonces for AES-GCM.

Protect private keys with strong passphrases and PBKDF2/Argon2 when serializing PEM if desired.

Tests

Write tests using pytest covering:

Round-trip encrypt/decrypt (hybrid and password modes)

Wrong-passphrase and wrong-key failure modes

Header corruption detection

Large-file streaming encryption (encrypt in chunks while authenticating)

Example CLI (suggested CLI argument patterns)

gen-rsa --out-private PATH --out-public PATH --bits N --passphrase-file PATH

encrypt --in-file PATH --out-file PATH --recipient-pub PATH (hybrid)

encrypt --in-file PATH --out-file PATH --password (password mode)

decrypt --in-file PATH --out-file PATH --private-key PATH (or --password)

Packaging & Distribution

Add setup.cfg / pyproject.toml to publish to PyPI if desired.

Provide a Dockerfile for a reproducible CLI environment.

Contributing

Contributions are welcome. Please open a PR and include tests. Follow secure coding guidelines and keep cryptographic dependencies up to date.

License

MIT License — include LICENSE file.

References & Further Reading

NIST SP 800-38D (GCM)

RFC 8017 (PKCS #1: RSA Cryptography Specifications)
