# Dokumentacja struktury monorepo

## Cel

Celem tej dokumentacji jest opisanie zalecanej struktury folderów dla monorepo, które zawiera zarówno backend, frontend, jak i infrastrukturę. Struktura ta pozwala na łatwe zarządzanie kodem przez GitHub Copilot oraz inne narzędzia automatyzujące rozwój.

## Główne katalogi

- `webapp/` – kod frontendu (np. Next.js, React, inne frameworki JS/TS)
- `webapi/` – backend (aplikacja FastAPI, REST API)
- `try/` – **Folder ten jest całkowicie ignorowany przez Copilota i nie powinien być modyfikowany ani wykorzystywany przez narzędzia AI.**
- `infra/` – infrastruktura jako kod (np. Terraform, skrypty DevOps)
- `docs/` – dokumentacja techniczna i architektoniczna
- `scripts/` – skrypty pomocnicze do automatyzacji zadań
- `tests/` – testy end-to-end, integracyjne, wspólne dla całego repozytorium

## Przykładowa struktura

```
/ (root)
│
├── webapp/           # Frontend (Next.js, React, itp.)
│   └── ...
│
├── infra/            # Infrastruktura jako kod (Terraform, Ansible, itp.)
│   └── ...
│
├── docs/             # Dokumentacja
│   └── ...
│
├── scripts/          # Skrypty automatyzujące
│   └── ...
│
├── tests/            # Testy wspólne
│   └── ...
│
├── README.md         # Główny opis repozytorium
└── ADR.md            # Decyzje architektoniczne
```



