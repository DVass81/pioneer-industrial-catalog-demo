# Pioneer Design Principles

Pioneer should feel like a premium industrial operating system: grounded, precise, durable, and built for people who need to make good decisions quickly. The interface must respect the work. Buyers, reps, and warehouse teams are not browsing for amusement; they are checking fit, availability, timing, account context, and next action.

## North Star

Design every Pioneer screen around this promise:

> Show the right industrial detail at the right moment so the next operational action is obvious.

That means the interface must make product reality visible: category, SKU, manufacturer part number, availability, lead time, bin/location, quote state, customer relevance, and fulfillment status. Beauty comes from order, hierarchy, material honesty, and speed.

## Product Personality

| Attribute | Meaning in UI | Avoid |
| --- | --- | --- |
| Field-ready | Works in a warehouse, shop floor, counter, or customer visit. Large enough targets, fast scanning, resilient states. | Fragile, overdelicate layouts that collapse under real data. |
| Premium industrial | Strong hierarchy, restrained brand color, high-quality product imagery, confident spacing, clear data tables. | Generic SaaS gloss, decorative gradients, or oversized marketing cards. |
| Accountable | Shows where numbers and statuses come from and what still needs confirmation. | Pretending demo availability or pricing is final when it is not. |
| Practical | Every control moves the user toward browse, compare, quote, recommend, pick, or resolve. | Decorative controls, vague icons, or feature tours embedded in the UI. |
| Calm | Errors, exceptions, and stock constraints are visible without panic. | Alarm-color overload or hidden failure states. |

## Design Principles

### 1. Industrial Detail Is the Hero

Product information should carry the experience. A row or detail view is successful when a user can answer:

- What is this item?
- What category and product type does it belong to?
- What SKU or manufacturer part number identifies it?
- Is it stocked, constrained, backordered, or quote-only?
- Where is it located or fulfilled from when relevant?
- What action can I take next?

Required product fields by surface:

| Field | Public Catalog | Tablet Mode | WMS |
| --- | --- | --- | --- |
| Product name | Required | Required | Required |
| Category/product type | Required | Required | Useful |
| SKU | Required | Required | Required |
| Manufacturer part number | Required when available | Required when available | Required when available |
| Product image | Required for browse/detail when available | Required for guided selling | Optional, useful for pick verification |
| Stock/availability | Required as context, not final promise | Required with account caveats | Required as operational truth |
| Lead time | Required when known | Required when known | Required when exception affects fulfillment |
| Bin/location | Optional public context | Useful for field confidence | Required when available |
| Quote/order state | Quote request only | Quote/order prep | Pick, stage, fulfill, exception |

### 2. Separate Audiences, Connect Their Work

The three systems must remain distinct:

- Public catalog is for open product discovery and quote requests.
- Tablet mode is for sales reps using customer context.
- WMS is for warehouse execution and inventory accountability.

The connection is the handoff, not a shared wall of every feature. A public buyer does not need a customer selector. A rep does not need a pick queue during a customer conversation. A warehouse operator does not need sales recommendation copy.

### 3. Design for Repeated Use

Pioneer screens should support repeated daily work. Favor:

- Dense but legible tables.
- Persistent filters.
- Search that respects SKU, product name, category, and part number.
- Clear selected-customer or selected-order context.
- Fast quantity edits.
- Visible status chips.
- Compact detail panels.
- Stable layouts that do not jump when filters or cart lines change.

Avoid single-use landing-page patterns inside operational surfaces.

### 4. Show Status and Uncertainty Honestly

Availability, pricing, customer terms, and fulfillment state often require confirmation. The interface should distinguish:

- In stock.
- Low stock.
- Lead time required.
- Quote required.
- Pending confirmation.
- Ready for warehouse review.
- Exception.
- Completed.

Never make uncertain demo data look like final contractual truth. Use copy such as "Pioneer will confirm final pricing and availability" where needed.

### 5. Use Brand as Structure

Pioneer brand expression should come through disciplined interface choices:

- Olive green for primary action, key section identity, and selected states.
- Charcoal and black-green text for authority and readability.
- Warm neutral backgrounds for separation and reduced glare.
- Product photography as practical recognition, not decorative mood.
- Compact cards only where a repeated item benefits from framing.
- Tables, bands, panels, and detail drawers for work surfaces.

The brand should feel steady and capable. It should not feel like a themed template.

## Required Behaviors

### Navigation

- Keep public catalog, tablet mode, and WMS entrypoints clearly named.
- Make the current surface obvious at all times.
- Keep account-specific screens out of public navigation.
- Preserve user context when moving from catalog browse to cart or quote request.
- Preserve selected customer context in tablet mode until changed deliberately.
- Preserve selected warehouse queue or order context in WMS until completed or exited.

### Search and Filtering

- Search must support product name, SKU, manufacturer part number, category, and product type when data exists.
- Category filters should never leave the user stranded without a way back to all categories.
- Empty results must explain the filter/search state and provide a reset action.
- Filters should be visually compact and close to the result set they affect.
- On tablet, filter controls must be touch-friendly and usable during conversation.

### Product Cards and Rows

- Always show product name, SKU, category or type, and availability context.
- Show the product image where it improves recognition.
- Place the primary action consistently: add to quote, add to order, review item, or pick line.
- Keep quantity edits close to the line item they affect.
- Avoid hiding essential industrial identifiers behind hover-only UI.

### Quote and Cart Flow

- Quote cart must show every line item, quantity, SKU, and enough description to verify intent.
- Quantity changes must be explicit and reversible.
- Removal must be clear and scoped to a single line.
- Request quote flow must collect only necessary contact/request information for the current demo stage.
- Confirmation should provide a readable reference ID.
- Public quote copy must say that Pioneer confirms final pricing, availability, delivery, and payment instructions.

### Tablet Mode

- The selected customer must be visible on every account-aware screen.
- Customer switching must be deliberate and obvious.
- Recommendations must show why they are relevant: preferred category, prior quote placeholder, field note, or replenishment logic.
- Sales reps need quick add, quantity edit, note capture, and handoff preview.
- Tablet layouts must support touch: comfortable row height, clear selected states, and no tiny critical controls.
- Keep the customer conversation clean: do not expose internal debugging, raw data dumps, or warehouse-only details.

### WMS

- WMS screens must prioritize order/quote reference, line items, quantity, bin/location, status, and exceptions.
- Operators must be able to tell what is ready, blocked, partially available, staged, or complete.
- Exceptions need a reason, owner, and next action.
- Inventory-affecting actions should be explicit and auditable in production paths.
- WMS should receive handoff data from catalog/tablet flows but should not inherit their presentation language.

### Error, Empty, and Loading States

- Loading states should preserve layout shape where possible.
- Empty states should name the missing object: products, quote lines, customers, warehouse tasks, or images.
- Error states should explain what failed and what the user can do next.
- Never show raw stack traces, file paths, secrets, or internal script names in user-facing UI.

## Forbidden Moves

Do not do any of the following:

- Put demo customer accounts, negotiated pricing, quote history, or private notes in the public catalog.
- Treat public catalog as a logged-in account portal without an explicit product decision.
- Combine catalog, tablet, and WMS into one indistinct dashboard.
- Use oversized hero sections as the main operational screen.
- Use decorative gradients, floating blobs, abstract illustrations, or generic stock imagery as a substitute for product clarity.
- Use one-note green styling everywhere; green is an accent and state color, not the whole interface.
- Hide SKU, part number, stock, lead time, or line-item quantities when those fields are relevant.
- Use vague CTA labels such as "Learn More" when the action is actually "View Details", "Add to Quote", "Review Handoff", or "Mark Picked".
- Present sample product photos as verified exact matches when they are placeholders or visual stand-ins.
- Show real customer data unless explicitly approved for the environment.
- Use tiny icon-only destructive controls without label, tooltip, or confirmation pattern.
- Make warehouse exception states look like normal informational notes.
- Let a selected customer, cart, or warehouse order become ambiguous.

## Component Guidance

### Tables

Use tables for product lists, quote lines, WMS queues, order lines, and audit-style status views. Tables should support scanning and comparison.

Recommended columns:

| Surface | Columns |
| --- | --- |
| Public catalog | Product, category/type, SKU, manufacturer part number, stock/lead time, action |
| Tablet recommendations | Product, reason, SKU, stock/lead time, quantity, add action |
| Quote cart | Product, SKU, quantity, availability note, remove/update |
| WMS queue | Reference, source, customer/account if allowed, status, line count, priority, updated time |
| WMS line items | Item, SKU, quantity requested, quantity available, bin/location, status, exception |

### Cards

Use cards for repeated browsable product tiles, customer summary blocks, recommendation items, and compact status summaries. Cards should remain utilitarian:

- Small radius.
- Clear title.
- One strong image or identifier.
- Two to four high-value facts.
- One primary action.

Do not use nested cards or card-heavy decorative layouts for main work areas.

### Status Chips

Status chips should be short, consistent, and meaningful:

- `In stock`
- `Low stock`
- `Lead time`
- `Quote required`
- `Pending`
- `Ready for WMS`
- `Picking`
- `Staged`
- `Exception`
- `Complete`

Use color with text, never color alone.

### Actions

Action labels should be operational:

- `View Details`
- `Add to Quote`
- `Update Quantity`
- `Remove Line`
- `Request Quote`
- `Select Customer`
- `Add to Order`
- `Preview Handoff`
- `Send to Warehouse`
- `Mark Picked`
- `Flag Exception`
- `Resolve Exception`

### Copy

Voice should be clear, specific, and plainspoken.

Use:

- "Pioneer will confirm final pricing and availability."
- "3 lines ready for warehouse review."
- "Low stock: confirm before promising delivery."
- "No products match this category and search."

Avoid:

- "Unlock seamless industrial excellence."
- "Revolutionize your workflow."
- "Browse our amazing solutions."
- "Click here."

## Surface-Specific Standards

### Public Catalog Standard

The public catalog should answer: "Can Pioneer likely help me source this, and how do I ask for a quote?"

Must include:

- Category-led browsing.
- Product search.
- Product details with industrial identifiers.
- Quote cart.
- Request quote confirmation.
- Clear demo/sample-data boundary.

Must exclude:

- Customer selector.
- Private account data.
- Negotiated pricing.
- Rep notes.
- Warehouse picking controls.

### Taylor Tablet Mode Standard

Tablet mode should answer: "What should I show or build for this customer while I am with them?"

Must include:

- Selected customer context.
- Account-aware recommendations or preferred categories.
- Fast product lookup.
- Quote/order builder.
- Notes or handoff context when appropriate.
- Warehouse handoff preview for future WMS work.

Must exclude:

- Public marketing framing.
- Crowded desktop-only controls.
- Warehouse task execution.
- Hidden customer context.

### WMS Standard

WMS should answer: "What needs to be picked, staged, resolved, or completed?"

Must include:

- Queue of incoming handoffs.
- Source reference and status.
- Line-item quantities.
- Bin/location when available.
- Availability and exception state.
- Clear next actions.

Must exclude:

- Sales pitch content.
- Public quote-request copy.
- Decorative product browsing.
- Ambiguous inventory-changing actions.

## QA Checklist

Use this checklist before approving a Pioneer UI change:

- The surface and user are obvious within five seconds.
- Product identifiers are visible wherever selection or fulfillment decisions happen.
- Search and filters have reset paths.
- Empty states are specific and useful.
- Public catalog contains no account-specific data.
- Tablet mode always shows selected customer context.
- WMS status and exceptions are visible without drilling into every row.
- Quote/order lines show quantity and SKU.
- Availability uncertainty is phrased honestly.
- Primary actions use specific operational verbs.
- Touch targets are adequate on tablet workflows.
- Product imagery is relevant or explicitly treated as placeholder/sample.
- The layout remains stable with long product names and realistic line counts.
- No raw internal file paths, debug output, secrets, or real unapproved customer data appear.
