# Security Policy

## Supported versions

Security fixes are generally targeted at the latest version on the default branch. If you rely on a deployed copy, verify that it includes current fixes.

## Reporting a vulnerability

Please do not publish exploitable vulnerability details in a public issue.

Use GitHub's **Report a vulnerability** feature on this repository, if enabled, to send a private report to the maintainer. Include:
- A concise description and potential impact.
- Steps to reproduce or a minimal proof of concept.
- Affected commit, version, or deployment configuration.
- Any suggested mitigation.

Do not include real user resumes, credentials, access tokens, or other sensitive personal information in a report.

## Response

The maintainer will review the report, assess severity, and coordinate a fix and disclosure. No specific response or remediation time is guaranteed.

## Deployment guidance

- Store provider API keys in environment variables or a secret manager.
- Never commit `.env` files, credentials, or production data.
- Use HTTPS in deployed environments.
- Review rate limits and request-size limits for the expected traffic.
- Replace in-memory rate limiting with a shared mechanism when running multiple instances.
