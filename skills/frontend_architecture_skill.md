# Frontend UI & Architecture Skill

When explicitly instructed to modify or create frontend React code for the DesignBook application, you must adhere strictly to these UX and architectural principles.

## Core Framework
- **React + TypeScript via Vite**.
- Absolutely zero TypeScript or TSX compilation errors are tolerated (`npm run build` MUST pass cleanly without ignoring typing rules).
- State Management: Use **Zustand** specifically (`app/frontend/src/store/`). Create normalized stores for `projectStore`, `analysisStore`, `designStore`, and `uiStore`.
- Remote Data Fetching: Encapsulate API layer calls explicitly inside custom React hooks wrapped by React Query (`@tanstack/react-query`).

## Global UI / UX Design Language
- **Aesthetic Direction**: "Digital Twin Command Center".
- **Primary Theme Elements**:
  - Dark-mode first design natively implemented.
  - Background base: Deep Navy (`#0A0F1E`).
  - Brand Primary: Electric Blue (`#3B82F6`).
  - Functional Accents: Structural Green (`#10B981`) for passing designs, Structural Red (`#EF4444`) for mechanical failures, Amber (`#F59E0B`) for warnings.
- **Micro-animations**: Inject `framer-motion` seamlessly on layout transitions, element mounting, and hover mechanics. Ensure all transitions are silky and under 60fps.
- **Glassmorphism Componentry**: Utilize backdrop filters, semi-transparent layers, and CSS blur (`backdrop-filter: blur(10px); background: rgba(10, 15, 30, 0.7);`) rather than flat opaque cards.

## Component Tooling
- Exclusively leverage **TailwindCSS (v3)** and **Radix UI Primitives** (often via `shadcn/ui` preset).
- Typography: Use **Inter** for body text and headers, and use **JetBrains Mono** strictly for engineering data, loads, matrix outputs, and analytical coordinates.
- Ensure all complex structural geometry mappings are rendered via **Three.js** utilizing `@react-three/fiber` components inside `ThreeViewer`.

## Hard Rules
- Never use CDNs (e.g., FontAwesome, Google Fonts web-links) for icons or fonts. Use module-imported Lucide icons (`lucide-react`) to maintain **offline capability**.
- All user input configurations representing building geometry MUST implement Zod parsing prior to submitting to the API layer, effectively mapping to the backend Pydantic schemas.
