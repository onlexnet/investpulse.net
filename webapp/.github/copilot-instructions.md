## Copilot Instructions for Predictive Trading Dashboard (webapp)

### Overview
This is a Next.js 15 app (App Router, TypeScript, Tailwind CSS, shadcn/ui) for a financial dashboard visualizing AI-ranked stocks and ETFs, inspired by Danelfin.com.

### Architecture & Structure
- **App Router**: All routing and pages are under `src/app/` (see `layout.tsx`, `page.tsx`).
- **UI Components**: Custom shadcn/ui-based components in `src/components/ui/` (e.g., `card.tsx`, `badge.tsx`, `table.tsx`).
- **Feature Components**: Main dashboard logic in `src/components/PopularStocksRanking.tsx`.
- **Utility Functions**: Shared helpers in `src/lib/utils.ts` (e.g., `cn` for class merging).
- **Styling**: Tailwind CSS with custom theme in `src/app/globals.css`.
- **TypeScript**: All code is strictly typed; interfaces for all props and data.
- **Aliases**: Use `@/` for imports (see `tsconfig.json` and `components.json`).

### Data Flow & Patterns
- **Dummy Data**: Stock/ETF data is hardcoded in `PopularStocksRanking.tsx` for demo purposes.
- **Component Pattern**: UI is composed of small, typed, reusable components (Card, Badge, Table, etc.).
- **Color/Badge Logic**: Helper functions in `PopularStocksRanking.tsx` determine color classes and icons for AI scores, returns, and changes.
- **No API/Backend**: All data is local; no server calls or API integration in this package.

### Developer Workflows
- **Development**: Run with `npm run dev -- -p 8080` (or change port as needed).
- **Production**: Build with `npm run build`, then start with `npm start` (serves on port 3000 by default; use `-p` to change).
- **Linting**: `npm run lint` (uses Next.js and TypeScript ESLint config).
- **Component Editing**: Main entry is `src/app/page.tsx` (renders `PopularStocksRanking`).
- **Live Reload**: All changes in `src/` auto-reload in dev mode.

### Project-Specific Conventions
- **UI Consistency**: Always use shadcn/ui components for new UI elements; style with Tailwind utility classes.
- **Type Safety**: All props and data must be explicitly typed (see interfaces in `PopularStocksRanking.tsx`).
- **Accessibility**: Use semantic HTML and accessible markup in all components.
- **Imports**: Use path aliases (`@/components/...`, `@/lib/...`) instead of relative paths.
- **No Global State**: No Redux, Zustand, or context—keep state local to components.

### Integration Points
- **Fonts**: Uses `next/font` for loading Geist font (see `layout.tsx`).
- **Icons**: Uses `lucide-react` for icons (see `package.json`).
- **shadcn/ui**: All UI primitives are customized via Tailwind and shadcn/ui patterns.

### Examples
- To add a new table: create a component in `src/components/ui/`, use `Table`, `TableRow`, etc., and type all props.
- To add a new data section: extend `PopularStocksRanking.tsx` with new dummy data and a new Card/Table.

### Key Files
- `src/components/PopularStocksRanking.tsx`: Main dashboard logic and data
- `src/components/ui/`: All UI primitives (Card, Badge, Table)
- `src/lib/utils.ts`: Utility helpers (e.g., `cn`)
- `src/app/page.tsx`: App entry point
- `src/app/layout.tsx`: Global layout and font setup
- `src/app/globals.css`: Tailwind and theme config

---
For more, see the README.md and comments in each file. Keep all new code idiomatic to this structure and style.
