class LLMResolutionError(Exception):
    """Base exception for LLM resolution failures."""


class LLMTimeoutError(LLMResolutionError):
    """The LLM request exceeded the configured timeout."""


class LLMProviderError(LLMResolutionError):
    """The LLM provider failed to produce a valid response."""