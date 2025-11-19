#!/usr/bin/env python3
"""
Security Module for Bazzite Gaming Optimizer
Provides authentication, rate limiting, input validation, and security hardening
"""

import re
import time
import hmac
import hashlib
import secrets
import logging
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
from functools import wraps

logger = logging.getLogger(__name__)


class TokenManager:
    """Secure token management with expiration and validation"""

    def __init__(self, secret_key: Optional[str] = None, token_ttl: int = 300):
        """
        Initialize TokenManager

        Args:
            secret_key: Secret key for HMAC signing (generated if not provided)
            token_ttl: Token time-to-live in seconds (default: 300s / 5 minutes)
        """
        self.secret_key = secret_key or secrets.token_hex(32)
        self.token_ttl = token_ttl
        self.active_tokens: Dict[str, Dict] = {}  # token -> {device_id, expires_at, metadata}

    def generate_token(self, device_id: str, metadata: Optional[Dict] = None) -> Tuple[str, float]:
        """
        Generate a secure authentication token

        Args:
            device_id: Unique device identifier
            metadata: Optional metadata to associate with token

        Returns:
            Tuple of (token, expires_at_timestamp)
        """
        # Generate random token
        token = secrets.token_urlsafe(32)

        # Calculate expiration
        expires_at = time.time() + self.token_ttl

        # Store token with metadata
        self.active_tokens[token] = {
            'device_id': device_id,
            'expires_at': expires_at,
            'created_at': time.time(),
            'metadata': metadata or {}
        }

        logger.info(f"Generated token for device {device_id}, expires in {self.token_ttl}s")
        return token, expires_at

    def validate_token(self, token: str) -> Optional[str]:
        """
        Validate token and return device_id if valid

        Args:
            token: Token to validate

        Returns:
            device_id if valid, None if invalid or expired
        """
        if token not in self.active_tokens:
            logger.warning(f"Token validation failed: Token not found")
            return None

        token_data = self.active_tokens[token]

        # Check expiration
        if time.time() > token_data['expires_at']:
            logger.warning(f"Token validation failed: Token expired")
            del self.active_tokens[token]
            return None

        return token_data['device_id']

    def revoke_token(self, token: str) -> bool:
        """
        Revoke a token

        Args:
            token: Token to revoke

        Returns:
            True if token was revoked, False if token didn't exist
        """
        if token in self.active_tokens:
            device_id = self.active_tokens[token]['device_id']
            del self.active_tokens[token]
            logger.info(f"Revoked token for device {device_id}")
            return True
        return False

    def cleanup_expired_tokens(self):
        """Remove expired tokens from storage"""
        current_time = time.time()
        expired_tokens = [
            token for token, data in self.active_tokens.items()
            if current_time > data['expires_at']
        ]

        for token in expired_tokens:
            device_id = self.active_tokens[token]['device_id']
            del self.active_tokens[token]
            logger.debug(f"Cleaned up expired token for device {device_id}")

        if expired_tokens:
            logger.info(f"Cleaned up {len(expired_tokens)} expired tokens")


class RateLimiter:
    """Rate limiting to prevent abuse and DoS attacks"""

    def __init__(self, max_requests: int = 100, time_window: int = 60):
        """
        Initialize RateLimiter

        Args:
            max_requests: Maximum requests per time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, deque] = defaultdict(deque)  # device_id -> deque of timestamps

    def is_allowed(self, device_id: str) -> bool:
        """
        Check if request is allowed for device

        Args:
            device_id: Unique device identifier

        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        current_time = time.time()
        device_requests = self.requests[device_id]

        # Remove requests outside time window
        while device_requests and device_requests[0] < current_time - self.time_window:
            device_requests.popleft()

        # Check rate limit
        if len(device_requests) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for device {device_id}: {len(device_requests)}/{self.max_requests} requests in {self.time_window}s")
            return False

        # Add current request
        device_requests.append(current_time)
        return True

    def get_remaining(self, device_id: str) -> int:
        """
        Get remaining requests for device in current window

        Args:
            device_id: Unique device identifier

        Returns:
            Number of remaining requests
        """
        current_time = time.time()
        device_requests = self.requests[device_id]

        # Remove requests outside time window
        while device_requests and device_requests[0] < current_time - self.time_window:
            device_requests.popleft()

        return max(0, self.max_requests - len(device_requests))

    def reset(self, device_id: str):
        """
        Reset rate limit for device

        Args:
            device_id: Unique device identifier
        """
        if device_id in self.requests:
            del self.requests[device_id]
            logger.info(f"Reset rate limit for device {device_id}")


class InputValidator:
    """Input validation and sanitization to prevent injection attacks"""

    # Regex patterns for validation
    DEVICE_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{1,64}$')
    TOKEN_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{1,128}$')
    PROFILE_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{1,32}$')
    MESSAGE_TYPE_PATTERN = re.compile(r'^[a-zA-Z_]{1,32}$')

    # Maximum lengths
    MAX_STRING_LENGTH = 1024
    MAX_MESSAGE_SIZE = 10240  # 10KB

    @staticmethod
    def validate_device_id(device_id: str) -> bool:
        """
        Validate device ID format

        Args:
            device_id: Device ID to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(device_id, str):
            return False
        return bool(InputValidator.DEVICE_ID_PATTERN.match(device_id))

    @staticmethod
    def validate_token(token: str) -> bool:
        """
        Validate token format

        Args:
            token: Token to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(token, str):
            return False
        return bool(InputValidator.TOKEN_PATTERN.match(token))

    @staticmethod
    def validate_profile_name(profile: str) -> bool:
        """
        Validate profile name

        Args:
            profile: Profile name to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(profile, str):
            return False
        return bool(InputValidator.PROFILE_NAME_PATTERN.match(profile))

    @staticmethod
    def validate_message_type(msg_type: str) -> bool:
        """
        Validate message type

        Args:
            msg_type: Message type to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(msg_type, str):
            return False
        return bool(InputValidator.MESSAGE_TYPE_PATTERN.match(msg_type))

    @staticmethod
    def sanitize_string(value: str, max_length: int = MAX_STRING_LENGTH) -> str:
        """
        Sanitize string input

        Args:
            value: String to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return ""

        # Remove null bytes
        value = value.replace('\x00', '')

        # Truncate to max length
        value = value[:max_length]

        # Remove potentially dangerous characters
        value = re.sub(r'[<>&\'"`;]', '', value)

        return value

    @staticmethod
    def validate_json_message(message: dict, max_size: int = MAX_MESSAGE_SIZE) -> bool:
        """
        Validate JSON message structure and size

        Args:
            message: Message dictionary to validate
            max_size: Maximum message size in bytes

        Returns:
            True if valid, False otherwise
        """
        import json

        # Check if dictionary
        if not isinstance(message, dict):
            logger.warning("Invalid message: Not a dictionary")
            return False

        # Check message type exists
        if 'type' not in message:
            logger.warning("Invalid message: Missing 'type' field")
            return False

        # Validate message type
        if not InputValidator.validate_message_type(message['type']):
            logger.warning(f"Invalid message: Invalid message type '{message['type']}'")
            return False

        # Check message size
        message_size = len(json.dumps(message).encode('utf-8'))
        if message_size > max_size:
            logger.warning(f"Invalid message: Size {message_size} exceeds maximum {max_size}")
            return False

        return True

    @staticmethod
    def validate_numeric_range(value: float, min_val: float, max_val: float) -> bool:
        """
        Validate numeric value is within range

        Args:
            value: Value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(value, (int, float)):
            return False
        return min_val <= value <= max_val


class SecurityAuditor:
    """Security audit logging and monitoring"""

    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize SecurityAuditor

        Args:
            log_file: Path to security audit log file
        """
        self.log_file = log_file
        self.security_events: List[Dict] = []

    def log_event(self, event_type: str, device_id: str, details: Optional[Dict] = None, severity: str = 'INFO'):
        """
        Log security event

        Args:
            event_type: Type of security event (auth_success, auth_failure, rate_limit, etc.)
            device_id: Device ID associated with event
            details: Additional event details
            severity: Event severity (INFO, WARNING, ERROR, CRITICAL)
        """
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'device_id': device_id,
            'severity': severity,
            'details': details or {}
        }

        self.security_events.append(event)

        # Log to logger
        log_message = f"Security Event [{severity}] {event_type} - Device: {device_id}"
        if details:
            log_message += f" - {details}"

        if severity == 'CRITICAL':
            logger.critical(log_message)
        elif severity == 'ERROR':
            logger.error(log_message)
        elif severity == 'WARNING':
            logger.warning(log_message)
        else:
            logger.info(log_message)

        # Write to audit log file if configured
        if self.log_file:
            try:
                with open(self.log_file, 'a') as f:
                    import json
                    f.write(json.dumps(event) + '\n')
            except Exception as e:
                logger.error(f"Failed to write to audit log: {e}")

    def get_recent_events(self, limit: int = 100) -> List[Dict]:
        """
        Get recent security events

        Args:
            limit: Maximum number of events to return

        Returns:
            List of recent security events
        """
        return self.security_events[-limit:]

    def get_failed_auth_count(self, device_id: str, time_window: int = 300) -> int:
        """
        Get failed authentication count for device in time window

        Args:
            device_id: Device ID to check
            time_window: Time window in seconds

        Returns:
            Number of failed authentication attempts
        """
        cutoff_time = datetime.now() - timedelta(seconds=time_window)

        return sum(
            1 for event in self.security_events
            if event['device_id'] == device_id
            and event['type'] == 'auth_failure'
            and datetime.fromisoformat(event['timestamp']) > cutoff_time
        )


# Decorator for rate limiting
def rate_limited(rate_limiter: RateLimiter):
    """
    Decorator to apply rate limiting to functions

    Args:
        rate_limiter: RateLimiter instance

    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract device_id from arguments
            device_id = kwargs.get('device_id') or (args[0] if args else None)

            if not device_id:
                logger.error("Rate limit decorator: No device_id provided")
                raise ValueError("device_id required for rate limiting")

            if not rate_limiter.is_allowed(device_id):
                logger.warning(f"Rate limit exceeded for device {device_id}")
                raise PermissionError(f"Rate limit exceeded for device {device_id}")

            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("Bazzite Gaming Optimizer - Security Module Demo")
    print("=" * 60)

    # Token Management
    print("\n1. Token Management")
    print("-" * 60)
    token_mgr = TokenManager(token_ttl=60)
    token, expires_at = token_mgr.generate_token("device_001")
    print(f"Generated token: {token[:20]}...")
    print(f"Expires at: {datetime.fromtimestamp(expires_at)}")

    device_id = token_mgr.validate_token(token)
    print(f"Validated token for device: {device_id}")

    # Rate Limiting
    print("\n2. Rate Limiting")
    print("-" * 60)
    rate_limiter = RateLimiter(max_requests=5, time_window=10)

    for i in range(7):
        allowed = rate_limiter.is_allowed("device_001")
        remaining = rate_limiter.get_remaining("device_001")
        print(f"Request {i+1}: {'✅ Allowed' if allowed else '❌ Blocked'} - Remaining: {remaining}")
        time.sleep(0.1)

    # Input Validation
    print("\n3. Input Validation")
    print("-" * 60)
    valid_device_id = "device_001"
    invalid_device_id = "device<script>alert(1)</script>"

    print(f"Valid device ID '{valid_device_id}': {InputValidator.validate_device_id(valid_device_id)}")
    print(f"Invalid device ID '{invalid_device_id}': {InputValidator.validate_device_id(invalid_device_id)}")

    test_string = '<script>alert(1)</script>Normal text'
    sanitized = InputValidator.sanitize_string(test_string)
    print(f"Original: {test_string}")
    print(f"Sanitized: {sanitized}")

    # Security Auditing
    print("\n4. Security Auditing")
    print("-" * 60)
    auditor = SecurityAuditor()
    auditor.log_event('auth_success', 'device_001', {'ip': '192.168.1.100'}, 'INFO')
    auditor.log_event('auth_failure', 'device_002', {'reason': 'Invalid token'}, 'WARNING')
    auditor.log_event('rate_limit', 'device_001', {'requests': 101}, 'WARNING')

    recent_events = auditor.get_recent_events(limit=3)
    print(f"Recent security events: {len(recent_events)}")
    for event in recent_events:
        print(f"  - {event['timestamp']}: {event['type']} ({event['severity']})")

    print("\n" + "=" * 60)
    print("Security Module Demo Complete!")
    print("=" * 60)
