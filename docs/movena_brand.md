# Movena Brand Guide

## The Personality

**A calm, capable care partner.** Movena helps people understand movement and stay
connected to care. It should feel attentive and credible, not like a hospital
administration system, a competitive fitness tracker, or an all-knowing AI.

**Brand line:** Move forward, together.

**Descriptor:** Clear movement insights. Connected care.

The promise is clarity about the next step, not a guaranteed recovery outcome.
Patients remain in control; therapists bring clinical judgment. Independent
patients are welcome and should never feel like incomplete accounts.

| Trait | In Practice | Avoid |
| --- | --- | --- |
| Clear | Name the action and its consequence | Vague labels and technical jargon |
| Considerate | Acknowledge effort without judgment | Shame, streak pressure, forced cheerfulness |
| Grounded | Explain uncertainty and clinician review | Diagnosis claims and AI authority |
| Encouraging | Offer a practical next step | Recovery promises and excessive celebration |

## Colour Roles

| Colour | Hex | Purpose |
| --- | --- | --- |
| Movement blue | `#245edb` | Primary actions and brand recognition |
| Care teal | `#07776f` | Support, connection, and completed actions |
| Graphite | `#202b33` | Wordmark, headings, and structural clarity |
| Cloud | `#f5f7f8` | Quiet workspace canvas |
| Blue tint | `#eaf0ff` | Selection and informational emphasis |
| Teal tint | `#e6f5f1` | Supported and positive states |
| Muted ink | `#5d6973` | Secondary text, never essential text at low opacity |
| Review amber | `#8a560c` | Caution or review needed, with a label |
| Error rose | `#b13f47` | Errors and destructive consequences, not decoration |

Let white/cloud surfaces dominate. Use graphite for structure, blue for action,
and teal as a supporting accent. Do not turn entire screens into blue panels.
Amber and rose are reserved for meaning, not brand embellishment. Never equate
a teal badge with medical clearance; it describes the labelled state only.

Dark mode uses charcoal surfaces, pale text, and lighter semantic foregrounds.
Primary buttons retain white text on blue; blue text on dark backgrounds uses
the separate lighter selection token. Always pair status colours with text or icons.

## Identity And UI

- Retain the existing blue/teal movement symbol. Pair it with the graphite Movena
  wordmark; reverse the wordmark to pale graphite in dark mode. Keep the symbol's
  aspect ratio and allow breathing room. Do not add gradients, badges or shadows.
- Use the bundled Inter family. Wordmark weight 700, headings 600-750, body 400-500.
  Sentence case, normal tracking, and short labels support everyday clinical work.
- Preserve the approved exercise-library composition and male illustrations.
  Illustration colour supports the palette but is not a clinical instruction.
- Use 6-8px control/card corners, restrained borders, familiar line icons, and
  visible keyboard focus. Keep layouts quiet rather than adding decorative panels.
- Charts must retain distinct series and textual legends. Never flatten clinical
  charts into a single brand colour or use branding to change a risk classification.

## Voice Examples

| Situation | Preferred | Avoid |
| --- | --- | --- |
| Upload failure | "Your video couldn't upload. Try again." | "Oops! Something went wrong!" |
| Incomplete session | "Your progress is saved. Continue when you're ready." | "You missed your goal." |
| Analysis uncertainty | "This recording needs a clearer side view." | "Your movement is incorrect." |
| Connection accepted | "Your care connection is active." | "Your recovery journey is unlocked!" |
| Independent patient | "Your exercises and progress remain available." | "You don't have a care plan yet!" |

Use these examples only where the underlying behavior is true. Do not soften
safety warnings, remove consent detail, or add clinical advice while editing tone.
Arabic copy should communicate the same intent naturally and use RTL layouts;
the Arabic brand line is maintained in the translation catalogue.

## Source Of Truth

Brand identity and palette: `frontend/src/config/brand.js`.
Theme tokens: `frontend/src/styles.css`. Shared component treatments:
`frontend/src/workspace.css`. Browser/install metadata stays aligned with the brand.
Regression tests check core text/background contrast and metadata consistency.
