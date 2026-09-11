# DeMille Lab Widgets for PyQt5

Small, reusable PyQt5 widgets developed for laboratory control-system interfaces.

The package improves several common Qt interactions, including preventing spin boxes and combo boxes from changing when the mouse wheel is used while the widget does not have focus. It also provides cursor-position-aware numeric stepping, scientific-notation input, convenience layouts, a configured plotting widget, and a table widget with frozen rows and columns.

## Installation

Once the first release is published to PyPI:

```console
python -m pip install demille-lab-widgets-pyqt5
```

## Usage

```python
from demille_lab_widgets import NewBox, NewDoubleSpinBox, NewSpinBox

voltage = NewDoubleSpinBox(range=(-10.0, 10.0), decimals=3, suffix=" V")
shots = NewSpinBox(range=(0, 100_000))
controls = NewBox(layout_type="form")
controls.frame.addRow("Voltage", voltage)
controls.frame.addRow("Shots", shots)
```

The public classes are:

- `NewBox`
- `NewComboBox`
- `NewSpinBox`
- `NewDoubleSpinBox`
- `ScientificDoubleSpinBox`
- `NewPlot`
- `NewScrollArea`
- `FlexibleGridLayout`
- `NewTableWidget`

## Behavior

`NewSpinBox`, `NewDoubleSpinBox`, and `NewComboBox` ignore mouse-wheel changes until they have keyboard focus. The numeric spin boxes also change their step size according to the cursor position. Keyboard tracking is disabled so typed values are committed when Enter is pressed or focus is lost.

## Development

Create a virtual environment, then install the package in editable form:

```console
python -m pip install -e ".[test]"
python -m unittest discover -s tests -v
python -m build
python -m twine check dist/*
```

## Release status

The package implementation is maintained independently in this repository and
is distributed under the [MIT License](LICENSE). Runtime dependencies retain
their own licenses; see [Third-party notices](THIRD_PARTY_NOTICES.md).

## Acknowledgements

The widget collection was originally developed by Olivier and Jakob for the
CeNTREX experiment. Wang subsequently brought it into the DeMille Lab control
software and developed additional improvements. Shaozhen later extracted it
into this standalone package, coordinated the licensing review, and prepared
the public release. See [project history and contributors](AUTHORS.md).
