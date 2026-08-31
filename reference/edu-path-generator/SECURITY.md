# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in AI Learning Path Generator, please report it responsibly. **Do not open a public GitHub issue for security vulnerabilities.**

### How to Report

Email us at **hello@enterprisedna.co** with:

1. A description of the vulnerability
2. Steps to reproduce the issue
3. The potential impact
4. Any suggested fixes (optional)

### What to Expect

- **Acknowledgment** within 48 hours of your report
- **Status update** within 7 days with our assessment
- **Resolution timeline** communicated once we've triaged the issue
- **Credit** in the release notes (unless you prefer to remain anonymous)

### Scope

The following are in scope:

- Authentication and authorization bypasses
- Token or credential exposure
- SQL injection or other injection attacks
- Cross-site scripting (XSS) or cross-site request forgery (CSRF)
- Sensitive data exposure in API responses
- Insecure default configurations
- Prompt injection leading to privilege escalation or data leakage

### Out of Scope

- Vulnerabilities in third-party dependencies (report these upstream)
- Issues requiring physical access to a user's device
- Social engineering attacks
- Denial of service attacks

## Security Best Practices for Self-Hosters

- Never commit `.env` or any file containing secrets to version control
- Store the OpenAI API key and Replicate API token in Supabase secrets, not in `.env` or the frontend
- Enable Row Level Security (RLS) on every user-facing Supabase table
- Keep dependencies updated with `npm audit` and `npm update`
- Use HTTPS in production (required for Supabase Auth)
- Configure Supabase Auth redirect URLs to your actual domain, not wildcards
- Rotate the Supabase anon key if you believe it's been exposed

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest  | Yes       |
| Older   | No        |

We only provide security fixes for the latest release.
