# Changelog

## Documentation & media — 2026-10-02

- Added a real Blender GIF demonstration and MP4 export to both READMEs.
- Added orange/blue icon variants and a 1920 × 1080 cover, with source artwork and media preparation notes.
- Added a reproducible Blender capture script; the add-on remains at version 1.2.0.

## 1.2.0 — 2026-10-02

- Cached the HUD shader, measured layout, static geometry, and text positions per operation; combined static shapes into one batch.
- Reused geometry while following the cursor; only the progress fill is rebuilt when the value changes.
- Skipped repeated weight writes and mesh updates, cached valid selected-element targets, and reduced selection snapshot allocation.
- Avoided duplicate redraw requests and preserved mixed weights on stationary or vertical mouse events.
- Released HUD and selection caches on confirm, cancel, or add-on disable.
- Added a reproducible Blender benchmark with deterministic work-count checks and expanded integration coverage to 13 tests.

## 1.1.2 — 2026-10-02

- Set orange as the crease theme and blue as the bevel-weight theme.
- Added separate theme color preferences for each tool, applied to its value, selection badge, indicator, and progress bar.

## 1.1.1 — 2026-10-02

- Moved mouse and keyboard hints into a separate vertical floating list to the right of the value HUD.
- Kept the list visible throughout adjustment, with an independent visibility toggle in preferences.
- Fit both panels together within the viewport, including cursor placement and large font settings.

## 1.1.0 — 2026-10-02

- Redesigned the HUD with anti-aliased rounded cards, selection badges, a pill progress bar, and grouped key hints.
- Added configurable corner radius and card shadow.
- Added automatic sizing to keep the HUD inside smaller viewports.
- Simplified standalone setup and shortcut preferences.

## 1.0.0 — 2026-10-02

- Added selection-aware crease and bevel-weight adjustment as a standalone add-on.
- Added native shortcut customization and configurable HUD position, size, colors, background, and help.
- Added multi-object editing with shared-mesh deduplication.
- Fixed cancel behavior to restore individual values and remove newly created attribute layers.
- Made Shift snapping match the on-screen help.
- Added real Blender integration tests and window interaction checks.
- Added illustrated Chinese and English documentation and an installable extension archive.
