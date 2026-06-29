# Pioneer Design System Template

Use this file as the working source of truth for Pioneer UI direction before implementation. Keep the system practical, catalog-first, and aligned with the existing Streamlit experience unless a project brief explicitly expands the brand.

## System Intent

Pioneer Industrial Sales should feel direct, service-minded, and operational. The interface must help buyers and reps find industrial supplies quickly, understand stock and lead-time context, and build a quote or field order without marketing friction.

Primary experience modes:

- Public catalog: open browsing, product details, quote cart, request quote, service overview.
- Taylor field tablet: rep-facing customer visit workflow, account-aware recommendations, line notes, substitution preference, warehouse handoff preview.
- Future WMS: fulfillment queue, pick/pack verification, inventory exceptions, order readiness.

## Brand Defaults

```yaml
brand:
  name: Pioneer Industrial Sales
  short_name: Pioneer
  promise: We Sell Service.
  product_category: Industrial supply catalog and quote workflow
  voice:
    attributes:
      - practical
      - knowledgeable
      - service-first
      - calm under pressure
      - inventory-aware
    write_like:
      - "Use clear industrial language: SKU, lead time, bin, stock, quote cart."
      - "Prefer exact next steps over promotional claims."
      - "Call out confirmation needs for pricing, availability, delivery, and payment."
    avoid:
      - consumer ecommerce hype
      - unsupported price certainty
      - exposing customer-specific data in public catalog
      - long paragraphs in operational screens
```

## YAML Tokens

These defaults are concrete Pioneer values for design exploration, handoff prompts, Streamlit CSS, and future component libraries. Keep token names stable so screen briefs and Codex prompts can reference them.

```yaml
tokens:
  color:
    brand:
      pioneer_olive: "#4C6444"
      pioneer_olive_dark: "#344530"
      pioneer_ink: "#171914"
      pioneer_charcoal: "#252826"
      pioneer_moss: "#6F7D57"
      pioneer_service_gold: "#B08A3C"
    surface:
      page: "#F7F6F1"
      panel: "#FFFFFF"
      panel_subtle: "#F8FAF7"
      neutral_band: "#F4F2EC"
      raised: "#FFFFFF"
      inverse: "#252826"
    text:
      primary: "#171914"
      secondary: "#59615B"
      muted: "#727A74"
      inverse: "#FFFFFF"
      link: "#344530"
      warning: "#704B00"
      danger: "#8A2D23"
      success: "#315A35"
    border:
      default: "#D9DDD6"
      subtle: "#E3E6DF"
      strong: "#B8C0B2"
      focus: "#4C6444"
    state:
      success_bg: "#EEF6EC"
      success_fg: "#315A35"
      warning_bg: "#FFF3D6"
      warning_fg: "#704B00"
      danger_bg: "#FBE9E6"
      danger_fg: "#8A2D23"
      info_bg: "#EEF3F6"
      info_fg: "#2F5362"
      stock_good_bg: "#EEF6EC"
      stock_low_bg: "#FFF3D6"
      stock_out_bg: "#FBE9E6"
    category:
      safety: "#C7483B"
      electrical: "#D9A62E"
      fasteners: "#6F7D57"
      hydraulics: "#327A78"
      abrasives: "#6B6478"
      material_handling: "#5B6F8E"
      cutting_tools: "#8A5A2B"
      mro: "#4C6444"

  typography:
    font_family:
      ui: "Inter, Segoe UI, system-ui, sans-serif"
      data: "Roboto Mono, Consolas, monospace"
    scale:
      display:
        size: "40px"
        line_height: "48px"
        weight: 800
      h1:
        size: "32px"
        line_height: "40px"
        weight: 800
      h2:
        size: "24px"
        line_height: "32px"
        weight: 750
      h3:
        size: "18px"
        line_height: "26px"
        weight: 750
      body:
        size: "16px"
        line_height: "24px"
        weight: 400
      compact:
        size: "14px"
        line_height: "20px"
        weight: 400
      caption:
        size: "12px"
        line_height: "16px"
        weight: 600
      data:
        size: "13px"
        line_height: "18px"
        weight: 500
    casing:
      nav: "title"
      labels: "sentence"
      table_headers: "sentence"
      status_chips: "sentence"

  spacing:
    0: "0"
    1: "4px"
    2: "8px"
    3: "12px"
    4: "16px"
    5: "20px"
    6: "24px"
    8: "32px"
    10: "40px"
    12: "48px"
    16: "64px"
    page_padding_desktop: "32px"
    page_padding_tablet: "20px"
    page_padding_mobile: "16px"
    section_gap: "24px"
    card_gap: "12px"

  radius:
    none: "0"
    sm: "4px"
    md: "8px"
    pill: "999px"

  shadow:
    none: "none"
    raised: "0 8px 20px rgba(37, 40, 38, 0.06)"
    overlay: "0 18px 40px rgba(37, 40, 38, 0.16)"

  layout:
    max_content_width: "1180px"
    catalog_grid_min: "240px"
    tablet_min_touch_target: "44px"
    sidebar_width: "280px"
    detail_image_aspect_ratio: "4 / 3"
    product_tile_min_height: "265px"
    table_row_min_height: "48px"

  motion:
    duration_fast: "120ms"
    duration_base: "180ms"
    duration_slow: "240ms"
    easing: "cubic-bezier(0.2, 0, 0, 1)"
    reduce_motion_rule: "Disable nonessential transitions when prefers-reduced-motion is active."

  components:
    button:
      radius: "{tokens.radius.md}"
      min_height: "44px"
      primary_bg: "{tokens.color.brand.pioneer_olive}"
      primary_fg: "{tokens.color.text.inverse}"
      secondary_bg: "{tokens.color.surface.panel}"
      secondary_fg: "{tokens.color.text.primary}"
      border: "{tokens.color.border.default}"
    card:
      radius: "{tokens.radius.md}"
      bg: "{tokens.color.surface.panel}"
      border: "{tokens.color.border.default}"
      shadow: "{tokens.shadow.raised}"
    field:
      radius: "{tokens.radius.md}"
      bg: "{tokens.color.surface.panel}"
      border: "{tokens.color.border.default}"
      focus_ring: "2px solid {tokens.color.border.focus}"
    chip:
      radius: "{tokens.radius.pill}"
      bg: "{tokens.color.surface.panel_subtle}"
      border: "{tokens.color.border.subtle}"
      fg: "{tokens.color.text.primary}"
```

## Core Layout Principles

- Catalog pages optimize for scanning: left or top filters, dense product facts, predictable quote actions.
- Public pages must never show demo customer profiles, negotiated pricing, quote history, private notes, or account-specific recommendations.
- Tablet pages prioritize touch targets, short field notes, customer context, and quick add-to-order actions.
- WMS pages prioritize exception visibility, pick sequence, location/bin accuracy, and confirmation states.
- Product media uses real, cleared, or explicitly approved demo images. Avoid decorative stock imagery when the user needs to inspect an item.

## Breakpoints

```yaml
breakpoints:
  mobile:
    min: 0
    max: 599
    behavior: "Single column; filters collapse above catalog results; sticky quote action allowed."
  tablet:
    min: 600
    max: 1023
    behavior: "Two-column where useful; touch target minimum 44px; primary actions visible without hover."
  desktop:
    min: 1024
    max: 1439
    behavior: "Sidebar navigation and multi-column catalog grids."
  wide:
    min: 1440
    behavior: "Constrain content width; do not stretch product cards beyond useful scan width."
```

## Accessibility Requirements

- Minimum contrast: 4.5:1 for body text, 3:1 for large text and non-text UI boundaries.
- Keyboard: all filters, quantity controls, product links, cart updates, and request quote actions must be reachable and visible on focus.
- Product images require useful alt text using product name and type, not "image".
- Status color must be paired with text, icon, or label.
- Forms need explicit labels, validation messages, and confirmation state.
- Tablet workflows must not rely on hover-only affordances.

## Implementation Notes

- Streamlit CSS should map directly to the token intent above even if Streamlit does not support tokens natively.
- Keep cards at 8px radius or less unless a platform component requires otherwise.
- Use stable dimensions for product tiles, image wells, data tables, and quantity controls to prevent layout shifts.
- Prefer one source of formatting truth for money, lead time, availability, and quote IDs.
- Treat Stage 2 tablet and future WMS styling as extensions of the same system, not separate brands.
