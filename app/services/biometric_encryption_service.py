
import base64
import hashlib
import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import settings


NONCE_LENGTH = 12
KEY_LENGTH = 32


def _get_encryption_key() -> bytes:
    """Load and validate the AES-256 encryption key."""

    encoded_key = settings.digicoc_biometric_encryption_key

    if not encoded_key:
        raise RuntimeError(
            "Biometric encryption key is not configured."
        )

    try:
        key = base64.urlsafe_b64decode(
            encoded_key.encode("utf-8")
        )
    except Exception as exc:
        raise RuntimeError(
            "Biometric encryption key is not valid Base64."
        ) from exc

    if len(key) != KEY_LENGTH:
        raise RuntimeError(
            "Biometric encryption key must contain exactly 32 bytes."
        )

    return key


def get_encryption_key_version() -> str:
    """Return the configured encryption key version."""

    version = settings.digicoc_biometric_encryption_key_version.strip()

    if not version:
        raise RuntimeError(
            "Biometric encryption key version cannot be empty."
        )

    return version


def calculate_template_checksum(template_data: bytes) -> str:
    """Calculate SHA-256 checksum of the original template."""

    if not isinstance(template_data, bytes) or not template_data:
        raise ValueError("Fingerprint template cannot be empty.")

    return hashlib.sha256(template_data).hexdigest()


def encrypt_template(template_data: bytes) -> bytes:
    """Encrypt fingerprint template using AES-256-GCM."""

    if not isinstance(template_data, bytes) or not template_data:
        raise ValueError(
            "Fingerprint template must be non-empty binary data."
        )

    key = _get_encryption_key()
    nonce = os.urandom(NONCE_LENGTH)

    encrypted_data = AESGCM(key).encrypt(
        nonce,
        template_data,
        None,
    )

    return nonce + encrypted_data


def decrypt_template(encrypted_data: bytes) -> bytes:
    """Decrypt a stored template and verify its authentication tag."""

    if not isinstance(encrypted_data, bytes):
        raise ValueError("Encrypted template must be binary data.")

    if len(encrypted_data) <= NONCE_LENGTH:
        raise ValueError("Encrypted template data is incomplete.")

    key = _get_encryption_key()

    nonce = encrypted_data[:NONCE_LENGTH]
    ciphertext = encrypted_data[NONCE_LENGTH:]

    try:
        return AESGCM(key).decrypt(
            nonce,
            ciphertext,
            None,
        )
    except InvalidTag as exc:
        raise ValueError(
            "Template decryption failed. Data or encryption key is invalid."
        ) from exc


def verify_template_checksum(
    template_data: bytes,
    expected_checksum: str,
) -> bool:
    """Verify the SHA-256 checksum of a fingerprint template."""

    if not expected_checksum:
        return False

    actual_checksum = calculate_template_checksum(template_data)

    return actual_checksum.lower() == expected_checksum.lower()
