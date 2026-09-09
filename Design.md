---
name: Modern FinTech Expense Experience
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#45464d'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#76777d'
  outline-variant: '#c6c6cd'
  surface-tint: '#565e74'
  primary: '#0f172a'
  on-primary: '#ffffff'
  primary-container: '#131b2e'
  on-primary-container: '#7c839b'
  inverse-primary: '#bec6e0'
  secondary: '#10b981'
  on-secondary: '#ffffff'
  secondary-container: '#6cf8bb'
  on-secondary-container: '#00714d'
  tertiary: '#f43f5e'
  on-tertiary: '#ffffff'
  tertiary-container: '#40000d'
  on-tertiary-container: '#f23d5c'
  neutral: '#64748b'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae2fd'
  primary-fixed-dim: '#bec6e0'
  on-primary-fixed: '#131b2e'
  on-primary-fixed-variant: '#3f465c'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffdadb'
  tertiary-fixed-dim: '#ffb2b7'
  on-tertiary-fixed: '#40000d'
  on-tertiary-fixed-variant: '#92002a'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.03em
  headline-xl-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.025em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 34px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 30px
    letterSpacing: -0.02em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  amount-display:
    fontFamily: Plus Jakarta Sans
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.03em
  amount-metric:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 26px
    letterSpacing: -0.02em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: -0.01em
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0em
  body-md-medium:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: -0.005em
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.03em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  space-2xs: 0.25rem
  space-xs: 0.5rem
  space-sm: 0.75rem
  space-md: 1rem
  space-lg: 1.25rem
  space-xl: 1.5rem
  space-2xl: 2rem
  space-3xl: 2.5rem
  margin-screen-mobile: 1.25rem
  gutter-card: 0.75rem
---

# ExpenseFlow Design System Specification

> **Project Source:** Stitch MCP (`projects/4264470475102559508`)  
> **Theme:** Modern FinTech Expense Experience  
> **Color Mode:** Light Mode Foundation (with Dark Glassmorphism Parity)  
> **Headline Font:** Plus Jakarta Sans  
> **Body / Data Font:** Inter  

---

## 1. Brand & Aesthetic Principles

This design system targets modern mobile and web users who demand financial agency, speed, and friction-free tracking. The emotional tone is deliberate, calm, and confidence-inspiring—countering financial anxiety through generous whitespace, high-contrast typography, and unmistakable directional indicators.

### Key Characteristics
- **Modern FinTech Minimalism:** Crisp white active cards floating over a soft cool neutral canvas.
- **Directional Color Semantics:** Color is functional, never purely decorative. Emerald is reserved exclusively for inflow/savings; Coral Rose is reserved strictly for outflow/alerts.
- **Micro-Borders & Tactile Layering:** 1px subtle borders combined with diffused ambient shadows instead of heavy, muddy drops.
- **Mobile-First Android Ergonomics:** Generous touch targets, rounded corners (12px–24px), and comfortable one-handed thumb interaction zones.

---

## 2. Color Palette & Tokens

### Core Semantic Colors

| Token Name | Hex Code | Role & Usage |
| :--- | :--- | :--- |
| **Primary** | `#0F172A` | Deep Slate Navy: Structural anchor, high-emphasis headings, key balance figures, primary buttons. |
| **Secondary** | `#10B981` | Vivid Emerald: Positive financial flow, income deposits, surplus targets, savings progress. |
| **Tertiary** | `#F43F5E` | Warm Coral Rose: Outflow, expense items, overspending warnings, critical pacing alerts. |
| **Neutral** | `#64748B` | Slate Muted: Auxiliary labels, inactive icons, timestamps, category subtitles. |
| **Error** | `#BA1A1A` | Validation errors, input failure states, system rejection messages. |

### Surface Hierarchy & Containers

| Surface Token | Hex Code | Role & Application |
| :--- | :--- | :--- |
| `background` / `surface` | `#F8F9FF` | Soft cool app canvas background; reduces screen glare. |
| `surface-container-lowest` | `#FFFFFF` | Pristine foreground card containers, modal cards, active sheets. |
| `surface-container-low` | `#EFF4FF` | Subtle nested group containers, table headers. |
| `surface-container` | `#E5EEFF` | Neutral metric panels, secondary container fills. |
| `surface-container-high` | `#DCE9FF` | Hover states, selected list items, toggle containers. |
| `surface-container-highest` | `#D3E4FE` | Segmented controls, active tab indicators, chip backdrops. |
| `outline` | `#76777D` | High-contrast component borders and divider strokes. |
| `outline-variant` | `#C6C6CD` | Subtle 1px dividers between transaction items. |

### Semantic Status Pills & Tints

- **Income Badge:**
  - Background: `#ECFDF5` (Emerald Tint)
  - Text: `#047857` or `#065F46` (Deep Emerald)
  - Icon: `↑` Upward micro-arrow
- **Expense Badge:**
  - Background: `#FFF1F2` (Coral Tint)
  - Text: `#BE123C` or `#9F1239` (Deep Coral)
  - Icon: `↓` Downward micro-arrow
- **Neutral Metric Badge:**
  - Background: `#F1F5F9` (Light Slate Tint)
  - Text: `#475569` (Slate Dark)

---

## 3. Typography System

The typography is built around two complementary typefaces:
- **Plus Jakarta Sans**: Bold, geometric, and modern for headlines, aggregate amounts, and brand identity.
- **Inter**: Neutral, highly legible at micro-sizes for body text, data points, transaction items, and form fields.

### Typographic Scale

| Token | Font Family | Size | Weight | Line Height | Tracking | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `headline-xl` | Plus Jakarta Sans | 40px | 700 (Bold) | 48px | -0.03em | Primary web hero balance display |
| `headline-xl-mobile`| Plus Jakarta Sans | 32px | 700 (Bold) | 38px | -0.025em| Hero balance display on mobile screens |
| `amount-display` | Plus Jakarta Sans | 36px | 700 (Bold) | 40px | -0.03em | Primary transaction/account balance amounts |
| `headline-lg` | Plus Jakarta Sans | 28px | 600 (SemiBold)| 34px | -0.02em | Section headers, card titles (Desktop) |
| `headline-lg-mobile`| Plus Jakarta Sans | 24px | 600 (SemiBold)| 30px | -0.02em | Section headers, modal sheet titles (Mobile)|
| `amount-metric` | Inter | 20px | 600 (SemiBold)| 26px | -0.02em | Secondary balance metrics, breakdown figures|
| `headline-sm` | Plus Jakarta Sans | 18px | 600 (SemiBold)| 24px | -0.01em | Sub-card headers, category headers |
| `body-lg` | Inter | 16px | 400 (Regular) | 24px | -0.01em | Primary reading text, instructions |
| `body-md-medium` | Inter | 14px | 500 (Medium) | 20px | -0.005em| Transaction titles, form labels, buttons |
| `body-md` | Inter | 14px | 400 (Regular) | 20px | 0.00em | Transaction timestamps, secondary subtitles |
| `label-md` | Inter | 12px | 600 (SemiBold)| 16px | +0.02em | Category chips, filter pill labels |
| `label-sm` | Inter | 11px | 600 (SemiBold)| 14px | +0.03em | Micro-badges, pacing tags, system flags |

### Financial Formatting Rule
When rendering numbers, currency figures, and transaction feeds, enable **tabular figures** (`font-variant-numeric: tabular-nums`) so decimal points and digits align precisely across vertical lists.

---

## 4. Spacing, Shapes & Corner Radii

Built upon an **8pt base grid** (with a 4pt micro-grid for badges and compact alignments):

### Spacing Scale
- `space-2xs`: `0.25rem` (4px)
- `space-xs`: `0.5rem` (8px)
- `space-sm`: `0.75rem` (12px)
- `space-md`: `1.0rem` (16px)
- `space-lg`: `1.25rem` (20px)
- `space-xl`: `1.5rem` (24px)
- `space-2xl`: `2.0rem` (32px)
- `space-3xl`: `2.5rem` (40px)
- `margin-screen-mobile`: `1.25rem` (20px)
- `gutter-card`: `0.75rem` (12px)

### Corner Radii
- `sm`: `0.25rem` (4px) — micro-badges
- `DEFAULT`: `0.5rem` (8px) — nested controls
- `md`: `0.75rem` (12px) — standard buttons, form inputs
- `lg`: `1.0rem` (16px) — standard transaction cards, dialogs
- `xl`: `1.5rem` (24px) — hero summary balance cards, bottom sheets
- `full`: `9999px` — pills, badges, floating action buttons

---

## 5. Elevation & Tactile Layering

| Elevation Level | Surface Color | Border | Shadow Specification | Usage |
| :--- | :--- | :--- | :--- | :--- |
| **Elevation 0** | `#F8F9FF` | None | None | Base background canvas |
| **Elevation 1** | `#FFFFFF` | `1px solid #E2E8F0` | `0px 1px 3px rgba(15,23,42,0.04), 0px 4px 12px rgba(15,23,42,0.02)` | Resting cards, transaction list cards |
| **Elevation 2** | `#FFFFFF` | `1px solid #CBD5E1` | `0px 4px 6px -1px rgba(15,23,42,0.06), 0px 10px 24px -3px rgba(15,23,42,0.04)` | Pressed states, dropdown menus, filter sheets |
| **Elevation 3** | `#FFFFFF` / Glass | `1px solid rgba(226,232,240,0.8)` | `0px 12px 32px -4px rgba(15,23,42,0.08), 0px 4px 12px -2px rgba(15,23,42,0.04)` | Floating bottom nav, FAB, modal bottom sheets |

---

## 6. Core Component Patterns

### 1. Hero Balance Card
- Surface: `#FFFFFF`, `1.5rem` (24px) padding, `rounded-3xl` (24px radius), `1px solid #E2E8F0`.
- Net Balance: `headline-xl` (`#0F172A`) with negative letter tracking.
- Trend Indicator: Inline status pill badge (`+12.4% vs last month`).
- Nested Metrics: Side-by-side Total Income (`#10B981`) and Total Expense (`#F43F5E`) in `#F8F9FF` sub-containers (`rounded-2xl`).

### 2. Transaction List Card
- Surface: `#FFFFFF`, `rounded-2xl` (16px radius).
- Item Row: 40px × 40px `rounded-xl` category icon container with soft pastel tint.
- Text: Merchant / Category in `body-md-medium` (`#0F172A`), subtitle in `body-md` (`#64748B`).
- Amount: Right-aligned tabular text (`body-md-medium` or `amount-metric`). Expenses lead with `-`, income with `+`.
- Separators: 1px divider in `#F1F5F9`.

### 3. Action Buttons
- **Primary Button:** Height 48px–52px. Background `#0F172A`, text `#FFFFFF` (`body-md-medium`), `rounded-xl`.
- **Secondary / Ghost:** Height 44px–48px. Background `#F8FAFC`, border `1px solid #E2E8F0`, text `#0F172A`, `rounded-xl`.
- **Quick-Add FAB:** Height 56px, `rounded-full`, background `#0F172A`, elevated shadow.

### 4. Input Fields
- Height 52px, background `#F8FAFC`, border `1px solid #E2E8F0`, `rounded-xl`, padding `0 16px`.
- Active focus state: Background `#FFFFFF`, border `1.5px solid #0F172A`.
- Amount Input: Large 36px font (`amount-display`) with anchored currency sign (`#64748B`).

---

## 7. Stitch Project Screen References

The following screens are registered in the Stitch project (`projects/4264470475102559508`):

1. **Dashboard - FlowExpense**: `screens/6d7b67d6adab4ba8b91a7f7a4f83501e`
   - Hero balance display, quick transaction feed, monthly trend radar.
2. **Analytics & Budgets**: `screens/14fb7176ac234b9085394a6cc1f09da1`
   - Category budget limit pacing, 50/30/20 breakdown, spending surges.
3. **Transactions History**: `screens/f687379a83864055b33f965ac3f0a0ce`
   - Filter chips, paginated transaction lists, date grouping.
4. **Quick Add Expense**: `screens/4e148d035f2342c0bd2b39059c0cab37`
   - Numeric keypad input, category selector grid, payment method tags.
5. **FlowPay Expense Logo**: `screens/e22861f78b3d419a850bdf5bfbe0d966`
   - Official brand mark and application icon.
