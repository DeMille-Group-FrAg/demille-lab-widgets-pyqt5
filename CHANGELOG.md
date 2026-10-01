# Changelog

## Unreleased

- Keep `NewTableWidget`'s frozen rows and columns aligned with the table. The
  overlays enforced their own minimum section size, so a row shorter than that
  minimum (30 px against 31 px on a scaled Windows display) was drawn taller in
  the frozen column, which drifted one pixel further off its row every row.
  The frozen-row overlay also sized its row header only for the numbers it
  shows, so with ten or more rows its cells sat left of their columns.

## 0.1.4 - 2026-09-14

- Link each contributor named in the acknowledgements to their GitHub account.

## 0.1.3 - 2026-09-11

- Stop `NewTableWidget` from collapsing its own rows and columns. Hiding a
  section in a frozen overlay resizes that section to zero, and the overlay
  reported the change back to the table, so every unfrozen row and column ended
  up zero-sized and the table rendered empty.
- Reserve room for the title on `NewBox(layout_type="form")`. The style sheet
  that removes the form box's border made Qt derive the contents rect from the
  CSS box model, so a box with a title drew its first row underneath the title
  text. Untitled form boxes keep their zero margins.
- Log a warning instead of raising when `FlexibleGridLayout.addWidget` targets
  an occupied cell, so a duplicated position in a configuration file costs one
  widget rather than the window.

## 0.1.1 - 2026-09-11

- Select PyQt5 for PyQtGraph before importing it, so PyQtGraph no longer
  tries to load another Qt binding when one is present in the environment.

## 0.1.0 - 2026-09-11

- Replace implementations with independently maintained package-local code
  before the first public release.
- Add the MIT license and retain a record of the source-provenance review.
- Record the known contributor history for the initial public release.
- Create an installable package from the established DeMille Lab widget collection.
- Use the `demille_lab_widgets` import namespace.
- Fix the internal scientific-spin-box import for installed-package use.
- Correct frozen-row initialization to use the model's row count.
- Forward `NewPlot`'s optional parent to `PlotWidget`.
