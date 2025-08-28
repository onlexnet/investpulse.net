
# Monorepo Structure Documentation

## Purpose

This document describes the recommended folder structure for the monorepo, which includes backend, frontend, and infrastructure. This structure enables easy code management by GitHub Copilot and other automation tools.

## Main directories

- `webapp/` – frontend code (e.g. Next.js, React, other JS/TS frameworks)
- `webapi/` – backend (FastAPI application, REST API)
- `try/` – **This folder is completely ignored by Copilot and should not be modified or used by AI tools.**
- `infra/` – infrastructure as code (e.g. Terraform, DevOps scripts)
- `docs/` – technical and architectural documentation
- `scripts/` – helper scripts for automation
- `tests/` – end-to-end, integration, and shared tests for the whole repository

## Example structure

```
/ (root)
│
├── webapp/           # Frontend (Next.js, React, etc.)
│   └── ...
│
├── infra/            # Infrastructure as code (Terraform, Ansible, etc.)
│   └── ...
│
├── docs/             # Documentation
│   └── ...
│
├── scripts/          # Automation scripts
│   └── ...
│
├── tests/            # Shared tests
│   └── ...
│
├── README.md         # Main repository description
└── ADR.md            # Architectural decisions
```



