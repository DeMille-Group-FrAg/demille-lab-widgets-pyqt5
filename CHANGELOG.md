# Changelog

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
