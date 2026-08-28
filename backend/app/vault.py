import base64
import json
import os
import secrets
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

PREFIX = "aa:v1:"
AAD = b"attackatlas:credential:v1"
DEFAULT_KEY_FILE = "/secrets/credential-vault.json"

_key: bytes | None = None
_key_id: str | None = None
_key_file: Path | None = None


class VaultError(RuntimeError):
    pass


def is_encrypted(value: str | None) -> bool:
    return bool(value) and value.startswith(PREFIX)


def _b64e(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64d(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _write_key_file(path: Path, key: bytes, key_id: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(path.parent, 0o700)
    except PermissionError:
        pass
    payload = {
        "version": 1,
        "mode": "local-key",
        "key_id": key_id,
        # This field is intentionally isolated so a future master-password
        # implementation can replace it with a wrapped_key envelope without
        # re-encrypting every credential in SQLite.
        "key": _b64e(key),
    }
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(path, flags, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, separators=(",", ":"))
            fh.write("\n")
    except Exception:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def _load_key_file(path: Path) -> tuple[bytes, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise VaultError(f"Could not read credential vault key file {path}: {exc}") from exc
    if data.get("version") != 1 or data.get("mode") != "local-key":
        raise VaultError("Unsupported credential vault key format")
    key_id = str(data.get("key_id") or "")
    raw = data.get("key")
    if not key_id or not isinstance(raw, str):
        raise VaultError("Credential vault key file is incomplete")
    try:
        key = _b64d(raw)
    except Exception as exc:
        raise VaultError("Credential vault key is invalid") from exc
    if len(key) != 32:
        raise VaultError("Credential vault key must be 256 bits")
    return key, key_id


def initialize_vault(db_session) -> dict:
    """Load/create the local vault key and migrate legacy plaintext secrets.

    If encrypted secrets already exist and the key file is missing, startup
    fails instead of silently generating a replacement key.
    """
    global _key, _key_id, _key_file
    from .models import Credential

    path = Path(os.environ.get("ATTACKATLAS_VAULT_KEY_FILE", DEFAULT_KEY_FILE))
    rows = db_session.query(Credential).all()
    encrypted_present = any(is_encrypted(row.secret) for row in rows)

    if path.exists():
        key, key_id = _load_key_file(path)
    else:
        if encrypted_present:
            raise VaultError(
                f"Encrypted credentials exist but the vault key is missing: {path}. "
                "Restore credential-vault.json from backup before starting AttackAtlas."
            )
        key = AESGCM.generate_key(bit_length=256)
        key_id = secrets.token_hex(8)
        _write_key_file(path, key, key_id)

    _key, _key_id, _key_file = key, key_id, path

    migrated = 0
    for row in rows:
        if not is_encrypted(row.secret):
            row.secret = encrypt_secret(row.secret or "")
            migrated += 1
    if migrated:
        db_session.commit()

    # Verify that all encrypted rows can be authenticated/decrypted with this key.
    for row in rows:
        decrypt_secret(row.secret)

    return {
        "mode": "local-key",
        "cipher": "AES-256-GCM",
        "key_id": key_id,
        "key_file": str(path),
        "migrated": migrated,
    }


def encrypt_secret(value: str) -> str:
    if _key is None or _key_id is None:
        raise VaultError("Credential vault is not initialized")
    nonce = os.urandom(12)
    ciphertext = AESGCM(_key).encrypt(nonce, value.encode("utf-8"), AAD)
    return f"{PREFIX}{_key_id}:{_b64e(nonce)}:{_b64e(ciphertext)}"


def decrypt_secret(value: str | None) -> str:
    if value is None:
        return ""
    if not is_encrypted(value):
        # Compatibility only. Startup migration encrypts legacy values.
        return value
    if _key is None or _key_id is None:
        raise VaultError("Credential vault is not initialized")
    try:
        _, version, key_id, nonce_text, ciphertext_text = value.split(":", 4)
    except ValueError as exc:
        raise VaultError("Malformed encrypted credential") from exc
    if f"aa:{version}:" != PREFIX:
        raise VaultError("Unsupported credential encryption version")
    if key_id != _key_id:
        raise VaultError(
            f"Credential was encrypted with vault key {key_id}, but loaded key is {_key_id}"
        )
    try:
        plaintext = AESGCM(_key).decrypt(_b64d(nonce_text), _b64d(ciphertext_text), AAD)
        return plaintext.decode("utf-8")
    except Exception as exc:
        raise VaultError("Credential authentication/decryption failed") from exc


def vault_status() -> dict:
    return {
        "initialized": _key is not None,
        "mode": "local-key",
        "cipher": "AES-256-GCM",
        "key_id": _key_id,
        "master_password": False,
        "future_master_password_ready": True,
    }
