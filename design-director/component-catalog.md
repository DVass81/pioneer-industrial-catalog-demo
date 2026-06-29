# Pioneer Component Catalog

This catalog defines reusable UI components for Pioneer Industrial Sales. Each entry includes purpose, where to use it, when not to use it, design notes, implementation notes, and accessibility notes.

## App Shell

Purpose: Provides the consistent Pioneer frame: logo, brand promise, navigation, quote/order context, and page content area.

Where to use: Public catalog Streamlit app, Taylor tablet entrypoint, future WMS entrypoint with mode-specific navigation.

When not to use: Embedded widgets, print exports, emails, or small modal-like panels where full navigation would distract.

Design notes:

- Sidebar may use Pioneer dark green and brand logo.
- Public catalog nav includes Home, Product Catalog, Product Detail, Quote Cart, Request Quote, About Pioneer Services.
- Tablet nav should foreground account, visit prep, lookup, order, and handoff tasks.
- WMS nav should foreground queue, picking, exceptions, and completed work.

Implementation notes:

- Keep page mode explicit so public catalog does not render customer context.
- Reuse existing Streamlit sidebar patterns.
- Keep quote/cart or active order summary available without crowding primary navigation.

Accessibility notes:

- Navigation labels must be text, not icons alone.
- Current page must be visually and programmatically clear where feasible.
- Sidebar content must remain usable when collapsed or on smaller screens.

## Product Search And Filter Bar

Purpose: Helps users narrow products by query, category, product type, stock, and other catalog facts.

Where to use: Public product catalog, tablet product lookup, WMS item search.

When not to use: Small recommendation lists with fewer than six items or final order review screens.

Design notes:

- Place before results on mobile and tablet; sidebar or top row on desktop.
- Category and product type filters should be easy to reset.
- Search should support product name, SKU, manufacturer part number, and category terms.

Implementation notes:

- Persist selected filters during product detail drill-in when practical.
- Avoid expensive filtering on every keystroke if data grows significantly.
- Show a clear count of matching products.

Accessibility notes:

- Every input/select needs a visible label.
- Reset filters must be keyboard reachable.
- Empty result text should explain how to recover.

## Product Card

Purpose: Presents a scannable product option with enough facts to compare and take action.

Where to use: Catalog grids, tablet recommendations, related products.

When not to use: Dense WMS pick lists where table rows are faster, or product detail pages where full facts are needed.

Design notes:

- Stable image well with 4:3 aspect ratio.
- Show product name, category/type, SKU, stock/lead time, and primary action.
- Keep description short; avoid pushing actions below inconsistent card heights.
- Use status chips for stock context.

Implementation notes:

- Use fixed or minimum card heights to prevent grid jumping.
- Product image source may be local or approved remote data; missing images need a graceful fallback.
- Card action should set selected product or add to quote/order based on mode.

Accessibility notes:

- Image alt text should include product name.
- Product name link/button needs a clear accessible label.
- Stock status must include text, not only color.

## Product Detail Panel

Purpose: Gives a buyer or rep confidence to quote/order the right item.

Where to use: Public Product Detail page, tablet selected product detail, product drawer in future WMS exceptions.

When not to use: Product grids or pick queues where users need fast line-by-line scanning.

Design notes:

- Use split layout on desktop/tablet: image on one side, facts/actions on the other.
- Required facts: product name, SKU/product ID, category, product type, manufacturer part number, stock, lead time, bin/location when relevant.
- Public mode should say "Request quote" rather than implying final purchase.
- Tablet mode may show account-aware price only when explicitly allowed.

Implementation notes:

- Handle stale selected product IDs with a friendly info state.
- Keep quantity control near add action.
- Use shared formatting helpers for money, lead time, and stock labels.

Accessibility notes:

- Detail heading must identify the product.
- Quantity input requires label and validation.
- Add action confirmation should be announced or visibly persistent.

## Quote Cart Summary

Purpose: Shows selected public catalog items before quote request.

Where to use: Sidebar summary, Quote Cart page, Request Quote review.

When not to use: Taylor field order handoff, which needs customer, line notes, and substitution preferences.

Design notes:

- Show line item name, SKU, quantity, and remove/update controls.
- Include a plain note that Pioneer confirms final pricing and availability.
- Empty cart should direct users back to Product Catalog.

Implementation notes:

- Store cart by product ID and quantity.
- Validate quantity minimums.
- Keep remove action specific to each line.

Accessibility notes:

- Quantity controls need labels tied to product names.
- Remove controls need descriptive labels, not just "Remove".
- Confirmation message should be visible after submission.

## Request Quote Form

Purpose: Captures enough public buyer information for Pioneer to follow up.

Where to use: Public Request Quote page after one or more quote cart items.

When not to use: Rep tablet field order flow, WMS picking, or account-specific order entry.

Design notes:

- Required fields should be obvious.
- Keep fields practical: name, company, email/phone, notes, requested items.
- Confirmation should include generated quote request ID when available.

Implementation notes:

- Validate required contact fields before submission.
- Do not collect payment details in Phase 1.
- Do not expose or infer private customer records from public form input.

Accessibility notes:

- Use explicit labels and inline validation.
- Required fields must be conveyed in text.
- Confirmation state should be reachable after submit.

## Customer Context Strip

Purpose: Shows the active account in Taylor tablet or WMS workflows.

Where to use: Rep tablet hero, order handoff, WMS order detail.

When not to use: Public catalog pages.

Design notes:

- Show customer name, account status, preferred category, and key visit note when allowed.
- Keep it compact and clearly rep/operations-facing.
- Use neutral panels rather than flashy profile cards.

Implementation notes:

- Gate rendering by mode.
- Use demo, anonymized, or approved data only.
- Provide an empty state when no customer is selected.

Accessibility notes:

- Do not encode account status by color alone.
- Long customer names must wrap without overlapping nearby controls.
- Account selector needs a clear label.

## Tablet Order Builder

Purpose: Lets a sales rep build an in-person field order or quote with customer context.

Where to use: Taylor tablet workflow after product lookup or recommendation selection.

When not to use: Public quote cart or warehouse picking.

Design notes:

- Touch-first quantity controls.
- Line note and substitution preference are first-class fields.
- Summary should always show active customer and line count.
- Use "field order" or "handoff" language, not checkout.

Implementation notes:

- Keep `cart_line_details` or equivalent line metadata separate from public cart state.
- Clear line details when a product is removed.
- Generate handoff preview before final submission.

Accessibility notes:

- Controls must be at least 44px tall.
- Dropdowns and note fields require labels.
- Toasts should not be the only confirmation.

## Warehouse Handoff Preview

Purpose: Summarizes what operations needs to pick, confirm, or resolve.

Where to use: Taylor tablet handoff, future WMS intake.

When not to use: Public buyer request confirmation.

Design notes:

- Include customer, requested date, line items, quantities, substitutions, notes, and stock/bin context.
- Highlight exceptions or quote-required lines.
- Use a sober operational style with clear statuses.

Implementation notes:

- Build from current order/cart state.
- Preserve line notes verbatim but escape user-entered text when rendering HTML.
- Future integration should map to WMS queue statuses.

Accessibility notes:

- Status labels must be text.
- Tables need headers that identify product and fulfillment facts.
- Ensure the preview is readable on tablet width.

## WMS Queue Row

Purpose: Represents one order or pick task in an operations queue.

Where to use: Future WMS queue, dashboard, or fulfillment board.

When not to use: Public catalog, marketing pages, or product recommendation grids.

Design notes:

- Show order/quote ID, customer, priority, line count, requested date, status, and primary next action.
- Blocked or exception rows should be visually stronger than ready rows.
- Avoid overusing color; pair color with status text and icons if available.

Implementation notes:

- Row actions should be idempotent where possible.
- Keep status transitions explicit.
- Support sorting or grouping by priority, status, and requested date.

Accessibility notes:

- Rows must remain understandable when read linearly.
- Keyboard users must be able to open details and change status.
- Priority indicators need text equivalents.

## WMS Pick Line

Purpose: Guides warehouse staff through accurate item picking.

Where to use: Future WMS pick detail, exception resolution, printed pick support.

When not to use: Public product browsing or buyer quote cart.

Design notes:

- Put bin/location, SKU, product name, quantity requested, and quantity picked in predictable positions.
- Make exception states obvious: short stock, substitute needed, damaged, cannot find.
- Support scan or manual entry patterns.

Implementation notes:

- Validate picked quantity against requested quantity and stock rules.
- Record exception reason and next action.
- Avoid losing scroll position after a line update.

Accessibility notes:

- Quantity fields need labels and numeric validation.
- Error text must be close to the affected line.
- Touch targets must work with gloves or warehouse tablet use where relevant.

## Status Chip

Purpose: Labels stock, quote, account, order, or WMS state compactly.

Where to use: Product cards, detail facts, queue rows, order summaries.

When not to use: Long explanatory messages or primary actions.

Design notes:

- Use sentence case labels like "In stock", "Low stock", "Quote required", "Blocked".
- Pair color with text.
- Keep chip shape pill-like; avoid oversized badges.

Implementation notes:

- Centralize status-to-style mapping.
- Provide safe fallback for unknown statuses.
- Do not use status chips as buttons unless they are visibly interactive.

Accessibility notes:

- Text contrast must meet minimum requirements.
- Screen readers should receive the status text.
- Avoid color-only meaning.

## KPI Fact Tile

Purpose: Displays one important metric or fact.

Where to use: Tablet customer summary, WMS dashboard, service overview.

When not to use: Product facts that belong in a table/detail layout or metrics without a clear action.

Design notes:

- Use compact label, strong value, and optional short helper text.
- Keep tiles uniform height.
- Do not overpopulate a screen with decorative metrics.

Implementation notes:

- Values should be formatted consistently.
- Long values must wrap.
- Keep data refresh behavior clear if metrics become live.

Accessibility notes:

- Label and value should read together.
- Avoid relying on visual position alone to explain meaning.
- Ensure compact helper text remains legible.

## Empty State

Purpose: Helps the user recover when there is no data or no current selection.

Where to use: Empty cart, no matching products, no selected customer, no WMS queue.

When not to use: Brief loading moments where skeletons or spinners are more appropriate.

Design notes:

- Say what happened and offer the next useful action.
- Keep copy short and operational.
- Avoid playful or vague language.

Implementation notes:

- Empty states should be mode-aware.
- Public empty cart should link users back to Product Catalog.
- Tablet no-customer state should prompt selection before recommendations.

Accessibility notes:

- Empty state action must be keyboard reachable.
- Do not present critical recovery guidance only in an icon.

## Confirmation And Toast

Purpose: Confirms that an action succeeded without derailing the workflow.

Where to use: Added to quote cart, added to field order, quote submitted, handoff created.

When not to use: Critical errors, destructive confirmations, or final states that need persistent review.

Design notes:

- Toasts can acknowledge quick actions.
- Persistent confirmation is required for submitted quote/order IDs.
- Use specific copy: "Added to quote cart" beats "Success".

Implementation notes:

- Do not make toast the only record of a submitted request.
- Include generated IDs in persistent confirmations when available.
- Clear stale success messages when the user starts a new flow.

Accessibility notes:

- Important confirmations must remain visible.
- Toast text should be concise and understandable.
- Do not rely on animation to communicate success.
