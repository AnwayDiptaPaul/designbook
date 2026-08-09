# Meta-Instructions for the AI Assistant

This directory contains foundational knowledge, guidelines, and behavioral algorithms distilled from the master architectural handbook located at `docs/plan.md`. To maintain codebase coherence and strict application stability, always read the appropriate skill file before taking action.

## Triggering Guidelines

- If you receive a request mentioning **UI updates, new React components, colors, themes, animations, or styling**, you must refer to:
  👉 `frontend_architecture_skill.md`
- If you receive a request mentioning **API endpoints, OpenSees integrations, error handling, performance speedups, or Pydantic validation**, you must refer to:
  👉 `backend_engineering_skill.md`
- If you receive a request that involves **calculating forces, resizing columns/beams, BNBC provisions, ACI standards, loads, or seismic mechanics**, you must refer to:
  👉 `structural_domain_skill.md`
- If you receive a request that involves **environment setup, running scripts locally, bash processing, vulnerabilities, offline execution, or fixing zombies**, you must refer to:
  👉 `deployment_and_quality_skill.md`

## AI Execution Philosophy
When interacting with the DesignBook repository:
1. **Locate Context**: Open and read the relevant skill files if you are unsure about the design system standard or coding convention.
2. **Apply Rigorous Typings**: Neither frontend TSX nor backend Python code should ever be emitted that generates structural warnings. You must proactively compile mental checks against Zod/Pydantic/Pyre boundaries.
3. **Respect Project Map**: Familiarize yourself with the system map located in the root `/README.md` to ensure any new code implementations natively bind to the correct architectural slice.
