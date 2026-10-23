# Design direction: Dashboard MPM Maospati

## What this is

A working dashboard for UPTD Puskesmas Maospati. Staff use it to check whether
monthly activity data is complete, trace a number back to its Excel source, and
reconcile differences before a report is printed or submitted. It is not a
marketing site and it is not a generic admin template.

## Direction

**Material pastel.** A calm, modern public-service workspace shaped by Google
Material 3: a white top app bar, pastel tonal surfaces, one blue action colour,
soft elevation, sans typography, and generous rounded corners. The reference is
Material behaviour, not a Google product clone and not a Google logo imitation.

This direction comes from decisions already present in the project: the light
theme, the public-health audience, the source-data note on every panel, and the
need to print or screenshot a page without losing the numbers. Staff should feel
that the page is friendly and current, while still trusting it as an official
working document.

Pastel is used for context, not decoration. The page header, status chips, and
heatmap get tonal fills because they organise information. The rest of the page
stays white and neutral so the numbers remain the focus.

## Dials

- **ENERGY 2:** friendly and institutional, not playful. Blue carries actions and
  active state; pastel supports status and page context.
- **RHYTHM 2:** a rounded summary strip, two-column analysis panels, full-width
  tables, and collapsed utilities. The header and KPI strip share a shape
  language, while tables stay flatter and denser.
- **MOTION 1:** no decorative animation. Hover and focus feedback only, with a
  short 150ms colour or elevation change.

## Palette

| Token | Value | Use |
| --- | --- | --- |
| Page | `#f7f9fc` | Page background |
| Surface | `#ffffff` | Top bar, cards, tables |
| Surface soft | `#f8f9fa` | Table headers, source notes |
| Ink | `#1f1f1f` | Primary text |
| Muted | `#5f6368` | Secondary text and labels |
| Outline | `#e8eaed` | Card and table hairlines |
| Control outline | `#80868b` | Field boundaries, 3:1 against white |
| Primary | `#0b57d0` | Links, active state, primary button |
| Primary strong | `#0842a0` | Primary hover |
| Primary soft | `#e8f0fe` | Page header, active nav, tonal button |
| Mint | `#e6f4ea` on `#137333` | Complete, safe, present |
| Peach | `#fce8e6` on `#c5221f` | Missing, failed, needs attention |
| Lemon | `#fef7e0` on `#b06000` | Warning, partial, needs checking |
| Lavender | `#f3e8fd` on `#7b1fa2` | Secondary category accent |

Chart fills: `#0b57d0`, `#137333`, `#b06000`, `#c5221f`, `#7b1fa2`, `#00796b`,
`#c2185b`, `#3949ab`. These are Google-adjacent categorical colours, at least
3:1 against the chart track, and remain distinguishable in print.

The official emblem's greens are institutional identity, not UI tokens. The mark
is used as supplied and is not recoloured to the blue action palette.

## Typography

- Display and headings: `Google Sans`, `Segoe UI Variable Display`, `Segoe UI`,
  Roboto, Arial, sans-serif. Google Sans is used when installed locally;
  otherwise the page falls back to the system sans. No external font request.
- Body and UI: the same sans stack. Neutral, readable, and consistent with the
  rounded Material surfaces.
- Numbers: tabular figures in tables, KPI values, and axes.
- Headings use slight negative tracking. No wide-tracked uppercase labels.
  Table headers remain sentence case.

## Shape and elevation

| Token | Value | Use |
| --- | --- | --- |
| Page header | `28px` | Hero surface |
| KPI strip | `28px` | Summary surface |
| Card | `24px` | Panels |
| Inner panel | `20px` | Scroll areas, calendar, details |
| Field | `12px` | Selects and inputs |
| Chip | `999px` | Status, filters, navigation |

- Cards use a single hairline outline plus Material elevation 1. They do not
  float on hover because they are not clickable.
- The sticky top bar uses a short shadow to separate it from the page while
  scrolling.
- Pills are reserved for status, navigation, buttons, and compact filters. Table
  rows and panels keep their own radius.

## Components

- **Top app bar:** white surface, official Puskesmas Maospati emblem in its
  original green, sans brand, pill navigation with a pale blue active state, and
  one blue sync action. On phones the app bar becomes one compact row:
  hamburger, emblem, brand, sync icon. The last-sync line sits underneath. The
  menu itself is a disclosure panel, not a second row of horizontal links.
- **Page header:** a pale blue tonal surface that groups the title, description,
  last-sync note, and Drive action. It replaces the old ruled masthead without
  changing the flow of the page.
- **Summary strip:** one rounded surface with four divided statistics, not four
  identical floating cards. Six-stat pages use two wide cells on desktop.
- **Panel:** white rounded surface, sans title, short subtitle, source-data
  footnote at the bottom. The footnote is the product, not filler.
- **Table:** sticky header inside a rounded scroll area, sentence-case headers,
  tabular numerals, soft row rules, and a sticky first column on mobile. The
  respondent table headers are sort buttons; `aria-sort` and a directional
  triangle mark the active column.
- **Status:** pastel chips with dark text. Colour never carries meaning alone;
  the label always says what the state is.
- **Heatmap:** pastel peach, lemon, and mint cells with dark text and a rounded
  cell shape. The legend repeats the same three colours.
- **Mobile navigation:** a 44px hamburger button opens the full menu below the
  app bar. The button changes to an X, `aria-expanded` follows the state, and
  Escape closes the menu and returns focus to the button. Menu rows are 48px.
- **Utilities:** Google Drive contents and the reading guide remain `<details>`
  sections, collapsed by default so the numbers lead.
- **Controls:** filled fields with a visible 3:1 boundary and a blue focus ring.

## Accessibility

- WCAG AA contrast for all text, checked with the antislop contrast script.
- 44px minimum tap targets for navigation, buttons, and fields.
- Visible `:focus-visible` outline on every interactive element.
- Skip link, `aria-current` on the active menu item, `scope="col"` on table
  headers.
- Mobile layout reflows: compact app bar with a hamburger disclosure, a
  two-column summary, single-column panels, and no page-level horizontal
  overflow. The mobile menu keeps a 48px row height and a visible active state.
- Sticky first table column and sticky header remain usable at 320, 360, and
  390 widths.
- `prefers-reduced-motion` respected.
- Print styles remove the top bar, shadows, and tonal fills but keep the data,
  source notes, and table structure.

## What we deliberately do not do

No gradients, glassmorphism, emoji decoration, coloured left stripes, giant
shadows, fake metrics, or generic AI pastel blocks. No Google logo, wordmark, or
product chrome is copied. No pastel fill on every surface: pastel is reserved
for context, status, and the heatmap. No pill navigation on tables or data
cells. The source-data line stays because it is the product, not filler.
