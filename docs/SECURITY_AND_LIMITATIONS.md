# Security, Governance and Limitations

## Intended use

This repository is a hackathon/reference implementation. It is not a production credit decision system and the included thresholds/weights are illustrative only.

## Data privacy

- Use synthetic data for demos and public/free-tier LLM testing.
- Do not send real tax, credit, identity, bank-statement, or collateral data to an external LLM without approved bank/vendor agreements and privacy/security controls.
- `.env`, local databases, uploads and logs are excluded from Git by default.

## Authentication / authorization

The demo accepts an `X-User-ID` header for underwriter actions; this is not production authentication. A real deployment requires enterprise identity, role-based access control, authorization on every application/document, and strong session/token handling.

## File security

The demo validates file extension/size and sanitizes filenames, but production systems should also perform malware scanning, MIME/magic-byte validation, quarantine, secure object storage, document encryption, and content-disarm/reconstruction where required.

## Prompt injection

Uploaded documents are untrusted input. The LLM is constrained to document understanding and cannot directly alter deterministic risk/policy calculations. Production hardening should add explicit prompt-injection detection, stronger schema enforcement, model/tool isolation, and red-team tests.

## Model governance

- LLM outputs are not authoritative lending decisions.
- Risk weights and credit policies must be approved/versioned by the institution.
- A real ML probability-of-default model requires legitimate historical labels, validation and model-risk governance; this repository does not fabricate such a model.
- Human review remains mandatory for consequential decisions in this demo.

## Financial formula limitation

The hackathon DSCR uses an explicitly documented EBITDA/cash-flow proxy. A bank must replace it with its approved product/jurisdiction-specific definition before real use.

## Database / infrastructure

The local path automatically creates SQLAlchemy tables and does not use Alembic migrations. Production deployment should add migrations, backups, encryption, secret management, monitoring, retention controls, rate limiting and HA architecture.
