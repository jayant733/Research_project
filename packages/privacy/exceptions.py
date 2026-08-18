class PrivacyEngineError(Exception):
    """Base exception for privacy engine errors."""
    pass


class ScaleOutOfRangeError(PrivacyEngineError):
    """Raised if FHE encoding parameters scale outside the noise budget boundaries."""
    pass


class DecryptionFailure(PrivacyEngineError):
    """Raised if key configurations are invalid or if a decryption step is triggered with corrupted keys."""
    pass


class CryptographicMismatchError(PrivacyEngineError):
    """Raised if parameters/updates use mismatched encryption scales, noise budgets, or key rings."""
    pass
