# Changelog

## 1.2.2 — 2026-10-04

- Released the English-first interface and Simplified Chinese translations on Blender Extensions. HUD, preference labels, tooltips, reports, and status hints follow Blender's translation settings.
- Re-recorded the real Blender demonstration and screenshots in English, with 16:9 demo exports for the extension listing.
- Added explicit English-language capture settings and checks for untranslated HUD text in the capture workflow.
- Mesh editing behavior and default shortcuts are unchanged.

## 1.2.1 — 2026-10-02

- Prepared the Blender Extensions submission under GPL-3.0-or-later, using the existing GPL-2.0-or-later grant; included the GPL version 3 license text and author copyright metadata.
- Added English and Simplified Chinese UI translations that follow Blender's language and its interface, tooltip, and report translation switches.
- Refresh HUD text, measured layout, and status hints when the language changes during an operation; added real-window translation checks.
- Documented the default Shift + E shortcut overlap, automatic interface translation, and the absence of network access or external dependencies.
- Excluded browser automation artifacts from extension builds. Mesh editing behavior is unchanged from 1.2.0.

## Documentation & media — 2026-10-02

- Redesigned the icon around editable mesh vertices and attribute edges: orange crease and blue bevel weight; refreshed both icon sizes and the media ZIP.
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
