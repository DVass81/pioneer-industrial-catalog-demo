# Pioneer Design Director Pipeline

This folder defines the design direction for the Pioneer Industrial Sales internal development pipeline. It is not app code, customer data, or deployment configuration. It is the working specification for how the team should design, review, and extend the three connected Pioneer systems:

1. Public catalog: a public-facing product discovery and quote-request experience.
2. Taylor tablet mode: a rep-facing field workflow for guided selling, customer context, quote building, and handoff prep.
3. Warehouse management system (WMS): an operations-facing fulfillment and inventory workflow that receives clean handoffs from catalog and tablet activity.

The goal is a premium industrial system: practical, direct, credible, and calm under pressure. Pioneer should feel like a serious supply partner with field knowledge and operational discipline, not a generic ecommerce template or a decorative startup dashboard.

## Audience

These documents are for developers, product owners, designers, and QA reviewers working on Pioneer demos and future production paths. They should be used before writing UI, changing workflow behavior, adding data fields, presenting a demo, or approving a pull request that touches the Pioneer product experience.

## Files

| File | Purpose | Use When |
| --- | --- | --- |
| `pioneer-design-principles.md` | Premium industrial design principles, required behaviors, forbidden moves, copy rules, component guidance, and QA checks. | Designing or reviewing any catalog, tablet, or WMS screen. |
| `system-map.md` | Implementation-ready map of the three-system pipeline, major objects, handoffs, ownership boundaries, and integration expectations. | Planning features, data flows, handoffs, and multi-stage demos. |
| `README.md` | Orientation to the Design Director Pipeline and how to apply it. | Onboarding or starting a new Pioneer task. |

## Product Frame

Pioneer is an industrial sales and supply workflow, not a broad retail storefront.

The experience should help three kinds of users:

| User | Surface | Primary Need |
| --- | --- | --- |
| Public buyer | Public catalog | Find relevant industrial products, understand availability context, and request a quote without friction. |
| Sales rep | Taylor tablet mode | Walk a customer through useful product options, account context, recommendations, and quote/order prep in the field. |
| Warehouse/operator | WMS | Receive a clear, actionable fulfillment signal with items, quantities, availability, bin context, exceptions, and status. |

The systems should share a common product truth while preserving audience boundaries. Public users should not see account-specific data. Sales reps need customer context but not an overloaded warehouse console. Warehouse users need fulfillment clarity, not sales theater.

## Design Director Mandate

Every Pioneer interface should satisfy these requirements:

- Make industrial products inspectable through category, SKU, part number, stock, lead-time, bin/location, and quote/order context.
- Keep public, sales, and warehouse workflows visibly distinct while allowing clean handoffs between them.
- Favor dense, scan-friendly information over oversized marketing sections.
- Present demo data honestly as sample, synthetic, anonymized, or explicitly approved.
- Use Pioneer brand cues with restraint: olive green, charcoal, warm neutrals, sturdy typography, clear hierarchy, and product imagery that helps recognition.
- Treat the tablet workflow as a field tool built for speed, confidence, and customer conversation.
- Treat WMS screens as operational tools built for accuracy, exception handling, and status visibility.

## Pipeline Workflow

Use this sequence for any new Pioneer feature:

1. Identify the surface: catalog, tablet, WMS, or cross-system handoff.
2. Confirm the user: public buyer, sales rep, customer in conversation, warehouse operator, manager, or demo reviewer.
3. Name the operational job: browse, compare, quote, recommend, reserve, pick, stage, update, or review.
4. Check the forbidden moves in `pioneer-design-principles.md`.
5. Check the system boundary and data contract in `system-map.md`.
6. Design the screen or behavior using the required patterns in `pioneer-design-principles.md`.
7. QA with realistic product, customer, quote, and inventory states.

## Definition of Done

A Pioneer design or implementation is ready for review when:

- The screen has a clear primary job and does not mix unrelated audience needs.
- Product rows/cards expose the fields needed for industrial decision-making.
- Empty, loading, error, and out-of-stock states are explicitly handled.
- Public catalog surfaces do not expose customer accounts, negotiated pricing, private notes, quote history, or warehouse-only controls.
- Tablet surfaces make customer context obvious and reversible.
- WMS surfaces make fulfillment state, quantity, location, and exceptions obvious.
- Handoffs preserve source, line items, quantities, status, and follow-up ownership.
- Copy is practical, specific, and free of vague marketing filler.
- Visual styling feels premium industrial: restrained, durable, organized, and trustworthy.

## Non-Goals

Do not use these documents to:

- Redesign unrelated application code.
- Introduce real customer data.
- Collapse public catalog, tablet mode, and WMS into one generic app shell.
- Create consumer ecommerce behavior that hides quote, fulfillment, and account realities.
- Replace engineering specs, database migrations, or security reviews.

These docs define product and design direction. Implementation still requires normal code review, data review, and deployment QA.
