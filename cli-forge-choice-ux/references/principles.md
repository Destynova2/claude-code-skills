# Choice UX Principles

This reference supports `cli-forge-choice-ux`. Load it when a task needs detailed audit criteria, numeric heuristics, or pattern decisions.

## Scorecard

Rate each 0-10. A production flow should score 8+ on all mandatory dimensions.

| Dimension | 0-3 | 4-7 | 8-10 |
|-----------|-----|-----|------|
| Decision Load | Many equal choices, no recommendation | Grouped, but still noisy | Clear default/recommendation, advanced hidden |
| Field Friction | Asks for everything upfront | Some deferral/prefill | Only asks what is required now |
| CTA Clarity | Multiple competing primaries | Primary visible but diluted | One dominant primary per region |
| Error Prevention | Errors after submit only | Some inline checks | Invalid states prevented early |
| Feedback & State | Silent waits, unclear saves | Partial indicators | Immediate feedback, progress, recovery |
| Trust & Reassurance | Hidden costs/risks | Some reassurance | Price, privacy, security, next step explicit |
| Accessibility | Mouse-only or unlabeled | Mostly usable | Semantic, labeled, focusable, keyboard complete |
| Lifecycle Consistency | Create/edit/delete feel unrelated | Some reuse | Same grammar, prefill, diff, recap, recovery |

## Core Laws

### Less Is More, More Is Less

Minimalism is not visual emptiness. It means every visible element competes for attention and must earn its place. Remove:
- Decorative elements that do not change understanding or confidence.
- Secondary CTAs near the main commit action.
- Optional fields in the first pass.
- Advanced settings from the default view.
- Copy that explains the UI instead of making the UI self-evident.

Keep:
- Information needed to decide.
- Reassurance needed to commit.
- Recovery paths needed to feel safe.
- Feedback needed to trust the system.

### Hick's Law

Decision time increases with number and complexity of choices. UX application:
- Keep visible peer options around 3-5 where possible.
- If >5, group into categories, add search/filter, or recommend one.
- Use "Recommended", "Best for teams", or "Most flexible" only when truthful and useful.
- Do not split a single hard choice into many tiny screens if the accumulated interaction cost is worse.

### Fitts's Law

Targets are easier to acquire when they are larger and closer to the user's current focus.
- Primary CTA should be near the decision summary.
- Touch targets should be 44 px or larger when possible.
- Keep destructive actions away from primary commit actions.
- Make the whole label+control area clickable for checkboxes/radios.

### Miller / Chunking

Short-term memory is limited. Group fields and options by user mental model:
- Contact, delivery, payment, review.
- Basic, notifications, security, advanced.
- Plan, billing cycle, add-ons, confirmation.

Keep each group small enough to scan. Prefer 3-7 items per chunk; 5 is a good default.

### Jakob's Law

Users spend most of their time in other products. Use familiar patterns for high-stakes flows:
- Cart -> delivery -> payment -> review -> confirmation.
- Settings sections with search and clear save/undo behavior.
- Pricing cards with comparable rows and one recommended plan.
- Standard buttons, links, tabs, radios, checkboxes, selects.

Invent only where familiarity is not important or where the domain demands it.

### Tesler's Law

Complexity has to live somewhere. Move it away from the user:
- Derive defaults from context.
- Validate combinations automatically.
- Explain tradeoffs in option labels.
- Collapse advanced choices.
- Provide "use recommended settings".

Do not hide real consequences. Hidden complexity that surprises the user is worse than visible complexity.

## Flow Patterns

### Resource Lifecycle / VM Ordering

Use this for VMs, cloud resources, subscriptions, environments, projects, teams, and anything with create/edit/delete/clone/restore operations.

The principle: **same object, same mental model**. Users should recognize the resource no matter what they are doing to it.

#### Canonical Object Layout

Every operation should reuse the same sections when relevant:

1. Identity: name, owner, tags, environment.
2. Shape: size, CPU/RAM/storage, region, image/template.
3. Network/access: subnet, IP, firewall/security group, credentials.
4. Cost/limits: price estimate, quota impact, billing cycle.
5. Review: summary, diff, risks, primary action.
6. Result: status, next actions, rollback/retry path.

Create does not need all edit-only metadata, and delete does not need editable fields, but the summary vocabulary and section order should remain recognizable.

#### Operation Rules

| Operation | Required UX |
|-----------|-------------|
| Create | Start from safe default or template. Show live cost and recap before provision. |
| Edit/resize | Pre-fill current values. Show exact diff and downtime/restart impact. |
| Clone | Start from existing resource. Mark inherited values and force only required new identity fields. |
| Delete | Show the same resource summary, dependencies, backups, and irreversible consequences. Require typed name or strong confirmation only when undo is impossible. |
| Restore | Show source restore point, target state, data overwritten, and rollback path. |

#### Do

- Keep section names identical across create/edit/delete.
- Keep primary action labels explicit: "Create VM", "Resize VM", "Delete VM", "Restore Backup".
- Keep the summary panel in the same position.
- Preserve user input when navigating back or fixing validation.
- Return users to the exact resource/detail page after completion.
- If a change can be undone, prefer optimistic action + undo over heavy confirmation.
- If a change cannot be undone, use confirmation plus a final recap.

#### Avoid

- Create flow as a wizard, edit flow as a raw form, delete flow as an unrelated modal with different language.
- Asking for region/image/network again when editing size only.
- Hiding cost impact until after apply.
- "OK", "Submit", "Done", or "Confirm" for high-impact actions.
- Dropping users into a list after completion without showing what changed.

### Checkout / Order

Prefer:
- Guest checkout by default.
- Address autocomplete and correct input types.
- Single page or multi-step depending on field count; field count matters more than step count.
- Persistent order summary.
- Shipping/tax/fees disclosed before payment commit.
- Payment form matching the physical card mental model.
- Final review before payment.
- Clear success state with receipt/next step.

Avoid:
- Forced account creation before purchase.
- Promo code box visually dominating users without a code.
- Duplicate email/phone fields.
- Clearing forms on error.
- Disabling paste in payment or password fields.

### Pricing / Plan Selection

Prefer:
- 3 tiers unless a stronger business reason exists.
- One highlighted recommendation with reason.
- "Who this is for" per tier.
- Comparable rows, not vague feature prose.
- Monthly/annual toggle with clear savings and billing consequences.
- FAQ near objections: cancellation, limits, security, support, migration.

Avoid:
- Hiding usage limits until after selection.
- Multiple "recommended" badges.
- Feature names that only internal teams understand.
- Equal visual weight for all CTAs.

### Signup / Trial

Prefer:
- Value before account creation where possible.
- Email + password or SSO only as first step.
- Defer company, role, phone, team size unless required now.
- Real-time password guidance and show/hide control.
- No credit card required copy only if true.
- Clear explanation of verification and next step.

Avoid:
- Asking "how did you hear about us" before activation.
- CAPTCHA before any abuse signal, unless risk demands it.
- Email confirmation field.
- Terms checkbox if implicit consent is legally acceptable in the context.

### Onboarding / Setup

Prefer:
- One first-session goal.
- Product action over tutorial text.
- Demo data or templates to avoid blank slates.
- Checklist with 3-7 items ordered by value.
- "Skip for now" for non-critical personalization.
- Resume where user left off.

Avoid:
- Long tours before the user can act.
- Blocking setup questions that only help marketing segmentation.
- Empty dashboards with no first action.

### Settings / Configuration

Prefer:
- Search for settings.
- Group by user task, not database model.
- Inline edit for simple values.
- Recap/diff before applying risky changes.
- Undo, reset to default, or safe rollback.
- Advanced mode opt-in.

Avoid:
- Auto-saving destructive/risky settings without confirmation.
- Global save button far from changed fields without dirty-state indicators.
- Hiding whether a setting is inherited, default, or custom.

### Product Configurator

Prefer:
- Start from recommended presets.
- Show compatibility constraints immediately.
- Disable impossible combinations with reasons.
- Keep price/impact summary live.
- Let users compare configurations.
- Preserve progress if they go back.

Avoid:
- Letting users build invalid states and only failing at checkout.
- Overloading with all options at once.
- Hiding dependencies between choices.

## Technical Checklist

### Accessibility

- Icon-only buttons have accessible names.
- Inputs have visible labels or robust accessible labels.
- Forms use meaningful `name`, `autocomplete`, `type`, and `inputmode`.
- Buttons are buttons; navigation is links.
- Keyboard path can complete the flow.
- Focus state is visible.
- Async updates use appropriate status/live regions.
- Errors are close to fields and associated with them.
- Do not disable zoom.

### Feedback

- Hover, active, focus, selected, disabled, loading, success, and error states exist.
- Operations over 300 ms show progress.
- Save/apply operations explain whether changes are local, pending, or persisted.
- Destructive actions have confirmation or undo.

### Copy

- CTA says the outcome: "Save Billing Address", "Start Free Trial", "Review Order".
- Errors include a fix: "Enter a 5-digit ZIP code" beats "Invalid ZIP".
- Labels use user language, not internal implementation names.
- Help text appears next to the decision it supports.

### Layout

- Primary CTA is visible without searching.
- Long content wraps, truncates, or clamps intentionally.
- Flex/grid children can shrink (`min-width: 0` where needed).
- Mobile layout is single-column for forms.
- Related items are close; unrelated groups have larger gaps.

## Visual Math

Use math to create consistency, not mysticism.

| Use | Good default |
|-----|--------------|
| Spacing | 4 or 8 px base scale |
| Touch target | 44 px preferred, 24 px minimum for WCAG 2.2 constrained cases |
| Body text | 16 px minimum for forms on mobile |
| Line length | 45-75 characters |
| Type ratio | 1.2-1.333 between adjacent levels |
| Animation | 100-150 ms micro, 200-300 ms state, reduced-motion supported |
| Visible choices | 3-5 primary options before grouping/recommendation |

### Golden Ratio

The golden ratio can be used for composition experiments, image crops, or a type/spacing exploration, but it is not a usability proof. Do not choose a 1.618 layout if it creates:
- Poor responsive behavior.
- Weak CTA position.
- Awkward line lengths.
- Inaccessible target sizes.
- Bad information hierarchy.

For product interfaces, an 8 px grid, accessible targets, clear hierarchy, and user-tested flow beat golden-ratio decoration.

## Severity

| Severity | Meaning | Examples |
|----------|---------|----------|
| 4 Catastrophic | User cannot complete task or may suffer serious loss | Payment blocked, destructive save without recovery, inaccessible required control |
| 3 Major | Many users struggle or abandon | Hidden fees late, too many required fields, unclear plan differences |
| 2 Minor | Slows or annoys but workaround exists | Weak labels, poor empty state, redundant help text |
| 1 Cosmetic | Polish issue only | Slight spacing inconsistency, non-critical copy awkwardness |

Prioritize by user impact first, implementation effort second.
