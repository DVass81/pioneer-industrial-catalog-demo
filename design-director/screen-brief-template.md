# Pioneer Screen Brief Template

Use this template before asking Codex, a designer, or an engineer to create a screen. Replace bracketed text with the specific screen details. Keep public catalog, tablet, and WMS requirements separate so private workflow assumptions do not leak into public pages.

## Screen Summary

```yaml
screen:
  name: "[Screen name]"
  mode: "[public_catalog | taylor_tablet | wms | shared]"
  route_or_entry: "[Streamlit page label, app entrypoint, or future route]"
  owner: "[Product/design owner]"
  status: "[draft | ready_for_build | needs_review | shipped]"
  primary_user: "[public buyer | Pioneer sales rep | warehouse associate | admin]"
  business_goal: "[What Pioneer needs this screen to accomplish]"
  user_goal: "[What the user is trying to get done]"
  source_data:
    products: "[CSV/API/table name]"
    customers: "[none for public catalog unless explicitly approved]"
    orders_or_quotes: "[quote cart/session/future WMS table]"
```

## Context

- Where the user came from:
- What they already know:
- What decision or action should be easier after this screen:
- What this screen must not expose:
- Existing Pioneer pages/components to match:

## User Story

As a [user type], I want to [task], so that [outcome].

Acceptance summary:

- [Outcome 1]
- [Outcome 2]
- [Outcome 3]

## Required Content

Above the fold:

- [Brand or page identity]
- [Primary user task]
- [Critical status or account context, if allowed]
- [Primary action]

Product/catalog content:

- Product name
- SKU or product ID
- Category and product type
- Manufacturer or manufacturer part number when available
- Stock status and quantity context
- Lead time
- Bin/location when relevant
- Image with approved source
- Unit price only if allowed for the mode
- Quote-required fallback where final pricing is not confirmed

Service content:

- Pioneer promise or service note
- Pricing/availability confirmation copy
- Delivery or pickup context
- Contact or quote next step

## Public Catalog Requirements

Use this section when `mode` is `public_catalog`.

- No authentication or customer selector.
- No customer-specific pricing, contract terms, quote history, private notes, account recommendations, or demo customer data.
- Quote cart can collect requested items and contact details, but confirmation must explain that Pioneer confirms final pricing, availability, delivery, and payment.
- Category browsing must be clear; do not dump all SKUs into an undifferentiated list.
- Product detail must make SKU, category, image, stock/lead time, and add-to-quote action easy to find.
- Product image quality must support buyer confidence; mark placeholders or review-needed images clearly in internal notes, not public copy.

Public catalog layout checklist:

- [ ] Navigation includes Home, Product Catalog, Product Detail, Quote Cart, Request Quote, About Pioneer Services.
- [ ] Search and category filters are reachable before or beside product results.
- [ ] Product cards show enough facts for comparison without becoming tables.
- [ ] Quote cart summary is visible after adding items.
- [ ] Request quote form has validation and confirmation.

## Taylor Tablet Requirements

Use this section when `mode` is `taylor_tablet`.

- Designed for a rep using a tablet during a field visit, counter conversation, trade show, or guided customer walkthrough.
- Touch targets are at least 44px tall, with no hover-only controls.
- Customer context may be visible only in this rep-facing mode and must be demo, anonymized, or approved data.
- Account selector should make it obvious which customer is active.
- Show visit prep, preferred categories, account notes, and recommended products only when the screen is clearly not public.
- Field order building needs quantity, line note, and substitution preference.
- Actions should be resilient to interruption: cart state, selected customer, and selected product should remain understandable.

Tablet layout checklist:

- [ ] Works at 600-1023px widths without cramped controls.
- [ ] Important facts are in large, scannable strips or compact panels.
- [ ] Product detail image uses a stable 4:3 well.
- [ ] Add-to-order action is close to quantity.
- [ ] Notes and substitution controls are available before handoff.
- [ ] Handoff preview summarizes customer, lines, quantities, notes, and substitutions.

## WMS Requirements

Use this section when `mode` is `wms`.

- Primary users are warehouse associates or operations staff, not public buyers.
- Prioritize pick accuracy, exception handling, and completion confidence.
- Required order facts: order/quote ID, customer, priority, requested date, line count, fulfillment status.
- Required line facts: SKU, product name, bin/location, quantity requested, quantity picked, substitution flag, stock issue flag.
- Every destructive or irreversible action needs confirmation or undo where practical.
- Exceptions must be more visible than normal completed lines.
- Scanning, keyboard entry, and touch entry should all be considered.

WMS layout checklist:

- [ ] Queue view separates ready, blocked, in progress, and completed work.
- [ ] Pick list groups by location/bin where useful.
- [ ] Line status can be updated without losing place.
- [ ] Stock exceptions capture reason and next action.
- [ ] Handoff/completion state is timestamped and attributable.
- [ ] Screen remains usable on tablet carts or compact warehouse stations.

## Interaction Requirements

Primary actions:

- [Action name] -> [Expected result]
- [Action name] -> [Expected result]

Secondary actions:

- [Action name] -> [Expected result]

Empty states:

- No products:
- No matching filters:
- Empty quote cart:
- No selected customer:
- No WMS queue items:

Error states:

- Missing required form fields:
- Product image unavailable:
- Product no longer available:
- Quote/order submission failure:
- WMS stock mismatch:

Loading states:

- Initial data load:
- Filter/search update:
- Submit quote/order:

## Content And Copy

Tone:

- Direct, helpful, and operational.
- Prefer "Request quote" and "Confirm availability" over "Buy now" when final pricing is not guaranteed.
- Avoid unsupported urgency and consumer-shopping language.

Required microcopy:

- Primary CTA:
- Secondary CTA:
- Confirmation:
- Validation:
- Destructive action:
- Permission/private data warning:

## Visual Direction

Use Pioneer design tokens:

- Primary action: `#4C6444`
- Dark brand area: `#344530`
- Text: `#171914`
- Neutral band: `#F4F2EC`
- Panel: `#FFFFFF`
- Border: `#D9DDD6`

Layout:

- [Single column | sidebar + content | grid | queue/table | detail split]
- Max content width:
- Card density:
- Image aspect ratio:
- Sticky elements:

Do not use:

- Decorative gradients or abstract blobs as primary visuals.
- Nested cards.
- Customer-specific content in public catalog screens.
- Tiny tap targets in tablet or WMS screens.

## Data Contract

Fields needed:

```yaml
product:
  product_id: ""
  product_name: ""
  category: ""
  product_type: ""
  sku: ""
  manufacturer: ""
  manufacturer_part_number: ""
  description: ""
  price: ""
  stock_quantity: ""
  lead_time: ""
  bin_location: ""
  image_url_or_ref: ""

customer:
  allowed_modes: ["taylor_tablet", "wms"]
  customer_name: ""
  account_status: ""
  preferred_categories: []
  account_notes: ""
  credit_limit: ""

quote_or_order:
  line_items: []
  requested_by: ""
  contact: ""
  notes: ""
  substitution_preference: ""
  status: ""
```

## Accessibility QA

- [ ] Screen can be navigated by keyboard.
- [ ] Focus states are visible on all interactive controls.
- [ ] Form fields have labels and useful validation messages.
- [ ] Status is not communicated by color alone.
- [ ] Product image alt text is meaningful.
- [ ] Tablet/WMS controls meet minimum touch target sizes.
- [ ] Text does not overlap or truncate critical product facts at mobile, tablet, or desktop widths.

## Final Handoff Notes

- Open questions:
- Dependencies:
- Out of scope:
- Test scenarios:
- Screenshots or references:
