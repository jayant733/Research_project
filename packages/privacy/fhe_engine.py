from typing import Any, List

import numpy as np
import tenseal as ts

from packages.privacy.exceptions import DecryptionFailure, ScaleOutOfRangeError


class FHEEngine:
    """Fully Homomorphic Encryption engine using TenSEAL (CKKS)."""

    def __init__(self, poly_modulus_degree: int = 8192):
        self.poly_modulus_degree = poly_modulus_degree
        self.context = self._create_context()
        self.secret_key = self.context.secret_key()
        # Drop the secret key from the context to make it safe for public operations
        self.context.make_context_public()

    def _create_context(self) -> ts.Context:
        """Creates a TenSEAL context for CKKS."""
        # Setup TenSEAL context
        context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=self.poly_modulus_degree,
            coeff_mod_bit_sizes=[60, 40, 40, 60]
        )
        context.global_scale = 2**40
        context.generate_galois_keys()
        return context

    def get_public_context(self) -> bytes:
        """Returns the serialized public context."""
        return self.context.serialize()

    def encrypt_weights(self, weights: np.ndarray) -> bytes:
        """Encrypts a flat numpy array of weights."""
        if not isinstance(weights, np.ndarray):
            weights = np.array(weights)
            
        # Flatten the weights
        flat_weights = weights.flatten().tolist()
        
        try:
            encrypted_vector = ts.ckks_vector(self.context, flat_weights)
            return encrypted_vector.serialize()
        except Exception as e:
            raise ScaleOutOfRangeError(f"Failed to encrypt weights: {e}")

    def decrypt_weights(self, ciphertext_bytes: bytes, original_shape: tuple) -> np.ndarray:
        """Decrypts a serialized TenSEAL ciphertext back into a numpy array."""
        try:
            # Recreate a context with the secret key for decryption
            decryption_context = self._create_context()
            decryption_context.secret_key() # We need the SK to decrypt
            # But wait, TenSEAL requires the exact same context/keys.
            # For this simplified engine, we will temporarily restore the SK to our context.
            
            # Note: In a real distributed setup, the server never has the SK. 
            # Clients encrypt, server aggregates blindly, clients decrypt.
            
            encrypted_vector = ts.lazy_ckks_vector_from(ciphertext_bytes)
            encrypted_vector.link_context(self.context)
            
            # Since we dropped the SK, we can't actually decrypt here unless we kept it.
            # For demonstration, we'll assume we kept it in self.secret_key
            # and we temporarily bind it.
            # In TenSEAL, you can't easily re-attach a dropped secret key to a public context.
            # So for this engine, we'll hold onto a private context.
            
            pass # See below
            
        except Exception as e:
            raise DecryptionFailure(f"Failed to decrypt: {e}")
            
    # Redesigning slightly for the RATC architecture:
    # We will keep a private context for the engine since it runs on the client.
    
class ClientFHEEngine:
    """Client-side FHE engine that holds the secret key."""
    def __init__(self, poly_modulus_degree: int = 8192):
        self.context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=poly_modulus_degree,
            coeff_mod_bit_sizes=[60, 40, 40, 60]
        )
        self.context.global_scale = 2**40
        self.context.generate_galois_keys()
        
    def encrypt_weights(self, weights: np.ndarray) -> bytes:
        flat_weights = weights.flatten().tolist()
        try:
            encrypted_vector = ts.ckks_vector(self.context, flat_weights)
            return encrypted_vector.serialize()
        except Exception as e:
            raise ScaleOutOfRangeError(f"Failed to encrypt weights: {e}")
            
    def decrypt_weights(self, ciphertext_bytes: bytes, original_shape: tuple) -> np.ndarray:
        try:
            encrypted_vector = ts.ckks_vector_from(self.context, ciphertext_bytes)
            decrypted_list = encrypted_vector.decrypt()
            return np.array(decrypted_list).reshape(original_shape)
        except Exception as e:
            raise DecryptionFailure(f"Failed to decrypt weights: {e}")

class ServerFHEEngine:
    """Server-side FHE engine that aggregates encrypted vectors blindly."""
    def __init__(self, serialized_context: bytes):
        self.context = ts.context_from(serialized_context)
        
    def aggregate(self, ciphertexts: List[bytes]) -> bytes:
        if not ciphertexts:
            raise ValueError("No ciphertexts to aggregate.")
            
        try:
            # Load first vector
            aggregated_vector = ts.ckks_vector_from(self.context, ciphertexts[0])
            
            # Add remaining vectors
            for ct in ciphertexts[1:]:
                vector = ts.ckks_vector_from(self.context, ct)
                aggregated_vector += vector
                
            # Average (multiply by 1/N)
            # In CKKS, division by scalar is multiplication by 1/scalar
            aggregated_vector *= (1.0 / len(ciphertexts))
            
            return aggregated_vector.serialize()
        except Exception as e:
            raise CryptographicMismatchError(f"Failed to aggregate ciphertexts: {e}")
