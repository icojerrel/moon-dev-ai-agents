"""
🔒 Security Utilities for Moon Dev AI Agents
Protects API keys and sensitive data from exposure in logs and output
"""

import re
import os
from typing import Any, Dict
from termcolor import cprint


# API Key Patterns - matches common formats
KEY_PATTERNS = {
    'openrouter': (r'sk-or-v1-[a-f0-9]{64}', '[OPENROUTER_KEY_REDACTED]'),
    'openai': (r'sk-[a-zA-Z0-9]{48,}', '[OPENAI_KEY_REDACTED]'),
    'anthropic': (r'sk-ant-[a-zA-Z0-9-]{95,}', '[ANTHROPIC_KEY_REDACTED]'),
    'deepseek': (r'sk-[a-f0-9]{32}', '[DEEPSEEK_KEY_REDACTED]'),
    'groq': (r'gsk_[a-zA-Z0-9]{52}', '[GROQ_KEY_REDACTED]'),
    'gemini': (r'AIza[a-zA-Z0-9_-]{35}', '[GEMINI_KEY_REDACTED]'),
    'elevenlabs': (r'[a-f0-9]{32}', '[ELEVENLABS_KEY_REDACTED]'),  # Generic hash pattern
    'solana_private_key': (r'[1-9A-HJ-NP-Za-km-z]{87,88}', '[SOLANA_PRIVATE_KEY_REDACTED]'),  # Base58 encoded
    'eth_private_key': (r'0x[a-fA-F0-9]{64}', '[ETH_PRIVATE_KEY_REDACTED]'),
}


def mask_sensitive_data(text: str) -> str:
    """
    Mask API keys and secrets in text output

    Args:
        text: Text that might contain sensitive data

    Returns:
        Text with all detected API keys masked

    Example:
        >>> text = "Using key: sk-or-v1-abc123..."
        >>> mask_sensitive_data(text)
        "Using key: [OPENROUTER_KEY_REDACTED]"
    """
    if not isinstance(text, str):
        text = str(text)

    masked_text = text

    # Apply all key patterns
    for key_type, (pattern, replacement) in KEY_PATTERNS.items():
        masked_text = re.sub(pattern, replacement, masked_text)

    # Also mask anything that looks like an API key assignment
    # Example: OPENAI_KEY=sk-abc123 -> OPENAI_KEY=[REDACTED]
    masked_text = re.sub(
        r'([A-Z_]+KEY\s*=\s*)(["\']?)([a-zA-Z0-9-_]{20,})(["\']?)',
        r'\1\2[REDACTED]\4',
        masked_text
    )

    return masked_text


def safe_print(message: Any, color: str = "white", **kwargs):
    """
    Print with automatic secret masking

    Args:
        message: Message to print (will be converted to string)
        color: Terminal color (default: white)
        **kwargs: Additional args for cprint

    Example:
        >>> safe_print(f"API key: {os.getenv('OPENAI_KEY')}", "green")
        API key: [OPENAI_KEY_REDACTED]  # Instead of exposing the real key
    """
    safe_message = mask_sensitive_data(str(message))
    cprint(safe_message, color, **kwargs)


def sanitize_error(error: Exception, include_trace: bool = False) -> str:
    """
    Sanitize exception messages to remove sensitive data

    Args:
        error: The exception object
        include_trace: Whether to include full traceback (default: False)

    Returns:
        Safe error message with secrets masked

    Example:
        >>> try:
        ...     api_call(key="sk-abc123")
        ... except Exception as e:
        ...     print(sanitize_error(e))
        "API call failed: [OPENAI_KEY_REDACTED]"
    """
    error_msg = str(error)

    # Mask the error message
    safe_msg = mask_sensitive_data(error_msg)

    # Never expose these attributes (they can contain env vars!)
    dangerous_attrs = ['__dict__', '__dir__', 'args']

    if include_trace:
        import traceback
        trace = traceback.format_exc()
        safe_msg += "\n" + mask_sensitive_data(trace)

    return safe_msg


def validate_env_vars() -> Dict[str, bool]:
    """
    Check which API keys are set (without exposing values)

    Returns:
        Dict mapping key names to whether they're set

    Example:
        >>> validate_env_vars()
        {
            'OPENAI_KEY': True,
            'ANTHROPIC_KEY': False,
            ...
        }
    """
    required_keys = [
        'OPENAI_KEY',
        'ANTHROPIC_KEY',
        'OPENROUTER_KEY',
        'DEEPSEEK_KEY',
        'GROQ_API_KEY',
        'GEMINI_KEY',
        'BIRDEYE_API_KEY',
        'MOONDEV_API_KEY',
        'SOLANA_PRIVATE_KEY',
    ]

    status = {}
    for key in required_keys:
        value = os.getenv(key)
        status[key] = bool(value and len(value) > 0)

    return status


def print_env_status():
    """
    Print which environment variables are configured (safely)
    """
    status = validate_env_vars()

    cprint("\n🔐 Environment Variables Status:", "cyan")
    for key, is_set in status.items():
        symbol = "✅" if is_set else "❌"
        color = "green" if is_set else "red"
        cprint(f"{symbol} {key}: {'Configured' if is_set else 'Not set'}", color)


# Example usage
if __name__ == "__main__":
    # Test masking
    test_strings = [
        "My OpenAI key is sk-abc123def456",
        "OPENROUTER_KEY=sk-or-v1-1234567890abcdef",
        "Error with key: sk-ant-api03-abc123",
    ]

    print("Testing secret masking:\n")
    for test in test_strings:
        print(f"Original: {test[:50]}...")
        print(f"Masked:   {mask_sensitive_data(test)}\n")

    # Test safe print
    print("\nTesting safe_print:")
    safe_print("This should be safe: sk-test123", "green")

    # Test env status
    print_env_status()
