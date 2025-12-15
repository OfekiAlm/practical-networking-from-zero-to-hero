# Security Model

This document details the security architecture and controls implemented in the Networking Demo Platform.

## Threat Model

### Assets to Protect
- **Host System**: Prevent unauthorized access or damage to the host system
- **User Data**: Protect any user input from being exploited
- **System Resources**: Prevent resource exhaustion attacks
- **Network**: Prevent unauthorized network access from demo containers

### Threat Actors
- **Malicious Users**: Attempting to execute arbitrary code or exploit vulnerabilities
- **Accidental Misuse**: Users providing invalid or dangerous inputs unintentionally
- **Resource Abuse**: Users or automated systems attempting DoS attacks

## Defense in Depth

We implement multiple layers of security controls. Even if one layer fails, others provide protection.

### Layer 1: Input Validation (API Level)

**Control**: Strong input validation using Pydantic schemas

**What it prevents**:
- SQL injection (no database, but principle applies)
- Command injection
- Path traversal
- Buffer overflow attempts
- Type confusion attacks

**Implementation**:
```python
class TCPHandshakeParams(BaseModel):
    target_ip: str = Field(..., regex=r"^(\d{1,3}\.){3}\d{1,3}$")
    target_port: int = Field(..., ge=1, le=65535)
    
    @field_validator("target_ip")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        # Validate each octet
        # Block private/reserved ranges
        # Only allow specific IP ranges (optional)
```

**Examples Blocked**:
- `target_ip: "8.8.8.8; rm -rf /"`
- `target_ip: "../../../etc/passwd"`
- `target_port: 99999`
- `target_port: "'; DROP TABLE users; --"`

### Layer 2: Demo Registry (Application Level)

**Control**: Whitelist of allowed demos

**What it prevents**:
- Arbitrary code execution
- Dynamic imports of malicious code
- eval() or exec() abuse

**Implementation**:
- Only registered demos can be executed
- Demo code is reviewed and static
- No user-supplied code paths
- No eval(), exec(), or __import__()

**Examples Blocked**:
- User cannot provide their own Python code
- User cannot specify which module to import
- User cannot modify demo logic
- Parameters are data only, never code

### Layer 3: Container Isolation (Container Level)

**Control**: Docker containers with strict security constraints

**What it prevents**:
- Host system access
- Privilege escalation
- Filesystem manipulation
- Container escape

**Implementation**:
```yaml
# Non-root user
USER demouser (UID 1000)

# Capabilities
cap_drop: ALL  # Drop all Linux capabilities

# Filesystem
read_only: true  # Root filesystem is read-only
tmpfs: /tmp (rw, noexec, nosuid, size=100m)  # Limited writable space

# Security options
security_opt:
  - no-new-privileges:true  # Cannot gain privileges

# Network
network_mode: none  # No network access by default
```

**Examples Blocked**:
- Container cannot access host files
- Container cannot bind to host network
- Container cannot execute setuid binaries
- Container cannot load kernel modules
- Container cannot mount filesystems

### Layer 4: Resource Limits (System Level)

**Control**: Hard limits on container resources

**What it prevents**:
- CPU exhaustion attacks
- Memory exhaustion (OOM)
- Fork bombs
- Infinite loops consuming resources

**Implementation**:
```yaml
cpus: '1.0'              # Max 1 CPU core
mem_limit: 512m          # Max 512MB RAM
mem_swap: 512m           # No additional swap
pids_limit: 100          # Max 100 processes
timeout: 30-60s          # Hard execution timeout
```

**Examples Blocked**:
```python
# Fork bomb - blocked by pids_limit
while True:
    os.fork()

# Memory exhaustion - blocked by mem_limit
data = []
while True:
    data.append("X" * 10**6)

# Infinite loop - blocked by timeout
while True:
    pass
```

### Layer 5: Monitoring and Logging (Operational Level)

**Control**: Comprehensive logging and monitoring

**What it provides**:
- Audit trail of all requests
- Detection of anomalous behavior
- Forensic analysis capability
- Performance monitoring

**Implementation**:
- All API requests logged with user context
- Job execution logged with parameters
- Failed attempts logged with reason
- Resource usage tracked per job
- Structured JSON logging for analysis

## Specific Attack Mitigations

### 1. Remote Code Execution (RCE)

**Attack**: User attempts to execute arbitrary code

**Prevention**:
- No eval() or exec() in codebase
- No dynamic imports based on user input
- Only predefined demos execute
- Parameters validated as data, not code
- Container isolation prevents system access

**Example Attack Attempt**:
```json
{
  "demo_id": "tcp-handshake",
  "parameters": {
    "target_ip": "8.8.8.8; __import__('os').system('rm -rf /')"
  }
}
```
**Result**: Rejected by IP address validator before execution

### 2. Container Escape

**Attack**: User attempts to break out of container to access host

**Prevention**:
- Non-root user (UID 1000)
- All capabilities dropped
- No new privileges allowed
- Read-only root filesystem
- No access to Docker socket
- No privileged mode

**Example Attack Attempt**:
Container tries to access `/var/run/docker.sock` or `/proc/1/root`

**Result**: Permission denied, file not accessible

### 3. Denial of Service (DoS)

**Attack**: User attempts to exhaust system resources

**Prevention**:
- CPU limits per container
- Memory limits per container
- Process count limits
- Execution timeouts
- Rate limiting (TODO: implement at API level)

**Example Attack Attempt**:
```python
# User submits job with intention to run:
while True:
    [x**2 for x in range(10**8)]
```
**Result**: Stopped after 30-60s timeout, CPU limited to 1 core

### 4. Data Exfiltration

**Attack**: User attempts to send sensitive data to external server

**Prevention**:
- Network disabled in containers (for non-network demos)
- No outbound network access by default
- Read-only filesystem prevents reading sensitive files
- Container has no access to host filesystem

**Example Attack Attempt**:
```python
# User hopes demo can read:
with open('/etc/shadow', 'r') as f:
    send_to_attacker_server(f.read())
```
**Result**: File not accessible (not in container), network blocked

### 5. SSRF (Server-Side Request Forgery)

**Attack**: User attempts to access internal services

**Prevention**:
- IP address validation blocks private ranges (optional)
- Network isolation in containers
- No access to internal networks
- Explicit validation of target IPs

**Example Attack Attempt**:
```json
{
  "demo_id": "tcp-handshake",
  "parameters": {
    "target_ip": "169.254.169.254"  // AWS metadata service
  }
}
```
**Result**: Can be blocked by IP validator if configured

### 6. Path Traversal

**Attack**: User attempts to access files outside allowed directories

**Prevention**:
- No file path parameters accepted
- Container has isolated filesystem
- Read-only root filesystem
- Limited writable /tmp

**Example Attack Attempt**:
```json
{
  "parameters": {
    "output_file": "../../../etc/passwd"
  }
}
```
**Result**: No file path parameters accepted by any demo

### 7. XML/JSON Injection

**Attack**: User attempts to inject malicious payloads in data

**Prevention**:
- Strict JSON parsing
- Pydantic validates all fields
- Type checking enforced
- No reflection or dynamic parsing

**Example Attack Attempt**:
```json
{
  "parameters": {
    "target_port": {"__class__": {"__init__": {"__globals__": ...}}}
  }
}
```
**Result**: Rejected by Pydantic type validator (expects int)

## Security Checklist

### Before Deployment

- [ ] Review all demo code for security issues
- [ ] Ensure no eval(), exec(), or __import__() in code
- [ ] Verify all parameters have validation
- [ ] Test container isolation works
- [ ] Verify resource limits are enforced
- [ ] Test execution timeouts work
- [ ] Ensure logging captures security events
- [ ] Review Docker security settings
- [ ] Test with malicious inputs
- [ ] Run security scanner (e.g., bandit, safety)

### For Each New Demo

- [ ] Review demo code for security issues
- [ ] Define strict parameter schema
- [ ] Add custom validators if needed
- [ ] Test with invalid inputs
- [ ] Verify demo doesn't access sensitive files
- [ ] Check demo respects resource limits
- [ ] Document any special security considerations
- [ ] Test in isolated container

### Operational Security

- [ ] Monitor logs for suspicious activity
- [ ] Set up alerts for failed authentication (future)
- [ ] Track resource usage patterns
- [ ] Review failed job attempts
- [ ] Keep dependencies updated
- [ ] Apply security patches promptly
- [ ] Backup configurations
- [ ] Document incident response procedures

## Known Limitations

1. **Network-Required Demos**: Some demos require network access (e.g., TCP handshake). These containers have network enabled but are still isolated from internal networks.

2. **Privileged Operations**: Some demos require raw socket access (root privileges inside container). The container still runs with user UID 1000 but with CAP_NET_RAW capability for these specific demos.

3. **Resource Limits**: Current limits (1 CPU, 512MB RAM) may be too restrictive or too generous depending on use case. Adjust based on your needs.

4. **Rate Limiting**: Not yet implemented at API level. Should be added before production.

5. **Authentication**: No authentication currently. Should be added for production.

## Reporting Security Issues

If you discover a security vulnerability, please:

1. **Do not** open a public issue
2. Email security concerns to [security contact]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Security Updates

- v1.0.0 (2024-12): Initial security model implemented
  - Multi-layer defense in depth
  - Container isolation
  - Input validation
  - Resource limits

## References

- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [Pydantic Validation](https://docs.pydantic.dev/latest/concepts/validators/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
