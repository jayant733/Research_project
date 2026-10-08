"""CKKS context ceremony, encrypted weighted aggregation, and aggregate decryption."""

from typing import Optional

import numpy as np
import tenseal as ts

from packages.privacy.exceptions import (
    CryptographicMismatchError,
    DecryptionFailure,
    ScaleOutOfRangeError,
)


def _build_private_context(poly_modulus_degree: int) -> ts.Context:
    if poly_modulus_degree >= 8192:
        coeff_mod_bit_sizes = [60, 40, 60]
        scale = 2**40
    else:
        coeff_mod_bit_sizes = [40, 20, 40]
        scale = 2**20
    context = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=poly_modulus_degree,
        coeff_mod_bit_sizes=coeff_mod_bit_sizes,
    )
    context.global_scale = scale
    context.generate_relin_keys()
    return context


class FHEAuthority:
    """Holds the CKKS secret key and decrypts only aggregated ciphertexts."""

    def __init__(self, private_context: ts.Context) -> None:
        self._context = private_context

    def decrypt(self, ciphertext: bytes, length: int) -> np.ndarray:
        try:
            encrypted = ts.ckks_vector_from(self._context, ciphertext)
            values = np.asarray(encrypted.decrypt(), dtype=np.float64)
        except Exception as exc:
            raise DecryptionFailure(f"Failed to decrypt aggregate: {exc}") from exc
        if values.size < length:
            raise DecryptionFailure("Decrypted vector is shorter than the model.")
        return values[:length]


class ServerFHEEngine:
    """Adds public ciphertexts. This object cannot decrypt individual updates."""

    def __init__(self, public_context: bytes) -> None:
        self.context = ts.context_from(public_context)

    def aggregate(self, ciphertexts: list[bytes], total_samples: float) -> bytes:
        if not ciphertexts:
            raise ValueError("No ciphertexts to aggregate.")
        if total_samples <= 0:
            raise ValueError("Sample count must be positive.")
        try:
            aggregated = ts.ckks_vector_from(self.context, ciphertexts[0])
            for ciphertext in ciphertexts[1:]:
                aggregated += ts.ckks_vector_from(self.context, ciphertext)
            aggregated *= 1.0 / float(total_samples)
            return bytes(aggregated.serialize())
        except Exception as exc:
            raise CryptographicMismatchError(
                f"Failed to aggregate ciphertexts: {exc}"
            ) from exc


class PublicFHEClient:
    """Encrypts with the shared public context and never sees the secret key."""

    def __init__(self, public_context: bytes) -> None:
        self.context = ts.context_from(public_context)

    def encrypt(self, values: np.ndarray) -> bytes:
        try:
            vector = np.asarray(values, dtype=np.float64).ravel().tolist()
            encrypted = ts.ckks_vector(self.context, vector)
            return bytes(encrypted.serialize())
        except Exception as exc:
            raise ScaleOutOfRangeError(f"Failed to encrypt weights: {exc}") from exc


class FHESession:
    """Creates a public context for clients and a separate decryption authority."""

    def __init__(self, poly_modulus_degree: int = 8192) -> None:
        private = _build_private_context(poly_modulus_degree)
        self.public_bytes = bytes(
            private.serialize(
                save_public_key=True,
                save_secret_key=False,
                save_galois_keys=False,
                save_relin_keys=True,
            )
        )
        private_bytes = private.serialize(
            save_public_key=True,
            save_secret_key=True,
            save_galois_keys=False,
            save_relin_keys=True,
        )
        self.authority = FHEAuthority(ts.context_from(private_bytes))
        self.server_engine = ServerFHEEngine(self.public_bytes)

    def client(self) -> PublicFHEClient:
        return PublicFHEClient(self.public_bytes)


class ClientFHEEngine:
    """Backward-compatible client helper that owns a standalone key pair."""

    def __init__(self, poly_modulus_degree: int = 8192) -> None:
        self._session: Optional[FHESession] = FHESession(poly_modulus_degree)

    def encrypt_weights(self, weights: np.ndarray) -> bytes:
        if self._session is None:
            raise ScaleOutOfRangeError("FHE session is closed.")
        return self._session.client().encrypt(np.asarray(weights))

    def decrypt_weights(
        self, ciphertext_bytes: bytes, original_shape: tuple
    ) -> np.ndarray:
        if self._session is None:
            raise DecryptionFailure("FHE session is closed.")
        length = int(np.prod(original_shape, dtype=int))
        values = self._session.authority.decrypt(ciphertext_bytes, length)
        return values.reshape(original_shape)


class FHEEngine(ClientFHEEngine):
    """Legacy alias kept for older imports."""
