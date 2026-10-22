# Design direction: Dashboard MPM Maospati

## What this is

A working dashboard for UPTD Puskesmas Maospati. Staff use it to check whether
monthly activity data is complete, trace a number back to its Excel source, and
reconcile differences before a report is printed or submitted. It is not a
marketing site and it is not a generic admin template.

## Direction

**Lembar kerja puskesmas.** An official working paper crossed with a statistical
bulletin: warm paper, deep green ink, hairline rules, serif headings, compact
sans body text, and tables that read like a printed report. The data is the
decoration. Panels are ruled sheets, not floating cards.

This direction comes from decisions already present in the project: the light
theme, the public-health audience, the source-data note on every panel, and the
need to print or screenshot a page without losing the numbers.

## Dials

- **ENERGY 3:** confident and institutional, not loud. One accent colour, used
  for actions and active state.
- **RHYTHM 3:** a summary strip, two-column analysis panels, full-width tables,
  and collapsed utilities. Sections do not all look the same.
- **MOTION 1:** no decorative animation. Hover and focus feedback only.

## Palette

| Token | Value | Use |
| --- | --- | --- |
| Paper | `#f7f4ec` | Page background |
| Surface | `#fffdf8` | Panels and header |
| Ink | `#1b2622` | Primary text |
| Muted | `#55615b` | Secondary text |
| Rule | `#d8d2c4` | Hairlines |
| Rule strong | `#a9a294` | Table and section rules |
| Accent | `#14594a` | Links, active state, primary button |
| Accent soft | `#e7efe9` | Tinted backgrounds |
| Warning | `#7a4e0a` on `#f6ecd6` | Data that needs checking |
| Danger | `#9c3527` on `#f7e5e0` | Missing or failed data |

Chart fills: `#14594a`, `#3f7d6b`, `#8a5a12`, `#a05a3c`, `#4f6d7a`,
`#6b5a3e`, `#7a2f4a`, `#2f6f8a`. They are muted, distinguishable, and at least
4:1 against the chart track. No rainbow palette.

## Typography

- Headings: `Iowan Old Style`, `Palatino Linotype`, `Book Antiqua`, Palatino,
  Georgia, serif. Public-report character, available offline.
- Body and UI: `Segoe UI`, system UI. Neutral, readable, no external font
  request.
- Numbers: tabular figures in tables and KPI values.
- No wide-tracked uppercase labels. Table headers are sentence case.

## Components

- **Header:** typographic MPM mark, double rule under the masthead, horizontal
  text navigation with an underline for the active page.
- **Summary strip:** one bordered strip with four divided statistics, not four
  identical cards.
- **Panel:** flat surface, one-pixel rule, no shadow, serif title, short
  subtitle underneath, source-data footnote at the bottom.
- **Table:** sticky header inside a scroll area, sentence-case headers, tabular
  numerals, hairline row rules.
- **Status:** small square stamps for `sinkron`, `perlu dicek`, and
  `tidak aktif`. No capsule badges.
- **Utilities:** Google Drive contents and the reading guide are `<details>`
  sections, collapsed by default so the numbers lead.

## Accessibility

- WCAG AA contrast for all text, checked with the antislop contrast script.
- 44px minimum tap targets for navigation and buttons.
- Visible `:focus-visible` outline on every interactive element.
- Skip link, `aria-current` on the active menu item, `scope="col"` on table
  headers.
- Mobile layout reflows: stacked header, scrollable text navigation, two-column
  summary, single-column panels, no page-level horizontal overflow.
- `prefers-reduced-motion` respected.

## What we deliberately do not do

No gradients, glassmorphism, emoji decoration, coloured left stripes, pill
navigation, floating shadows, rainbow charts, invented metrics, or decorative
dashboards. The source-data line stays because it is the product, not filler.
