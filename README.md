# English Learning App — Refactoring & Product Specification

## 1. Project Goal

Transform the existing `b1-b2-kelimeler-responsive.html` into a polished, reliable, mobile-first English-learning application that runs from **one self-contained HTML file**.

The result must be useful for sustained English study—not merely a vocabulary list. It should combine vocabulary learning, review, grammar, reading, listening, pronunciation support, writing practice, quizzes, progress tracking, and a coherent learning path while remaining usable on phones, tablets, and desktop computers.

This document is the implementation brief. Follow it as a product specification, engineering plan, and quality-assurance contract.

## 2. Non-Negotiable Constraints

1. **Single-file delivery:** The final application must run from one `index.html` (or one clearly named `.html` file).
2. **No build step:** Do not require npm, Node.js, a bundler, a framework, a server, a database, or a compilation step.
3. **Offline-first:** Core features must work when the HTML file is opened locally, without a network connection.
4. **Self-contained assets:** Prefer inline SVG, CSS, and embedded assets. If remote audio or external resources are offered, label them clearly as optional and provide a graceful fallback.
5. **No framework dependency:** Use semantic HTML, modern CSS, and plain JavaScript. Do not add React, Vue, jQuery, or a CSS framework.
6. **Preserve source content:** Do not silently delete, rewrite, renumber, or fabricate the existing vocabulary entries, translations, examples, pronunciation notes, or image assets. Treat the current HTML as the content source of truth. Any content corrections must be explicit and separately reviewable.
7. **English-learning product:** The user-facing learning interface should be in English by default, with Turkish translations and explanations available where pedagogically useful. Provide a clear language preference if both interface languages are supported.
8. **Real interactions only:** Every visible control must work. No decorative buttons, dead links, fake progress, or controls that look interactive but do nothing.
9. **Accessibility:** Support keyboard, touch, screen readers, zoom, reduced motion, visible focus, and adequate contrast.
10. **Do not claim testing that was not performed.** Report actual checks and remaining limitations honestly.

## 3. Audit the Existing HTML Before Editing

Read the entire source, including all script blocks and generated vocabulary markup, before implementing changes. Create an inventory of features and data first.

The current file appears to contain:
- A large vocabulary collection with embedded Base64 WebP images.
- Search by word and meaning.
- Learned/unlearned state and filters.
- Original, related-meaning, and alphabetical views.
- A vocabulary multiple-choice quiz.
- Grammar tense explanations and expandable examples.
- Progress persistence using `localStorage`.
- Extensive responsive CSS overrides.
- More than one layer of touch/click event handling.

### Known risk areas to investigate

- A very large HTML file with thousands of cards and embedded images can delay parsing, rendering, and interaction on lower-powered phones.
- The stylesheet has repeated and overlapping media queries and repeated declarations. Consolidate them into a deliberate responsive system rather than adding more overrides.
- The early-tap queue near the top of the document sets `window.__mobileInteractionsReady` to `false` and intercepts `touchend` and capture-phase `click` events. Verify whether it is ever switched to `true`, whether queued events are replayed, and whether the queue can prevent normal controls from receiving their clicks.
- A later script also synthesizes clicks from touch events and suppresses subsequent click events. Multiple competing touch/click systems can cause controls to appear unresponsive or actions to run twice. Replace these mechanisms with a single, standards-based interaction strategy.
- Vocabulary cards use both a clickable `figure` and a button to mark a word as learned. Avoid nested or duplicate interaction targets and make the intended action obvious.
- Some browsers restrict or partition `localStorage` for local files, private browsing, or embedded viewers. Storage failure must never crash the app.
- The page's current text and labels are largely Turkish even though the intended product is comprehensive English education. Design a consistent language and learning-level strategy.
- The current title and vocabulary focus suggest B1–B2, but the long-term product should support a structured path across levels without falsely labelling unverified content as CEFR-certified.

Do not assume these are the only defects. Inspect the source, identify root causes, and verify them with reproducible tests.

## 4. Required Engineering Workflow

Work in this order. Do not jump straight into cosmetic redesign.

### Phase A — Inventory and diagnosis

1. Inspect all HTML, CSS, JavaScript, vocabulary entries, embedded images, and any external references.
2. List every feature and its corresponding DOM elements, event handlers, state, and persistence mechanism.
3. Identify duplicate event listeners, global variables, event-order dependencies, race conditions, invalid markup, inaccessible controls, and CSS conflicts.
4. Reproduce the mobile interaction failure if possible. Use a small diagnostic test page or browser automation if available.
5. Record a concise root-cause report before changing the implementation.
6. Count and compare vocabulary entries before and after refactoring so that no content disappears unintentionally.

### Phase B — Establish a maintainable single-file architecture

Organize the HTML file into clearly commented sections:

1. Document metadata and theme settings.
2. Design tokens and global styles.
3. Semantic page structure and navigation.
4. Learning views and reusable templates.
5. Embedded content data.
6. Application state and storage adapter.
7. Feature modules / functions.
8. One initialization entry point.
9. Optional diagnostics and a short in-file version marker.

Use small, named functions with clear responsibilities. Avoid one enormous initialization function, unexplained global state, duplicated handlers, and broad CSS overrides.

Keep data separate from presentation where feasible. For a major refactor, convert existing card markup to a normalized in-memory vocabulary data structure only if every existing field and image can be preserved and validated. Do not manually retype thousands of entries.

### Phase C — Implement and test incrementally

Implement one feature at a time. After each feature:
- Check the browser console for errors.
- Test desktop and mobile interaction.
- Test keyboard access.
- Test empty, invalid, and missing data.
- Test storage failure.
- Confirm existing vocabulary content remains intact.

Do not declare the project complete until the acceptance checklist in this document has been checked.

## 5. Product Experience and Visual Design

Create a modern, calm, focused study environment. The visual design should feel like a carefully designed learning product, not a long page of unrelated cards.

### Design direction

- Use a consistent design system with spacing, typography, border radii, shadows, surfaces, and color tokens.
- Prefer a restrained palette: a deep blue or charcoal foundation, a clear primary accent, neutral backgrounds, and semantic success/error colors.
- Use color with sufficient contrast; never rely on color alone to communicate correctness or learning status.
- Establish clear hierarchy: page title, learning goal, section title, content, supporting details, and actions.
- Keep cards visually consistent. Avoid excessive gradients, decorative effects, tiny labels, or unnecessary animations.
- Use a small number of consistent icons. Inline SVG is acceptable; emoji should not be the only iconography.
- Include clear hover, focus, pressed, selected, disabled, success, and error states.
- Support light and dark themes if feasible, with a working theme toggle and persisted preference. If a theme toggle is shown, it must actually change the theme.
- Respect `prefers-reduced-motion`.
- Prevent horizontal overflow at narrow widths and high browser zoom.
- Avoid layout shifts when images load or content changes.

### Responsive layout

Design mobile-first, then enhance for larger screens.

- **Small phones (320–374 CSS px):** no horizontal page scrolling; controls remain legible and tappable.
- **Phones (375–599 px):** one-column cards and full-width quiz answers where appropriate.
- **Tablets (600–899 px):** flexible two-column layouts where useful.
- **Desktop (900 px and above):** balanced content width, readable line length, and multi-column layouts when they improve learning.
- Handle safe-area insets on supported mobile devices.
- Do not make essential actions dependent on hover.
- Avoid fixed overlays that cover controls or content. If a modal is used, provide a close button, Escape-key support, focus management, and scroll handling.

## 6. Mobile Interaction Reliability — Critical Priority

The reported issue is that buttons do not respond on phones. Treat this as a functional defect, not a styling problem.

### Required approach

1. Use native `<button type="button">` elements for actions and native `<details>/<summary>` for simple disclosures where appropriate.
2. Use one primary event model: standard `click` events work for mouse, touch, and keyboard activation on native buttons. Do not synthesize clicks from `touchend` unless a demonstrated browser bug requires it and a narrowly scoped, tested workaround is documented.
3. Remove competing document-level touch/click interception and any early-tap queue unless testing proves it is necessary. Never call `preventDefault()` or `stopImmediatePropagation()` globally for ordinary controls without a narrowly justified reason.
4. Use event delegation only when it is simple and reliable. Resolve the intended action using `event.target.closest(...)`, confirm the target exists, and ensure the handler cannot act on unrelated controls.
5. Do not attach click handlers to non-interactive elements unless they are deliberately given complete keyboard and accessibility behavior. Prefer native buttons.
6. Do not use `pointer-events: none` on interactive elements or their ancestors. Audit stacking contexts, pseudo-elements, overlays, z-index, and invisible elements that might intercept taps.
7. Do not depend on `:hover` to reveal a button or make it usable.
8. Use touch targets of approximately **44 × 44 CSS pixels or larger**, with enough spacing to prevent accidental activation.
9. Prevent duplicate actions and duplicate score updates. A single physical tap must cause exactly one action.
10. Keep handlers fast. A tap must not trigger a full expensive DOM rebuild unless necessary.
11. Never require a double tap to activate an ordinary button.
12. Test on actual mobile browsers when possible, not only desktop device emulation.

### Mobile interaction regression tests

Test each of these on a phone or a mobile browser emulator:
- Start quiz.
- Choose each quiz answer.
- Move to the next question.
- Search using the on-screen keyboard.
- Switch all/unlearned/learned filters.
- Change vocabulary sort/view.
- Mark a word learned and unlearn it.
- Open and close grammar sections.
- Change navigation tabs or learning modes.
- Open and close any modal or menu.
- Change theme and settings.
- Restore saved progress after reload.
- Scroll normally over cards without accidentally marking words learned.
- Tap rapidly more than once and verify there are no duplicate actions.

## 7. English Learning Features

Implement a coherent core first. If time or space is limited, prioritize correctness and usability over a long list of unfinished features.

### 7.1 Learning dashboard

- Show the learner's current level or selected study path.
- Show meaningful statistics: words reviewed, words learned, review due, quiz accuracy, and study streak only if the required data is actually tracked.
- Provide a clear “Continue learning” action.
- Show progress derived from real saved state; do not invent or hard-code progress.

### 7.2 Vocabulary

Each vocabulary item should support the fields available in the source:
- Stable ID.
- English word or phrase.
- Part of speech, if known.
- Turkish meaning or translation.
- Pronunciation guidance and/or IPA only when verified.
- Example sentence.
- Example translation, if available.
- Existing illustration or image.
- Level/category/tags only where supported by reliable data.
- Learning status and review metadata.

Features:
- Search English terms and Turkish meanings, case-insensitively.
- Normalize text carefully, including Turkish dotted/dotless I, without corrupting displayed text.
- Filter by learning status, level, topic, or part of speech where data exists.
- Sort alphabetically and by the original order; related-word groups must be based on explicit, understandable mappings.
- Provide a clear empty-search state and a way to reset filters.
- Let learners mark/unmark words as learned with visible state and accessible labels.
- Make the whole card non-clickable unless card activation has a single, unambiguous purpose.
- Preserve image aspect ratio, provide meaningful `alt` text, and show a graceful fallback if an image fails.
- Do not render huge lists in a way that blocks all interaction. Consider rendering a manageable subset or progressive batches while retaining search across the complete dataset.

### 7.3 Spaced review

Add a lightweight review system only if it can be implemented honestly and reliably:
- “Again,” “Hard,” “Good,” and “Easy” actions, or a simpler “Review again / Know it” system.
- Store the next review time and review history locally.
- Explain that scheduling is a study aid, not a scientific assessment of proficiency.
- Use stable vocabulary IDs so progress survives sorting or content reordering.
- Provide a reset/export option.
- Never mark a word learned simply because its card was opened.

### 7.4 Quizzes

- Multiple-choice vocabulary questions with one correct answer.
- Distractors must be different from the correct answer and, where possible, drawn from comparable data.
- Avoid duplicate answer options when the dataset is small.
- Shuffle questions and options fairly.
- Give immediate feedback with a short explanation where useful.
- Provide clear keyboard and screen-reader feedback.
- Track correct answers and attempts consistently.
- Disable or otherwise prevent answering the same question multiple times.
- Make next/restart actions work.
- Show a final result and a way to practice missed words.
- Handle insufficient valid vocabulary gracefully.

Optional quiz modes:
- English → Turkish.
- Turkish → English.
- Fill in the blank.
- Example-sentence comprehension.
- Spelling recall.
- Mixed review.

### 7.5 Grammar

Develop a structured grammar guide with:
- Clear explanations.
- Positive, negative, and question forms.
- Correct examples and translations.
- Common mistakes.
- Short exercises with feedback.

Start with common tenses and expand to articles, prepositions, modals, conditionals, passive voice, reported speech, relative clauses, and other topics only when quality content is available. Do not present an incomplete list as a complete grammar course.

### 7.6 Reading

Provide graded reading passages with:
- A level label supported by the content.
- A title and readable paragraph layout.
- Optional Turkish translation or line-by-line support.
- Vocabulary highlighting that does not disrupt reading.
- Comprehension questions with feedback.
- A way to save difficult words.

Do not generate fake source citations or imply that unreviewed text is professionally level-assessed.

### 7.7 Listening and pronunciation

- Listening exercises should have a clear play/pause state, replay, progress, transcript, and comprehension questions when audio is available.
- Browser speech synthesis may be offered as an optional pronunciation aid, but clearly identify it as device/browser-generated speech. Voice availability varies.
- Check for `speechSynthesis` and handle unsupported browsers without errors.
- Do not autoplay audio.
- Explain that offline speech synthesis may be unavailable or use a different voice on different devices.
- Do not make an external audio URL a requirement for core app operation.
- If audio is absent, show an honest placeholder and a path to add audio later; do not display a fake player.

### 7.8 Writing

- Provide a writing practice area with prompts by level or topic.
- Include a word counter and clear/reset action with confirmation if text would be lost.
- Offer a checklist or rubric for grammar, clarity, vocabulary, and task completion.
- Do not claim to perform AI grammar correction without a connected model or service. For offline use, provide only transparent rule-based hints and explain their limitations.
- Do not send user writing to an external service without explicit consent.

### 7.9 Study settings and data portability

- Let users choose their interface language and theme if those controls are implemented.
- Provide export of learning progress as JSON.
- Provide import with schema validation, clear error messages, and confirmation before overwriting progress.
- Provide a “Reset progress” action with explicit confirmation.
- Keep vocabulary content separate from learner progress so a content update does not erase learning history.
- Do not store passwords, secrets, or unnecessary personal information.

## 8. Persistence and State Management

Create one small storage adapter instead of scattering `localStorage` calls across handlers.

Requirements:
- Wrap reads/writes in `try/catch`.
- If storage is blocked or quota is exceeded, keep the app functional in memory and show a non-blocking explanation when appropriate.
- Validate parsed JSON and handle malformed or outdated saved data.
- Version the saved schema, e.g. `schemaVersion: 1`.
- Use stable word IDs, not card positions or DOM order.
- Separate vocabulary content from user state.
- Save only meaningful changes; do not write the entire progress state repeatedly during initial rendering.
- Avoid data loss if a storage write fails.
- Explain that local progress can be cleared by the browser and is not automatically synced between devices.
- Never claim cloud backup or cross-device synchronization unless implemented.

## 9. Performance

The source contains a large number of cards and inline image bytes, so performance is a core requirement.

- Avoid unnecessary DOM creation for every card on every keystroke.
- Debounce search only if needed, and keep it responsive.
- Keep all vocabulary searchable even if only a subset is currently rendered.
- Consider rendering in batches or using a small virtualized list if profiling proves it necessary.
- Avoid duplicating large Base64 image strings in JavaScript objects if they already exist in markup.
- Preserve `loading="lazy"` for non-critical images where appropriate.
- Provide explicit image dimensions or aspect ratios to reduce layout shifts.
- Keep event handlers lightweight.
- Avoid repeatedly sorting or scanning the entire dataset for every unrelated UI update.
- Measure performance on a representative phone or constrained device when possible.
- Do not sacrifice offline behavior or data integrity for a benchmark.

## 10. Accessibility Requirements

- Use semantic landmarks: `header`, `nav`, `main`, `section`, and `footer` where appropriate.
- Maintain a logical heading hierarchy.
- Give every form field an accessible name.
- Use native buttons for actions and native controls where possible.
- Ensure every interactive element is keyboard-operable.
- Provide clearly visible `:focus-visible` styles.
- Keep status and quiz feedback accessible through restrained `aria-live` regions.
- Use `aria-pressed` only for toggle buttons whose pressed state is real and updated.
- Keep labels and instructions understandable without color or icon interpretation.
- Ensure dialogs, if any, manage focus and return focus on close.
- Do not add ARIA roles that conflict with native semantics.
- Verify text contrast and usable layout at 200% zoom.
- Respect reduced-motion preferences.

## 11. Code Quality Rules

- Use descriptive names and consistent formatting.
- Prefer `const`; use `let` only for reassigned variables.
- Avoid unnecessary globals and implicit dependencies between script blocks.
- Initialize after the relevant DOM exists. Since scripts may be placed at the end of the body, use a clear, predictable initialization strategy.
- Add event listeners once.
- Keep DOM queries and data operations readable.
- Check elements before using them when a feature is optional.
- Use `textContent` for user-generated or plain-text content; do not interpolate untrusted content into `innerHTML`.
- If templates use `innerHTML`, only interpolate properly escaped or trusted static content.
- Avoid inline event attributes such as `onclick`.
- Avoid broad `preventDefault()` and `stopPropagation()` calls.
- Do not suppress console errors to make tests look clean.
- Do not add unnecessary third-party scripts or trackers.
- Comment on non-obvious decisions, not every line.
- Use a small number of well-named CSS sections and media queries.
- Remove dead code, duplicate event systems, and unused CSS after verifying that they are not needed.
- Keep a short change log in the README or in the project notes when major changes are made.

## 12. Testing and Acceptance Checklist

The work is complete only when the relevant items below pass. Record what was actually tested and on which browser/device.

### Functionality
- [ ] Every visible button and interactive control performs its advertised action.
- [ ] No control requires double-tapping.
- [ ] No single tap triggers an action twice.
- [ ] Search works for English words and Turkish meanings.
- [ ] Filters and sorting work together without losing card state.
- [ ] Learned status toggles correctly and persists when storage is available.
- [ ] Quiz starts, answers, scores, advances, restarts, and ends correctly.
- [ ] Grammar disclosures open and close with mouse, touch, and keyboard.
- [ ] Import/export/reset controls work if present.
- [ ] No fake or unfinished controls are shown as functional.

### Mobile
- [ ] Test at 320, 360, 390, and 430 CSS px viewport widths.
- [ ] No horizontal overflow.
- [ ] All targets are comfortably tappable.
- [ ] Touch scrolling does not accidentally activate cards.
- [ ] On-screen keyboard does not hide essential search or writing controls.
- [ ] Tested on at least one mobile browser or credible mobile emulator.
- [ ] Repeated rapid taps do not create duplicate state changes.

### Reliability
- [ ] No uncaught JavaScript errors on load or during normal use.
- [ ] Works with `localStorage` unavailable.
- [ ] Handles invalid stored JSON.
- [ ] Handles missing images and empty search results.
- [ ] Core vocabulary and quizzes work offline.
- [ ] Reload preserves state when storage is available.
- [ ] Existing vocabulary entries and their important fields have been preserved.
- [ ] No external dependency is silently required for core functionality.

### Accessibility and design
- [ ] Keyboard-only navigation works.
- [ ] Focus is visible and not obscured.
- [ ] Text remains readable at 200% zoom.
- [ ] Contrast is adequate.
- [ ] Screen-reader labels and quiz feedback are meaningful.
- [ ] Reduced-motion preference is respected.
- [ ] Layout and visual language are consistent across all views.

### Delivery
- [ ] One standalone HTML file opens directly in a modern browser.
- [ ] README documents what works, limitations, and how to extend the content.
- [ ] Test results distinguish automated checks from manual checks.
- [ ] No unverified claims such as “fully tested on all devices.”

## 13. Suggested Implementation Priorities

**P0 — Fix reliability first**
1. Identify and remove the cause of mobile taps being swallowed.
2. Eliminate conflicting touch/click interception.
3. Ensure all current controls work.
4. Handle storage errors.
5. Preserve all current vocabulary content and progress where feasible.

**P1 — Refactor foundation**
1. Consolidate CSS and responsive breakpoints.
2. Introduce clear state and storage boundaries.
3. Improve semantics and keyboard accessibility.
4. Improve initial load and search performance.
5. Establish the visual design system.

**P2 — Make it a coherent study tool**
1. Improve dashboard and navigation.
2. Improve vocabulary review and quiz modes.
3. Organize grammar content.
4. Add reading practice.
5. Add listening/pronunciation support.
6. Add writing practice.

**P3 — Polish and verify**
1. Theme and language settings.
2. Progress export/import/reset.
3. Edge-case handling.
4. Cross-browser regression tests.
5. Final content and accessibility review.

## 14. Master Prompt for an AI Coding Agent

Copy the following prompt into the coding agent that will modify the HTML file. Give it the current HTML file as input.

---

### ROLE

You are a senior front-end engineer, accessibility specialist, mobile web debugging expert, UI/UX designer, and English-learning product architect. You are responsible for refactoring an existing large single-file HTML English-learning app into a polished, reliable, offline-first learning environment.

### MISSION

Inspect the supplied `b1-b2-kelimeler-responsive.html` in full, diagnose its real defects, and deliver a production-minded single-file English-learning application. The final user-facing application must run by opening one HTML file directly in a modern browser.

### FIRST: INSPECT, DO NOT GUESS

Before changing code:
1. Read every script block and inspect the relevant HTML and CSS.
2. Map each visible control to the JavaScript handler and state it uses.
3. Diagnose why mobile taps may be intercepted or lost. In particular, inspect the early `queueMobileTap` capture listeners and the later synthetic-touch-click logic. Verify the readiness flag, event ordering, replay logic, and duplicate-event prevention.
4. Identify duplicate CSS rules, conflicting media queries, invalid semantics, storage assumptions, performance bottlenecks, and any broken interactions.
5. Count vocabulary entries and inspect the fields used by cards.
6. Write a concise root-cause summary before implementing the fix.

Do not invent a cause. Confirm it from the code and tests. If the cause cannot be reproduced, explain the evidence and test the plausible failure paths.

### HARD CONSTRAINTS

- Deliver one standalone HTML file with inline CSS and JavaScript.
- No build tools, package installation, framework, server, database, or required external dependency.
- Core vocabulary study and quiz functionality must work offline.
- Preserve existing vocabulary, translations, examples, pronunciation notes, and embedded images. Do not silently remove or fabricate content.
- Do not retype the entire dataset manually. Transform existing content programmatically or preserve it safely.
- Do not claim features are implemented unless they work.
- Every visible control must have a real, tested behavior.
- Do not replace one broken touch workaround with another untested global event hack.
- Prefer native buttons and standard click events. Remove conflicting global touch/click interception unless a narrow, proven exception is necessary.
- Make storage optional and fault-tolerant.
- Do not add trackers or send learner data to external services.
- Keep code understandable and maintainable despite the single-file constraint.

### DESIGN

Build a coherent, modern, calm, mobile-first interface with:
- Consistent color, spacing, typography, radius, and elevation tokens.
- Clear navigation and learning hierarchy.
- Readable vocabulary cards and focused study panels.
- Responsive layouts for small phones, larger phones, tablets, and desktop.
- Clear empty, loading, success, error, selected, pressed, and focus states.
- Touch targets at least about 44 CSS pixels in each dimension.
- No horizontal overflow at 320 CSS pixels.
- Keyboard and screen-reader support.
- Light/dark mode only if both themes work fully.
- Reduced-motion support and adequate contrast.
- No essential hover-only interaction.

Avoid visual clutter and excessive effects. Prioritize legibility and focus.

### LEARNING EXPERIENCE

Build a coherent English-learning foundation:
1. Vocabulary search by English word and Turkish meaning.
2. Learned/unlearned filters and reliable sorting.
3. Persistent learned status when browser storage permits.
4. A working multiple-choice quiz with unique options, immediate feedback, correct scoring, next/restart behavior, and a final result.
5. Grammar explanations with positive, negative, and question forms.
6. A clear foundation for reading, listening/pronunciation, and writing practice. Implement these only to the extent that accurate content and reliable behavior can be provided; never create fake audio or claim AI correction without a model.
7. Honest progress indicators derived from real activity.
8. Export/import/reset only if fully implemented and validated.

Use English as the default interface language where practical, while preserving Turkish translations as learning support. Do not falsely claim that all content has been professionally CEFR-graded.

### MOBILE BUG RULES

- Use native `<button type="button">` for actions.
- Use standard click events for touch, mouse, and keyboard activation.
- Avoid global `touchend` handlers that call `preventDefault()` or generate synthetic clicks.
- Do not suppress subsequent clicks globally.
- Do not let invisible overlays, pseudo-elements, stacking contexts, or `pointer-events` rules block controls.
- Do not use clickable figures as the only action mechanism; prefer a clearly labelled button.
- A single tap must trigger exactly one action.
- Normal scrolling must not accidentally mark words as learned.
- Do not require double-tapping.
- Keep event handlers light and avoid full-list rerenders where unnecessary.

### DATA AND STORAGE

- Use stable word IDs.
- Separate vocabulary data from learner state.
- Wrap storage reads and writes in `try/catch`.
- Validate stored data and handle schema changes.
- Keep the app usable in memory if storage is blocked.
- Preserve data when the user changes sorting or filters.
- Do not repeatedly save unchanged state.
- Provide a clear explanation that local progress may not sync across devices.

### REQUIRED WORK PROCESS

1. Inspect the full file.
2. Report the confirmed defects and a concise plan.
3. Fix mobile interactions first.
4. Refactor CSS and state/event handling.
5. Improve visual design and responsive layout.
6. Implement or polish learning features.
7. Run functional and responsive checks.
8. Compare vocabulary counts and essential fields against the source.
9. Report exactly what changed, what was tested, and what remains incomplete.

Do not stop after writing a plan if you have the tools to edit and test the file. Complete the implementation.

### REQUIRED TESTS

Test:
- Start quiz, answer a question, continue, finish, and restart.
- Search English and Turkish text.
- Change filters and sort modes.
- Mark and unmark a learned word.
- Open and close grammar disclosures.
- Reload and verify saved state.
- Run with storage blocked or malformed.
- Tap controls rapidly and ensure no duplicate actions.
- Scroll on top of cards without triggering accidental activation.
- Check widths 320, 360, 390, 430, 768, and 1280 CSS pixels.
- Check keyboard-only operation, visible focus, zoom, and reduced motion.
- Check for uncaught console errors.
- Check offline core behavior.

If a real phone or browser automation is unavailable, say so explicitly and distinguish code inspection from actual device testing.

### DEFINITION OF DONE

The task is complete only when:
- The final result is one standalone HTML file.
- The mobile interaction root cause has been addressed, not merely hidden with CSS.
- All visible controls work.
- Existing vocabulary content is preserved.
- Core functionality works offline.
- The app is responsive, accessible, and visually consistent.
- Storage failures do not crash the app.
- The test report is honest and specific.
- The final response includes the output file and a concise summary of changes, tests, and known limitations.

### FINAL RESPONSE FORMAT

Return:
1. The final standalone HTML file.
2. A concise root-cause report for the original mobile issue.
3. A list of completed features and visual improvements.
4. A list of tests actually performed and their results.
5. Any known limitations or unimplemented features.

Never state that a test passed unless it was actually run.

---

## 15. Final Principle

**Reliability before features; learning quality before decoration; evidence before assumptions.**

A smaller set of dependable learning tools is better than a large interface full of broken or misleading controls. Fix the mobile interaction foundation, preserve the content, then expand the learning experience in measured, testable steps.

---

## 16. Implementation Notes (v2.1.0, 2026-10-27)

### Deliverable

- **`index.html`**: the complete app in one file (about 21.9 MB). Open it directly in a modern browser; no server, build step or network connection is needed.
- `b1-b2-kelimeler-responsive.html`: the original page, left unchanged as the content source.
- `tools/sentences/*.json`: the example sentences grouped by word type (see below), merged into `index.html` by the build.
- `tools/build_index.py` + `tools/app_template.html`: only needed to regenerate `index.html` if the original page changes (`python tools/build_index.py`). The script extracts every card programmatically and **refuses to write output** if any count does not match the source.

### Root cause of the mobile tap problem (confirmed in the source)

1. A `<head>` script set `window.__mobileInteractionsReady = false` and registered a document-wide `touchend` listener (calling `preventDefault()`) and a capture-phase `click` listener (calling `stopImmediatePropagation()`). Every tap on a button, `summary` or clickable figure was swallowed and queued.
2. The flag was set to `true` only on the very last line of the final script, after the browser had parsed about 28 MB of HTML and the script had rewritten the examples of all 2000 cards. On a phone this can take seconds, and during that time every control looked dead. Queued taps were replayed later, out of context.
3. A second layer synthesised `click()` from `touchend` and suppressed the real click for 700 ms. The two competing layers could drop or duplicate taps, and they overrode native `<details>/<summary>` behaviour.
4. Each card had two learn toggles (a `figure role="button"` and a button), so tapping an image while scrolling could mark a word learned.

**Fix:** all global touch/click interception is gone. Every action is a native `<button type="button">` handled by a standard `click` listener (one delegated listener per container). Disclosures use native `<details>`. Images are not interactive. The app script runs *before* the image data, so the interface is usable while images are still parsing.

### Other defects found and fixed

- Search lower-cased with the Turkish locale, so "IT" became "ıt" and English searches for "it" failed. Search now maps ı/İ/I to "i" and ignores accents (`basarmak` finds `başarmak`); displayed text is unchanged.
- At runtime the old script replaced each card's original example sentence with a template-generated one. The original examples and translations are now shown. In v2.1 the template generator was removed and replaced by sentences written for each word type (see Features).
- 1262 cards used one of 90 generic shared images (e.g. “IT” used the “Employ” image). They are kept, labelled “Shared image”, with honest alt text.
- `localStorage` was written on every load and failures were silently ignored. Storage now goes through one adapter with validation, schema versioning and visible messages.
- 202 duplicate embedded images were deduplicated (828 → 626 unique), shrinking the file from 28.2 MB to 21.6 MB without removing any image.

### Content preserved (verified by the build script)

| Field | Source | Extracted |
|---|---|---|
| Cards / unique IDs | 2000 | 2000 |
| Example sentences | 738 | 738 |
| English definitions | 320 | 320 |
| Example translations | 638 | 638 |
| Pronunciation notes | 2000 | 2000 |
| Cards with an image | 2000 | 2000 |

IDs are `w` + the original card number, so progress saved under the old key (`b1-b2-learned-words-v1`) is migrated automatically on first load.

**Content issues noticed but deliberately not changed** (review separately): section titles state wrong counts (e.g. “A harfi (19 kelime)” contains 29 words); some definitions do not fit the entry (e.g. “IT” is defined as the country code for Italy); 18 words appear twice in different sections.

### Features

The app has five sections: Home, Words, Quiz, Reading and Settings.

- **Home:** study path (all / B1 / B2 / mixed, taken from section titles and not CEFR-certified), a next-step action, and statistics computed only from saved activity (learned words, quiz accuracy, study streak).
- **Words:** search (English and Turkish); status, level and section filters; original, A–Z and related-meaning order (using the original explicit groups); 24 cards per batch with “Show more”; empty state with reset; learned toggle; device speech. Each card shows its word types (verb, noun, adjective…) and an **“Example sentences”** disclosure that opens two sentences per word type, each with a Turkish translation.
- **Example sentences by word type:** 4,872 sentences for all 1,981 distinct words (all 2,000 entries; duplicate words share their sentences). Every word type the word commonly has in English gets its own group, e.g. *approach* (verb, noun), *welcome* (verb, adjective, interjection), *either* (determiner, conjunction, adverb). The sentences were written for this app, not generated from a template at runtime, and are stored in `tools/sentences/*.json`. The build checks that every key exists in the vocabulary, that only known word-type codes are used and that every pair is complete. It also lists the sentences where the word appears only in an irregular form (e.g. *sank*, *dug*, *tore*).
- **Quiz:** English→Turkish, Turkish→English, fill-in-the-blank and mixed. The word set defaults to **“Words I have learned”** whenever any word is marked learned (with live counts for each set). Fill-in-the-blank uses the original example and the new sentences. Distractors are unique, each question accepts one answer, and the result screen lists missed words with “practise missed”.
- **Reading and listening:** 3 passages written for this app (level is the author's estimate). Includes vocabulary highlighting with a glossary, a Turkish translation toggle, comprehension questions, and optional device speech with play / pause / stop plus a hide-text listening mode. No recorded audio is included.
- **Settings:** theme (system / light / dark), English or Turkish interface, show or hide Turkish sentence translations, voice and speed, JSON export, validated import with confirmation, and reset with confirmation.

### Tests actually performed

Automated checks ran in the Claude desktop app's built-in Chromium browser, with the page served from `http://127.0.0.1`. They used scripted DOM events plus real mouse clicks and real key presses.

- Build validation (table above), including sentence data (2000 of 2000 entries covered). Node.js syntax check of the app script.
- Search (English, Turkish, accent-less, İ/ı), empty state and reset; status, level and section filters; A–Z and related order; “Show more”.
- Learned toggle with real clicks: one click made one change, which was saved. Five rapid clicks made exactly five toggles. Scrolling over cards changed nothing.
- Example sentences: the disclosure opens the right word-type groups (e.g. *welcome*: verb, adjective, interjection) in English and Turkish interfaces; no card on the first page lacks sentences.
- Quiz: all four modes. Answered by real click and by keyboard (Enter, Tab, Space). A second answer is blocked, score and attempts count once, and the result screen, “practise missed” and ending early all work. The learned-word set is selected by default once words are marked, and fill-in-the-blank questions come from the new sentences.
- Reading translation, hide-text mode and questions work; the player changes state correctly and stops on navigation.
- In Settings: theme, the quick theme button, language switch and translation toggle.
- Export (the file was captured, not downloaded). Import with invalid JSON, a wrong schema and invalid IDs; cancel, Escape and confirm. Reset with confirm.
- Progress survives a reload. Corrupt saved JSON is backed up and a banner is shown. The old key is migrated. With storage switched off (`?storage=off`) the app works in memory and shows a banner.
- At 320, 360, 390, 430, 768 and 1280 px: no horizontal overflow and every control ≥ 44 × 44 px in every view (v2.0). After v2.1, the five-tab menu and all views were rechecked at 320 px with Turkish labels. Mobile preset (375 px, Android user agent): tap and scroll checked.
- Contrast of every text/background token pair is ≥ 5.9:1 in both themes (calculated from the colour values).
- No console errors during the session.

### Not tested / known limitations

- **Not tested on a real phone**, or in Safari/iOS or Firefox. Mobile checks used Chromium device emulation, which delivers taps as mouse clicks.
- Opening the file via `file://` could not be checked, because the test browser refused local files. The code has no server dependency, but this was not verified.
- Speech synthesis was checked only for state changes; audio output and voice quality were not heard. The test browser offered no English voice.
- Not tested with a real screen reader. Semantics and live regions were checked in the code and the accessibility tree only.
- Reduced motion and 200 % zoom were not emulated directly. The CSS rules exist, and 200 % zoom on a 1280 px desktop gives a 640 px layout, which falls inside the narrow widths tested.
- Load time was measured only on a desktop over localhost. Phones will be slower because the file is 21.9 MB.
- Progress stays in one browser on one device; there is no sync.

### How to extend the content

- **Vocabulary:** edit the original page and rerun `python tools/build_index.py`, or edit the JSON inside `<script id="vocab-data">` in `index.html` directly. Keep each `id` stable. Fields: `word`, `meaning`, `pron`, `example`, `exampleTr`, `definition`, `section`, `level`, `img`.
- **Example sentences:** add or edit entries in `tools/sentences/*.json` and rerun the build. Format: `{"word": {"v": [["English", "Türkçe"], ...], "n": [...]}}`. Word-type codes: `n`, `v`, `adj`, `adv`, `prep`, `conj`, `pron`, `det`, `num`, `int`, `phr`.
- **Reading:** add objects to `READINGS` in `tools/app_template.html` and rebuild.
- **Interface text:** `STRINGS.en` / `STRINGS.tr`.

### Change log

- **2.0.0 (2026-10-27)**: rebuilt as a single-file study app. Removed tap interception; new design system, dashboard, review, quiz modes, grammar, reading/listening, writing, settings and data portability; content extracted and validated.
- **2.1.0 (2026-10-27)**: removed the Review, Grammar and Writing sections at the user's request. Replaced the runtime template sentences with 4,872 example sentences, grouped by word type, for every word. The quiz now defaults to learned words, and fill-in-the-blank uses the new sentences.
