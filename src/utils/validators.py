"""
🌙 Moon Dev's Input Validation Utilities
Built with security in mind 🔒

This module provides validation functions for trading inputs to prevent
security vulnerabilities and data corruption.
"""

import re
from typing import Union, Optional
from decimal import Decimal, InvalidOperation


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


def validate_solana_address(address: str, field_name: str = "address") -> str:
    """
    Validate a Solana address format.

    Args:
        address: The Solana address to validate
        field_name: Name of the field for error messages

    Returns:
        The validated address

    Raises:
        ValidationError: If address is invalid

    Examples:
        >>> validate_solana_address("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
        'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'
    """
    if not address:
        raise ValidationError(f"{field_name} cannot be empty")

    if not isinstance(address, str):
        raise ValidationError(f"{field_name} must be a string, got {type(address)}")

    # Solana addresses are base58 encoded and typically 32-44 characters
    if not (32 <= len(address) <= 44):
        raise ValidationError(
            f"{field_name} must be between 32-44 characters, got {len(address)}"
        )

    # Base58 alphabet (no 0, O, I, l)
    base58_pattern = r'^[1-9A-HJ-NP-Za-km-z]+$'
    if not re.match(base58_pattern, address):
        raise ValidationError(
            f"{field_name} contains invalid characters (must be base58)"
        )

    return address


def validate_ethereum_address(address: str, field_name: str = "address") -> str:
    """
    Validate an Ethereum address format.

    Args:
        address: The Ethereum address to validate
        field_name: Name of the field for error messages

    Returns:
        The validated address

    Raises:
        ValidationError: If address is invalid
    """
    if not address:
        raise ValidationError(f"{field_name} cannot be empty")

    if not isinstance(address, str):
        raise ValidationError(f"{field_name} must be a string, got {type(address)}")

    # Ethereum addresses are 42 characters (0x + 40 hex chars)
    if not address.startswith('0x'):
        raise ValidationError(f"{field_name} must start with '0x'")

    if len(address) != 42:
        raise ValidationError(
            f"{field_name} must be 42 characters (0x + 40 hex), got {len(address)}"
        )

    # Check if hex
    try:
        int(address[2:], 16)
    except ValueError:
        raise ValidationError(f"{field_name} contains invalid hex characters")

    return address.lower()  # Normalize to lowercase


def validate_usd_amount(
    amount: Union[int, float, str, Decimal],
    min_value: float = 0.01,
    max_value: float = 1_000_000,
    field_name: str = "amount"
) -> Decimal:
    """
    Validate a USD amount.

    Args:
        amount: The USD amount to validate
        min_value: Minimum allowed value (default: $0.01)
        max_value: Maximum allowed value (default: $1,000,000)
        field_name: Name of the field for error messages

    Returns:
        The validated amount as Decimal

    Raises:
        ValidationError: If amount is invalid

    Examples:
        >>> validate_usd_amount(100.50)
        Decimal('100.50')
    """
    # Convert to Decimal for precise financial calculations
    try:
        if isinstance(amount, str):
            # Remove common currency symbols
            amount = amount.replace('$', '').replace(',', '').strip()
        decimal_amount = Decimal(str(amount))
    except (InvalidOperation, ValueError, TypeError) as e:
        raise ValidationError(
            f"{field_name} must be a valid number, got '{amount}': {e}"
        )

    # Check if positive
    if decimal_amount <= 0:
        raise ValidationError(f"{field_name} must be positive, got {decimal_amount}")

    # Check range
    if decimal_amount < Decimal(str(min_value)):
        raise ValidationError(
            f"{field_name} must be at least ${min_value}, got ${decimal_amount}"
        )

    if decimal_amount > Decimal(str(max_value)):
        raise ValidationError(
            f"{field_name} must be at most ${max_value}, got ${decimal_amount}"
        )

    return decimal_amount


def validate_percentage(
    percentage: Union[int, float, str],
    min_value: float = 0,
    max_value: float = 100,
    field_name: str = "percentage"
) -> float:
    """
    Validate a percentage value.

    Args:
        percentage: The percentage to validate
        min_value: Minimum allowed value (default: 0)
        max_value: Maximum allowed value (default: 100)
        field_name: Name of the field for error messages

    Returns:
        The validated percentage as float

    Raises:
        ValidationError: If percentage is invalid

    Examples:
        >>> validate_percentage(50)
        50.0
    """
    try:
        if isinstance(percentage, str):
            percentage = percentage.replace('%', '').strip()
        float_percentage = float(percentage)
    except (ValueError, TypeError) as e:
        raise ValidationError(
            f"{field_name} must be a valid number, got '{percentage}': {e}"
        )

    if not (min_value <= float_percentage <= max_value):
        raise ValidationError(
            f"{field_name} must be between {min_value}% and {max_value}%, "
            f"got {float_percentage}%"
        )

    return float_percentage


def validate_token_symbol(
    symbol: str,
    min_length: int = 1,
    max_length: int = 20,
    field_name: str = "symbol"
) -> str:
    """
    Validate a token symbol.

    Args:
        symbol: The token symbol to validate
        min_length: Minimum symbol length (default: 1)
        max_length: Maximum symbol length (default: 20)
        field_name: Name of the field for error messages

    Returns:
        The validated and uppercase symbol

    Raises:
        ValidationError: If symbol is invalid

    Examples:
        >>> validate_token_symbol("btc")
        'BTC'
    """
    if not symbol:
        raise ValidationError(f"{field_name} cannot be empty")

    if not isinstance(symbol, str):
        raise ValidationError(f"{field_name} must be a string, got {type(symbol)}")

    symbol = symbol.strip().upper()

    if not (min_length <= len(symbol) <= max_length):
        raise ValidationError(
            f"{field_name} must be between {min_length}-{max_length} characters, "
            f"got {len(symbol)}"
        )

    # Allow alphanumeric and some special chars
    if not re.match(r'^[A-Z0-9\-\_]+$', symbol):
        raise ValidationError(
            f"{field_name} contains invalid characters (only A-Z, 0-9, -, _ allowed)"
        )

    return symbol


def validate_api_key(
    api_key: str,
    min_length: int = 20,
    field_name: str = "API key"
) -> str:
    """
    Validate an API key format.

    Args:
        api_key: The API key to validate
        min_length: Minimum key length (default: 20)
        field_name: Name of the field for error messages

    Returns:
        The validated API key

    Raises:
        ValidationError: If API key is invalid
    """
    if not api_key:
        raise ValidationError(f"{field_name} cannot be empty")

    if not isinstance(api_key, str):
        raise ValidationError(f"{field_name} must be a string")

    api_key = api_key.strip()

    if len(api_key) < min_length:
        raise ValidationError(
            f"{field_name} must be at least {min_length} characters"
        )

    # Check for placeholder values
    placeholder_patterns = [
        'your_.*_here',
        'replace_this',
        'xxx+',
        'test_key',
        'example'
    ]

    for pattern in placeholder_patterns:
        if re.search(pattern, api_key, re.IGNORECASE):
            raise ValidationError(
                f"{field_name} appears to be a placeholder value, not a real key"
            )

    return api_key


def sanitize_error_message(error_message: str, max_length: int = 500) -> str:
    """
    Sanitize error messages to prevent information leakage.

    Removes sensitive information like API keys, private keys, wallet addresses.

    Args:
        error_message: The error message to sanitize
        max_length: Maximum length of sanitized message

    Returns:
        Sanitized error message
    """
    if not error_message:
        return ""

    sanitized = str(error_message)

    # Pattern to match potential sensitive data
    sensitive_patterns = [
        (r'[A-Za-z0-9]{32,}', '[REDACTED_KEY]'),  # Long alphanumeric strings
        (r'0x[a-fA-F0-9]{40}', '[REDACTED_ETH_ADDRESS]'),  # Ethereum addresses
        (r'[1-9A-HJ-NP-Za-km-z]{32,44}', '[REDACTED_ADDRESS]'),  # Base58 addresses
        (r'sk-[A-Za-z0-9]{32,}', '[REDACTED_API_KEY]'),  # OpenAI-style keys
        (r'xai-[A-Za-z0-9]{32,}', '[REDACTED_API_KEY]'),  # xAI keys
    ]

    for pattern, replacement in sensitive_patterns:
        sanitized = re.sub(pattern, replacement, sanitized)

    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "... [truncated]"

    return sanitized


def validate_config_value(
    value: any,
    expected_type: type,
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None,
    allowed_values: Optional[list] = None,
    field_name: str = "config value"
) -> any:
    """
    Generic config value validator.

    Args:
        value: The value to validate
        expected_type: Expected type of the value
        min_value: Minimum allowed value for numeric types
        max_value: Maximum allowed value for numeric types
        allowed_values: List of allowed values (whitelist)
        field_name: Name of the field for error messages

    Returns:
        The validated value

    Raises:
        ValidationError: If value is invalid
    """
    # Type check
    if not isinstance(value, expected_type):
        raise ValidationError(
            f"{field_name} must be {expected_type.__name__}, got {type(value).__name__}"
        )

    # Whitelist check
    if allowed_values is not None and value not in allowed_values:
        raise ValidationError(
            f"{field_name} must be one of {allowed_values}, got '{value}'"
        )

    # Range check for numeric types
    if isinstance(value, (int, float)):
        if min_value is not None and value < min_value:
            raise ValidationError(
                f"{field_name} must be at least {min_value}, got {value}"
            )
        if max_value is not None and value > max_value:
            raise ValidationError(
                f"{field_name} must be at most {max_value}, got {value}"
            )

    return value


# Convenience function for multiple validations
def validate_all(**validations) -> dict:
    """
    Perform multiple validations at once.

    Args:
        **validations: Dict of field_name: (value, validator_func, *args)

    Returns:
        Dict of validated values

    Raises:
        ValidationError: If any validation fails

    Example:
        >>> validate_all(
        ...     wallet=('EPjFWdd...', validate_solana_address),
        ...     amount=(100, validate_usd_amount, 1, 1000)
        ... )
    """
    results = {}
    errors = []

    for field_name, validation_tuple in validations.items():
        value = validation_tuple[0]
        validator = validation_tuple[1]
        args = validation_tuple[2:] if len(validation_tuple) > 2 else ()

        try:
            results[field_name] = validator(value, *args, field_name=field_name)
        except ValidationError as e:
            errors.append(str(e))

    if errors:
        raise ValidationError(f"Validation failed:\n  - " + "\n  - ".join(errors))

    return results
