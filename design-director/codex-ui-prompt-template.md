# Reusable Codex UI Prompt Template

Use this prompt when asking Codex to implement or update Pioneer UI. Fill in the bracketed sections, delete anything irrelevant, and keep the constraints explicit.

```markdown
You are Codex working in `C:\Users\Me\Documents\Pioneet Project`.

Task: [Implement/update/build the specific screen or component.]

Scope:
- Edit only: [list exact files or directories].
- Do not edit: [app code/data/assets/docs outside scope].
- Preserve existing user or teammate changes. Do not revert unrelated work.
- Keep public catalog and Taylor tablet behavior separate.

Product context:
- Pioneer Industrial Sales is a practical industrial supply catalog and quote workflow.
- Phase 1 public catalog includes open browsing, product detail, quote cart, request quote, and service overview.
- Stage 2 Taylor tablet is rep-facing and may use demo customer context, preferred categories, field order notes, substitution preferences, and warehouse handoff preview.
- Future WMS screens focus on pick accuracy, bin/location, exceptions, and fulfillment status.

Design system:
- Use Pioneer tokens from `design-director/design-system-template.md`.
- Primary action/accent: `#4C6444`.
- Dark brand area: `#344530`.
- Main text: `#171914`.
- Secondary background: `#F4F2EC`.
- Panel background: `#FFFFFF`.
- Border: `#D9DDD6`.
- Radius: 8px max for cards and controls unless existing Streamlit style requires otherwise.
- Keep the UI dense, scannable, and service-oriented.

User and goal:
- Primary user: [public buyer | Pioneer sales rep | warehouse associate].
- User goal: [specific job to be done].
- Business goal: [specific Pioneer outcome].

Screen requirements:
- Mode: [public_catalog | taylor_tablet | wms | shared].
- Route/page/entrypoint: [where this appears].
- Required states: [default, empty, loading, error, success].
- Required actions: [list].
- Required data fields: [list exact fields].

Public catalog rules:
- Do not expose demo customers, account-specific pricing, private account notes, quote history, or negotiated terms.
- Use "Request quote" language when final price/availability requires Pioneer confirmation.
- Product browsing must support category scanning, search/filtering, product detail review, and quote cart flow.

Taylor tablet rules:
- Use only for rep-facing mode.
- Touch targets must be at least 44px.
- No hover-only controls.
- Customer context must be clearly tied to the selected demo/approved account.
- Include quantity, line note, substitution preference, and handoff summary when building orders.

WMS rules:
- Prioritize queue status, bin/location, pick quantities, exceptions, and completion confidence.
- Make blocked/exception lines more visible than normal lines.
- Avoid public-buyer language like "shop" or "checkout".

Interaction details:
- Primary CTA: [label and behavior].
- Secondary actions: [labels and behavior].
- Empty state copy: [copy].
- Error copy: [copy].
- Confirmation copy: [copy].

Implementation guidance:
- Follow existing code patterns and Streamlit conventions in this repo.
- Reuse existing modules/components where appropriate.
- Do not introduce new frameworks unless already present or explicitly requested.
- Keep CSS scoped and consistent with existing `modules/styling.py` patterns.
- Use stable dimensions for product image wells, cards, controls, and tables to prevent layout shift.
- Use real existing assets when available; do not depend on remote images unless the current data already does.

Accessibility:
- Ensure keyboard navigation.
- Ensure visible focus states.
- Add meaningful labels and alt text.
- Do not rely on color alone for status.
- Check mobile/tablet/desktop text wrapping for critical controls and product facts.

Verification:
- Run the relevant local checks: [for example, `python -m compileall .` or app-specific test command].
- If the app needs visual verification, start Streamlit and inspect the changed screen.
- Report changed paths and any checks that could not be run.

Deliverable:
- Implement the requested change.
- Summarize what changed in plain language.
- List changed paths.
- Mention verification results.
```

## Prompt Fill Checklist

- [ ] The mode is clearly named.
- [ ] Edit scope is exact.
- [ ] Public vs tablet vs WMS privacy boundaries are stated.
- [ ] Required data fields are listed.
- [ ] Empty, error, and success states are included.
- [ ] Accessibility requirements are included.
- [ ] Verification expectations are included.

## Short Variant

Use this when the requested change is narrow.

```markdown
You are Codex in `C:\Users\Me\Documents\Pioneet Project`.

Build [specific UI change] for Pioneer Industrial Sales.

Edit only [files]. Do not edit app code outside that scope or revert unrelated changes.

Use Pioneer defaults: primary `#4C6444`, dark brand `#344530`, text `#171914`, neutral band `#F4F2EC`, panel `#FFFFFF`, border `#D9DDD6`, 8px radius, practical industrial tone.

Mode: [public_catalog | taylor_tablet | wms | shared].

Must include:
- [requirement]
- [requirement]
- [state/action]

Privacy boundary:
- Public catalog must not expose customer-specific data.
- Tablet/WMS customer context is allowed only when explicitly rep-facing or operations-facing.

Verify with [command/check]. Report changed paths.
```
