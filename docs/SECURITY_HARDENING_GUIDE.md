# Bazzite Gaming Optimizer - Security Hardening Guide

Comprehensive security hardening guide covering authentication, rate limiting, input validation, and production security best practices.

## Table of Contents

- [Overview](#overview)
- [Security Architecture](#security-architecture)
- [Authentication System](#authentication-system)
- [Rate Limiting](#rate-limiting)
- [Input Validation](#input-validation)
- [Security Auditing](#security-auditing)
- [Production Deployment](#production-deployment)
- [Security Checklist](#security-checklist)

---

## Overview

The Bazzite Gaming Optimizer implements enterprise-grade security measures:

- **Token-Based Authentication**: Secure device pairing with time-limited tokens
- **Rate Limiting**: Prevention of DoS attacks and abuse
- **Input Validation**: Protection against injection attacks
- **Security Auditing**: Comprehensive logging of security events
- **TLS/SSL Support**: Encrypted communication for production

**Security Principles**:
- Defense in depth
- Least privilege
- Fail securely
- Complete mediation
- Audit all actions

---

## Security Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│                   Mobile Client                         │
│  (Authentication Token + TLS/SSL Certificate Pinning)   │
└────────────────────┬────────────────────────────────────┘
                     │ WSS (TLS/SSL)
                     ↓
┌─────────────────────────────────────────────────────────┐
│              WebSocket Server (FastAPI)                 │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │            Security Middleware                   │  │
│  │  - Rate Limiter (100 req/min per device)        │  │
│  │  - Token Validator (300s TTL)                   │  │
│  │  - Input Validator (Regex + Sanitization)       │  │
│  │  - Security Auditor (Event Logging)             │  │
│  └──────────────────────────────────────────────────┘  │
│                      ↓                                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Connection Manager                       │  │
│  │  - Active Connections Map                        │  │
│  │  - Device Session Management                     │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│              Bazzite Gaming System                      │
│  (System Metrics + Profile Management)                  │
└─────────────────────────────────────────────────────────┘
```

### Security Layers

1. **Network Layer**: TLS/SSL encryption
2. **Authentication Layer**: Token validation
3. **Rate Limiting Layer**: Request throttling
4. **Validation Layer**: Input sanitization
5. **Audit Layer**: Security event logging
6. **Application Layer**: Business logic

---

## Authentication System

### Token Management

**TokenManager** provides secure authentication tokens with automatic expiration.

#### Generating Authentication Tokens

```python
from mobile_api.security import TokenManager

# Initialize token manager
token_mgr = TokenManager(
    secret_key="your-secret-key-here",  # Keep secret!
    token_ttl=300  # 5 minutes
)

# Generate token for device
device_id = "mobile_device_001"
token, expires_at = token_mgr.generate_token(
    device_id=device_id,
    metadata={
        'device_type': 'android',
        'device_name': 'User Phone',
        'ip_address': '192.168.1.100'
    }
)

print(f"Token: {token}")
print(f"Expires: {datetime.fromtimestamp(expires_at)}")
```

#### Validating Tokens

```python
# Client sends token with WebSocket connection
device_id = token_mgr.validate_token(token)

if device_id:
    print(f"✅ Valid token for device: {device_id}")
    # Allow connection
else:
    print("❌ Invalid or expired token")
    # Reject connection
```

#### Token Lifecycle

```python
# Revoke token (e.g., on logout)
token_mgr.revoke_token(token)

# Cleanup expired tokens (run periodically)
token_mgr.cleanup_expired_tokens()
```

### QR Code Pairing

**Secure device pairing workflow**:

1. **Server generates pairing code**:
```python
from mobile_api.websocket_server import MobileWebSocketServer

server = MobileWebSocketServer()
pairing_data = server._generate_pairing_token()

# Display QR code on screen
print(pairing_data['qr_code_ascii'])
```

2. **Mobile app scans QR code**:
   - QR contains: server URL + authentication token
   - Token valid for 300 seconds (5 minutes)

3. **App connects with token**:
```typescript
// Mobile app (TypeScript)
const pairingData = JSON.parse(qrCodeData);
const ws = new WebSocket(`${pairingData.server_url}?token=${pairingData.token}`);
```

4. **Server validates token**:
   - Check token exists
   - Check token not expired
   - Create authenticated session

### Best Practices

✅ **DO**:
- Generate unique tokens per device
- Use cryptographically secure random tokens (`secrets.token_urlsafe()`)
- Set reasonable token expiration (5-15 minutes for pairing, longer for sessions)
- Rotate secret keys periodically (monthly)
- Store tokens in memory, not database (for short-lived tokens)

❌ **DON'T**:
- Use predictable tokens (UUIDs are not cryptographically secure)
- Hardcode secret keys in source code
- Allow unlimited token lifetime
- Reuse tokens across devices
- Log tokens in plain text

---

## Rate Limiting

### RateLimiter Configuration

**Prevent abuse and DoS attacks** with request throttling:

```python
from mobile_api.security import RateLimiter

# Create rate limiter
# 100 requests per 60 seconds per device
rate_limiter = RateLimiter(
    max_requests=100,
    time_window=60
)

# Check if request allowed
device_id = "mobile_device_001"
if rate_limiter.is_allowed(device_id):
    # Process request
    handle_request()
else:
    # Reject with 429 Too Many Requests
    return {"error": "Rate limit exceeded"}

# Check remaining quota
remaining = rate_limiter.get_remaining(device_id)
print(f"Remaining requests: {remaining}")
```

### Decorator-Based Rate Limiting

```python
from mobile_api.security import rate_limited

# Apply rate limiting to async functions
@rate_limited(rate_limiter)
async def handle_websocket_message(device_id: str, message: dict):
    # This function is automatically rate-limited
    process_message(message)
```

### Rate Limit Strategies

**Different limits for different operations**:

```python
# Strict limit for authentication attempts
auth_limiter = RateLimiter(max_requests=5, time_window=60)

# Moderate limit for profile changes
profile_limiter = RateLimiter(max_requests=20, time_window=60)

# Lenient limit for metrics reading
metrics_limiter = RateLimiter(max_requests=100, time_window=60)
```

### Handling Rate Limit Errors

**Client-side handling**:

```typescript
// Mobile app
try {
  await sendRequest();
} catch (error) {
  if (error.code === 429) {
    // Rate limit exceeded
    const retryAfter = error.headers['Retry-After'] || 60;
    console.log(`Rate limited. Retry after ${retryAfter}s`);

    // Show user-friendly message
    showNotification(`Too many requests. Please wait ${retryAfter}s`);

    // Implement exponential backoff
    await sleep(retryAfter * 1000);
    await sendRequest();  // Retry
  }
}
```

**Server-side response**:

```python
from fastapi import HTTPException

if not rate_limiter.is_allowed(device_id):
    raise HTTPException(
        status_code=429,
        detail="Rate limit exceeded",
        headers={"Retry-After": "60"}
    )
```

---

## Input Validation

### InputValidator

**Prevent injection attacks** with comprehensive input validation:

```python
from mobile_api.security import InputValidator

# Validate device ID
device_id = "device_001"
if InputValidator.validate_device_id(device_id):
    print("✅ Valid device ID")
else:
    print("❌ Invalid device ID")

# Validate token
token = "abc123_secure_token"
if InputValidator.validate_token(token):
    print("✅ Valid token format")
else:
    print("❌ Invalid token format")

# Validate profile name
profile = "competitive"
if InputValidator.validate_profile_name(profile):
    print("✅ Valid profile name")
else:
    print("❌ Invalid profile name")
```

### String Sanitization

**Remove potentially dangerous characters**:

```python
# User input (potentially malicious)
user_input = '<script>alert("XSS")</script>Valid text'

# Sanitize
safe_input = InputValidator.sanitize_string(user_input)
print(f"Sanitized: {safe_input}")
# Output: "Valid text"
```

### JSON Message Validation

**Validate WebSocket messages**:

```python
# Received message
message = {
    "type": "apply_profile",
    "data": {
        "profile": "competitive"
    }
}

# Validate
if InputValidator.validate_json_message(message, max_size=10240):
    msg_type = message['type']
    profile = message['data']['profile']

    # Additional validation
    if InputValidator.validate_message_type(msg_type):
        if InputValidator.validate_profile_name(profile):
            # Process message
            apply_profile(profile)
        else:
            logger.warning(f"Invalid profile name: {profile}")
    else:
        logger.warning(f"Invalid message type: {msg_type}")
else:
    logger.error("Invalid message structure or size")
```

### Numeric Range Validation

**Validate numeric inputs**:

```python
# User-provided FPS target
fps_target = 144

if InputValidator.validate_numeric_range(fps_target, min_val=30, max_val=300):
    set_fps_target(fps_target)
else:
    logger.error(f"Invalid FPS target: {fps_target} (must be 30-300)")
```

### Validation Patterns

**Regex patterns used**:

- **Device ID**: `^[a-zA-Z0-9_-]{1,64}$` (alphanumeric, underscore, hyphen)
- **Token**: `^[a-zA-Z0-9_-]{1,128}$` (URL-safe characters)
- **Profile Name**: `^[a-zA-Z0-9_-]{1,32}$` (alphanumeric, limited length)
- **Message Type**: `^[a-zA-Z_]{1,32}$` (letters and underscore only)

### Custom Validation Rules

```python
class CustomValidator:
    @staticmethod
    def validate_game_name(game_name: str) -> bool:
        """Validate game name format"""
        # Allow alphanumeric, spaces, common punctuation
        pattern = re.compile(r'^[a-zA-Z0-9\s\'\-:\.]{1,100}$')
        return bool(pattern.match(game_name))

    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """Validate IPv4 address"""
        pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
        if not pattern.match(ip):
            return False

        # Validate each octet
        octets = ip.split('.')
        return all(0 <= int(octet) <= 255 for octet in octets)
```

---

## Security Auditing

### SecurityAuditor

**Comprehensive security event logging**:

```python
from mobile_api.security import SecurityAuditor

# Initialize auditor
auditor = SecurityAuditor(log_file='/var/log/bazzite-optimizer-security.log')

# Log authentication success
auditor.log_event(
    event_type='auth_success',
    device_id='mobile_device_001',
    details={'ip': '192.168.1.100', 'device_type': 'android'},
    severity='INFO'
)

# Log authentication failure
auditor.log_event(
    event_type='auth_failure',
    device_id='mobile_device_002',
    details={'reason': 'Invalid token', 'ip': '192.168.1.200'},
    severity='WARNING'
)

# Log rate limit violation
auditor.log_event(
    event_type='rate_limit_exceeded',
    device_id='mobile_device_001',
    details={'requests': 101, 'limit': 100},
    severity='WARNING'
)

# Log suspicious activity
auditor.log_event(
    event_type='suspicious_activity',
    device_id='mobile_device_003',
    details={'reason': 'SQL injection attempt', 'input': 'DROP TABLE users;'},
    severity='CRITICAL'
)
```

### Viewing Security Events

```python
# Get recent events
recent_events = auditor.get_recent_events(limit=100)

for event in recent_events:
    print(f"{event['timestamp']} [{event['severity']}] {event['type']}")
    print(f"  Device: {event['device_id']}")
    print(f"  Details: {event['details']}")

# Get failed authentication count
failed_count = auditor.get_failed_auth_count(
    device_id='mobile_device_002',
    time_window=300  # Last 5 minutes
)

if failed_count >= 5:
    print(f"⚠️  Possible brute force attack: {failed_count} failures")
    # Block device temporarily
```

### Audit Log Format

**JSON Lines format** for easy parsing:

```json
{"timestamp": "2025-11-19T10:30:45.123456", "type": "auth_success", "device_id": "device_001", "severity": "INFO", "details": {"ip": "192.168.1.100"}}
{"timestamp": "2025-11-19T10:31:12.654321", "type": "auth_failure", "device_id": "device_002", "severity": "WARNING", "details": {"reason": "Invalid token"}}
{"timestamp": "2025-11-19T10:32:34.987654", "type": "rate_limit_exceeded", "device_id": "device_001", "severity": "WARNING", "details": {"requests": 101}}
```

### Monitoring and Alerts

**Automated security monitoring**:

```python
import time

def security_monitoring_loop():
    """Continuous security monitoring"""
    while True:
        # Check for brute force attacks
        for device_id in get_active_devices():
            failed_count = auditor.get_failed_auth_count(device_id, time_window=300)

            if failed_count >= 5:
                # Alert administrators
                send_alert(f"Possible brute force on {device_id}: {failed_count} failures")

                # Temporarily block device
                blacklist_device(device_id, duration=3600)  # 1 hour

        # Check for unusual activity patterns
        recent_events = auditor.get_recent_events(limit=1000)
        critical_events = [e for e in recent_events if e['severity'] == 'CRITICAL']

        if len(critical_events) > 10:
            send_critical_alert(f"{len(critical_events)} critical security events")

        time.sleep(60)  # Check every minute
```

---

## Production Deployment

### TLS/SSL Configuration

**Enable encrypted communication**:

```python
# Use WSS (WebSocket Secure) instead of WS
server_url = "wss://bazzite-optimizer.example.com"  # Not ws://

# SSL certificate paths
ssl_cert_path = "/etc/letsencrypt/live/example.com/fullchain.pem"
ssl_key_path = "/etc/letsencrypt/live/example.com/privkey.pem"

# Start server with SSL
import ssl
import uvicorn

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(ssl_cert_path, ssl_key_path)

uvicorn.run(
    app,
    host="0.0.0.0",
    port=8081,
    ssl_keyfile=ssl_key_path,
    ssl_certfile=ssl_cert_path
)
```

### Environment Variables

**Never hardcode secrets**:

```bash
# .env file (DO NOT COMMIT TO GIT)
BAZZITE_SECRET_KEY=your-secret-key-here
BAZZITE_TOKEN_TTL=300
BAZZITE_RATE_LIMIT=100
BAZZITE_RATE_WINDOW=60
BAZZITE_SSL_CERT=/path/to/cert.pem
BAZZITE_SSL_KEY=/path/to/key.pem
```

**Load in application**:

```python
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('BAZZITE_SECRET_KEY')
TOKEN_TTL = int(os.getenv('BAZZITE_TOKEN_TTL', '300'))
RATE_LIMIT = int(os.getenv('BAZZITE_RATE_LIMIT', '100'))
```

### Firewall Configuration

```bash
# Allow only necessary ports
sudo firewall-cmd --permanent --add-port=8081/tcp  # WebSocket
sudo firewall-cmd --permanent --add-port=443/tcp   # HTTPS
sudo firewall-cmd --reload

# Block all other incoming connections
sudo firewall-cmd --set-default-zone=drop
sudo firewall-cmd --zone=drop --add-interface=eth0
```

### Reverse Proxy (Nginx)

**Use Nginx as reverse proxy for additional security**:

```nginx
server {
    listen 443 ssl http2;
    server_name bazzite-optimizer.example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # WebSocket proxy
    location /ws {
        proxy_pass http://127.0.0.1:8081;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # Timeout settings
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
}
```

---

## Security Checklist

### Pre-Deployment Checklist

- [ ] **Authentication**
  - [ ] Token-based authentication implemented
  - [ ] Token expiration configured (≤15 minutes)
  - [ ] Secret key is cryptographically secure (32+ bytes)
  - [ ] Secret key stored securely (environment variable)
  - [ ] Token revocation mechanism in place

- [ ] **Rate Limiting**
  - [ ] Rate limiting enabled for all endpoints
  - [ ] Appropriate limits set (100 req/min recommended)
  - [ ] Rate limit errors handled gracefully
  - [ ] Client implements retry with exponential backoff

- [ ] **Input Validation**
  - [ ] All user input validated and sanitized
  - [ ] Regex patterns prevent injection attacks
  - [ ] Maximum input lengths enforced
  - [ ] JSON message size limits enforced (10KB)
  - [ ] Numeric values range-checked

- [ ] **Security Auditing**
  - [ ] Security event logging enabled
  - [ ] Audit log rotation configured
  - [ ] Critical events trigger alerts
  - [ ] Failed authentication attempts monitored
  - [ ] Suspicious activity detection in place

- [ ] **Network Security**
  - [ ] TLS/SSL enabled (WSS, not WS)
  - [ ] Valid SSL certificate installed
  - [ ] Strong cipher suites configured
  - [ ] HSTS header enabled
  - [ ] Firewall rules configured

- [ ] **Code Security**
  - [ ] No hardcoded secrets in source code
  - [ ] Dependencies up to date
  - [ ] Security scan performed (Bandit, Safety)
  - [ ] Code review completed
  - [ ] Penetration testing performed

### Ongoing Security Maintenance

- [ ] Rotate secret keys monthly
- [ ] Update dependencies quarterly
- [ ] Review audit logs weekly
- [ ] Security scan before each release
- [ ] Monitor for CVEs in dependencies
- [ ] Renew SSL certificates before expiration
- [ ] Review and update rate limits as needed
- [ ] Test disaster recovery procedures

---

**Version**: 1.6.0
**Last Updated**: November 19, 2025
**Author**: Bazzite Gaming Optimizer Security Team
