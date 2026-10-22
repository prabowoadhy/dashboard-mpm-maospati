# Project instructions

## antislop

<!-- antislop:start -->
For UI, copy, people, mobile layout, or code comments work, load the `antislop`
skill and then the skill for the task from `.opencode/skills/`:

- UI / visual: `antislop-ui`
- Copy and text: `antislop-copywriting`
- People: `antislop-human`
- Mobile / responsive: `antislop-layoutmobile`
- Code comments: `antislop-code`

Before starting, follow the core's "Two Usage Modes" section in strict order:
explicit session instruction first, then global preference, then ask. A session
instruction always wins. For a resolved mode, say
`antislop active: <mode> (session override).` or
`antislop active: <mode> (global preference).` once before presenting findings
or making edits.

Only an explicit choice of antislop during or after selects a session mode. A
request to review, audit, or avoid file edits does not select a mode. If the
mode is unresolved, ask during/after and end the response.

Read `DESIGN.md` before changing the visual system. It is the project's design
direction, not a suggestion.
<!-- antislop:end -->
