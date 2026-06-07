# Frontend Design Notes

## Positioning

- Narrative role: engineering demo workbench, not a marketing landing page.
- Viewing distance: laptop screen and interview room projector.
- Visual temperature: calm, precise, lightly premium.
- Capacity check: dense enough to show real workflow; summary, evidence, cases, and recommendations remain visible without excessive scrolling.

## Design Decisions

- Color palette: cool professional teal, graphite neutrals, restrained amber for attention.
- Typography: native Segoe UI / Apple-like UI stack for offline reliability; monospace for logs.
- Spacing system: 8px base, with 14/18/20px operational spacing.
- Border-radius strategy: 14px controls, 22px glass panels; no nested decorative cards.
- Shadow hierarchy: one soft ambient shadow for panels, no heavy elevation stacks.
- Motion style: short 160ms hover/active transitions, disabled under reduced-motion.

## Compatibility

- `file://frontend/index.html`: runs with bundled static samples and a browser-side fallback analyzer.
- `http://127.0.0.1:8000`: served by FastAPI, auto-detects `/health` and `/config`.
- LLM mode: front end sends `use_llm=true`; backend calls qwen3-max only if `.env` or environment contains an API key.
