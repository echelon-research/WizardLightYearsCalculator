# Security Documentation

## Implemented Security Measures

### 1. Rate Limiting ✅

**Protection Against:** Denial of Service (DoS) attacks, API abuse

**Implementation:**
- Flask-Limiter middleware
- Default: 60 requests/minute per IP, 1000 requests/hour
- Configurable via environment variables
- Returns 429 status code when exceeded

**Configuration:**
```bash
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

**Response when limit exceeded:**
```json
{
    "error": "Rate limit exceeded. Please try again later.",
    "retry_after": "55 seconds"
}
```

### 2. SQL Injection Prevention ✅

**Protection Against:** SQL injection attacks

**Implementation:**
- All database queries use parameterized statements with `?` placeholders
- No string concatenation for SQL queries
- SQLite's parameter binding automatically escapes values

**Example:**
```python
cursor.execute("""
    SELECT * FROM systems WHERE system_id = ?
""", (system_id,))  # Safe - parameterized
```

**NOT used:**
```python
# UNSAFE - Never do this
cursor.execute(f"SELECT * FROM systems WHERE system_id = {system_id}")
```

### 3. Error Message Sanitization ✅

**Protection Against:** Information disclosure, debugging data exposure

**Implementation:**
- Generic error messages to clients
- Detailed errors logged server-side only
- No stack traces or internal paths exposed
- No database schema information leaked

**Examples:**

| Internal Error | Client Sees | Server Logs |
|---------------|-------------|-------------|
| `System 30000142 not found in ESI` | "One or more system IDs not found" | Full error with system ID |
| `Database connection failed` | "A service error occurred" | Full stack trace |
| `ESI API timeout after 10s` | "Unable to retrieve system information" | Full timeout details |

### 4. Input Validation ✅

**Protection Against:** Invalid data, injection attacks, application crashes

**Implementation:**
- Type checking (integers only for system IDs)
- Range validation (30,000,000 - 31,000,000)
- Validation before any database or API calls
- Clear error messages for invalid input

**Validation Rules:**
```python
- system_id must be an integer
- system_id must be >= 30,000,000
- system_id must be <= 31,000,000
```

### 5. Secure Headers (ESI API) ✅

**Protection Against:** API version conflicts, request identification

**Implementation:**
- `X-Compatibility-Date: 2026-02-02` - Ensures consistent API version
- `user-agent: WizardLightYearsCalculator, Username=Dusty Meg` - Identifies requests

### 6. Logging ✅

**Protection Against:** Unauthorized access, debugging, audit trail

**Implementation:**
- Structured logging with timestamps
- Different log levels (INFO, WARNING, ERROR)
- Rate limit violations logged
- Errors logged with traceback (server-side only)
- No sensitive data in logs

## Security Best Practices

### Database
- ✅ Parameterized queries (SQL injection prevention)
- ✅ Connection pooling and proper cleanup
- ✅ No direct user input in queries
- ⚠️ Database file permissions should be restricted (OS level)

### API
- ✅ Rate limiting enabled
- ✅ Input validation
- ✅ Error message sanitization
- ⚠️ Consider adding authentication for production
- ⚠️ Consider HTTPS/TLS for production
- ⚠️ Consider CORS configuration for web clients

### Configuration
- ✅ Environment variables for sensitive config
- ✅ Debug mode disabled by default
- ✅ Reasonable default limits
- ⚠️ Ensure `.env` file is in `.gitignore`

## Recommendations for Production

### High Priority
1. **HTTPS/TLS** - Use reverse proxy (nginx/Apache) with SSL certificates
2. **Authentication** - Add API key or OAuth for access control
3. **CORS** - Configure allowed origins if serving web clients
4. **Database Backups** - Regular automated backups
5. **Monitoring** - Add application monitoring (errors, performance)

### Medium Priority
6. **Request Size Limits** - Limit request body size
7. **Timeout Configuration** - Configure request timeouts
8. **Security Headers** - Add X-Content-Type-Options, X-Frame-Options, etc.
9. **Audit Logging** - Enhanced logging for security events
10. **WAF** - Consider Web Application Firewall for production

### Low Priority
11. **Content Security Policy** - If serving HTML content
12. **Rate Limit by User** - If authentication is added
13. **IP Whitelisting** - For restricted access scenarios

## Testing Security

### Rate Limit Testing
```bash
# Test rate limit (run quickly)
for i in {1..70}; do
  curl -X POST http://localhost:5000/calculate-distance \
    -H "Content-Type: application/json" \
    -d '{"system_id_1": 30000142, "system_id_2": 30000144}'
done
```

### SQL Injection Testing
The API is protected, but you can verify:
```bash
# These should all fail safely
curl "http://localhost:5000/calculate-distance?system_id_1=30000142'; DROP TABLE systems;--&system_id_2=30000144"
curl "http://localhost:5000/calculate-distance?system_id_1=30000142 OR 1=1&system_id_2=30000144"
```

### Invalid Input Testing
```bash
# Out of range
curl "http://localhost:5000/calculate-distance?system_id_1=99999999&system_id_2=30000144"

# Invalid type
curl "http://localhost:5000/calculate-distance?system_id_1=abc&system_id_2=30000144"
```

## Reporting Security Issues

If you discover a security vulnerability, please:
1. **Do not** open a public issue
2. Contact the maintainer directly
3. Provide detailed reproduction steps
4. Allow time for a fix before public disclosure

## Security Changelog

### 2026-02-20
- ✅ Implemented rate limiting with Flask-Limiter
- ✅ Added error message sanitization
- ✅ Enhanced logging with security context
- ✅ Documented SQL injection prevention
- ✅ Added rate limit error handler
