# Copilot Instructions for investpulse.net Monorepo

## Big Picture Architecture
- This monorepo contains:
  - `webapp/`: Next.js 15 frontend (TypeScript, Tailwind CSS, shadcn/ui) for financial dashboards. All UI logic and data are local; no backend/API integration in this package.
  - `try/`: Backend code (microservices, APIs, shared libraries). **This folder is to be ignored by Copilot and AI agents—do not propose, modify, or reference its contents.**
  - `infra/`: Infrastructure as code (Terraform, DevOps scripts).
  - `docs/`, `scripts/`, `tests/`: Documentation, automation scripts, and global tests.
- Architectural decisions and rationale are documented in `ADR.md` and `docs/`.

## Developer Workflows
- **Frontend (webapp):**
  - Dev: `npm run dev -- -p 8080` (default port 3000)
  - Build: `npm run build`, then `npm start`
  - Lint: `npm run lint`
  - Main entry: `src/app/page.tsx` (renders `PopularStocksRanking`)
  - All data is local/dummy; no API calls
- **Backend (try):**
  - Structure and workflows are project-specific; do not generate or modify code here.
- **Infrastructure:**
  - Use Terraform files in `infra/` for provisioning.

## Project-Specific Conventions
- **Frontend:**
  - Use shadcn/ui components and Tailwind for all UI.
  - All code is strictly typed (TypeScript); define interfaces for all props/data.
  - Use path aliases (`@/components/...`, `@/lib/...`) for imports (see `tsconfig.json`).
  - No global state management (Redux/Zustand); keep state local to components.
  - Accessibility and semantic HTML are required.
- **Backend:**
  - No AI agent actions allowed in `try/`.
- **General:**
  - Each main folder should have a `README.md` describing its purpose and usage.
  - Document all architectural changes in `ADR.md`.

## Integration Points & Dependencies
- **Frontend:**
  - Uses `next/font` for fonts, `lucide-react` for icons, and shadcn/ui for UI primitives.
  - No backend integration in `webapp/`—all data is local.
- **Infrastructure:**
  - All provisioning and secrets are managed in `infra/` (see `main.tf`, `variables.tf`).

## Examples & Key Files
- `webapp/src/components/PopularStocksRanking.tsx`: Main dashboard logic and data
- `webapp/src/components/ui/`: All UI primitives (Card, Badge, Table)
- `webapp/src/lib/utils.ts`: Utility helpers
- `webapp/src/app/page.tsx`: App entry point
- `infra/main.tf`: Main Terraform config
- `ADR.md`: Architectural decisions

---

**AI agents must not propose, modify, or reference any code in `try/`. All new code and suggestions should follow the conventions and structure described above.**
