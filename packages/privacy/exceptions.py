class PrivacyEngineError(Exception):
    """Base exception for privacy engine errors."""

    pass


class ScaleOutOfRangeError(PrivacyEngineError):
    """Raised if FHE encoding parameters scale outside the noise budget boundaries."""

    pass


class DecryptionFailure(PrivacyEngineError):
    """Raised when decryption is attempted with a corrupted or missing key."""

    pass


class CryptographicMismatchError(PrivacyEngineError):
    """Raised when encrypted updates do not share a context or scale."""

    pass


class SecAggDropoutError(PrivacyEngineError):
    """Raised when a masked client is missing and its mask cannot be cancelled."""

    pass
