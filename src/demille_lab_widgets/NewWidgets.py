"""Small Qt widgets with lab-friendly interaction defaults."""

from __future__ import annotations

import logging
import math

import os

# This distribution targets PyQt5. Prevent pyqtgraph from choosing another Qt binding.
os.environ["PYQTGRAPH_QT_LIB"] = "PyQt5"

import pyqtgraph as pg
from PyQt5 import QtCore
from PyQt5 import QtWidgets as qt


def _step_exponent(text: str, cursor: int, decimal_point: bool) -> int:
    """Return the base-10 place selected by an insertion cursor."""
    unsigned = text.lstrip("+-")
    sign_length = len(text) - len(unsigned)
    cursor = max(0, min(cursor - sign_length, len(unsigned)))

    separator = unsigned.find(".") if decimal_point else -1
    integer_length = separator if separator >= 0 else len(unsigned)
    integer_length = max(integer_length, 1)

    if separator < 0 or cursor <= separator:
        digit_offset = min(max(cursor, 1), integer_length)
        return integer_length - digit_offset

    fractional_offset = max(1, cursor - separator - 1)
    fractional_digits = max(1, len(unsigned) - separator - 1)
    return -min(fractional_offset, fractional_digits)


class FlexibleGridLayout(qt.QHBoxLayout):
    """A sparse, column-oriented grid with stable row/column positions."""

    def __init__(self, grid_num=10):
        super().__init__()
        if grid_num < 1:
            raise ValueError("grid_num must be at least 1")

        self.cols = {}
        self._cells = {}
        for column in range(grid_num):
            column_layout = qt.QVBoxLayout()
            self.cols[column] = column_layout
            self.addLayout(column_layout)
            for row in range(grid_num):
                cell = qt.QHBoxLayout()
                column_layout.addLayout(cell)
                self._cells[row, column] = cell
            column_layout.addStretch(1)

    def addWidget(self, widget, row, col):
        try:
            cell = self._cells[row, col]
        except KeyError as exc:
            raise IndexError(f"cell ({row}, {col}) is outside the layout") from exc
        if cell.count():
            raise ValueError(f"cell ({row}, {col}) is already occupied")
        cell.addWidget(widget)

    def clear(self):
        """Detach every widget while retaining the grid structure."""
        for cell in self._cells.values():
            while cell.count():
                item = cell.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)


class NewBox(qt.QGroupBox):
    """A group box with a zero-margin layout exposed as ``frame``."""

    def __init__(self, layout_type="grid"):
        super().__init__()
        factories = {
            "grid": qt.QGridLayout,
            "vbox": qt.QVBoxLayout,
            "hbox": qt.QHBoxLayout,
            "form": qt.QFormLayout,
            "flexgrid": FlexibleGridLayout,
        }
        factory = factories.get(layout_type)
        if factory is None:
            logging.warning("NewBox: unsupported layout type %r; using grid", layout_type)
            factory = qt.QGridLayout

        self.frame = factory()
        self.frame.setContentsMargins(0, 0, 0, 0)
        self._styles_form = isinstance(self.frame, qt.QFormLayout)
        if self._styles_form:
            self.frame.setHorizontalSpacing(0)
            self._apply_form_style()
        self.setLayout(self.frame)

    def _apply_form_style(self):
        """Re-apply the form style sheet, reserving room for the title.

        A style sheet makes Qt derive the contents rect from the CSS box model,
        which drops the strip a QGroupBox otherwise reserves for its title. Add
        that strip back as top padding whenever a title is set, so the first row
        of the form is not drawn underneath the title.
        """
        padding_top = self.fontMetrics().height() if self.title() else 0
        self.setStyleSheet(
            "QGroupBox {border: 0; padding-left: 0; padding-right: 0;"
            f" padding-top: {padding_top}px;}}"
        )

    def setTitle(self, title):
        super().setTitle(title)
        # Qt may call setTitle before __init__ has chosen a layout.
        if getattr(self, "_styles_form", False):
            self._apply_form_style()


class _FocusedWheelMixin:
    """Let a wheel event reach the control only while it has focus."""

    def wheelEvent(self, event):
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()


class _CursorStepMixin:
    _uses_decimal_point = False

    def stepBy(self, steps):
        editor = self.lineEdit()
        prefix_length = len(self.prefix())
        old_text = self.cleanText()
        old_integer_length = len(old_text.split(".", 1)[0])
        cursor = max(0, editor.cursorPosition() - prefix_length)
        exponent = _step_exponent(old_text, cursor, self._uses_decimal_point)
        step = 10.0**exponent if self._uses_decimal_point else 10**exponent
        self.setSingleStep(step)

        super().stepBy(steps)
        editor.deselect()

        new_integer_length = len(self.cleanText().split(".", 1)[0])
        cursor += new_integer_length - old_integer_length
        editor.setCursorPosition(prefix_length + max(0, cursor))


class NewDoubleSpinBox(_FocusedWheelMixin, _CursorStepMixin, qt.QDoubleSpinBox):
    """A double spin box with focus-only wheel and cursor-place stepping."""

    _uses_decimal_point = True

    def __init__(self, range=None, decimals=None, suffix=None):
        super().__init__()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setKeyboardTracking(False)
        self.setRange(*(range if range is not None else (-math.inf, math.inf)))
        if decimals is not None:
            self.setDecimals(decimals)
        if suffix is not None:
            self.setSuffix(suffix)


class NewSpinBox(_FocusedWheelMixin, _CursorStepMixin, qt.QSpinBox):
    """An integer spin box with focus-only wheel and cursor-place stepping."""

    def __init__(self, range=None, suffix=None):
        super().__init__()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setKeyboardTracking(False)
        self.setRange(*(range if range is not None else (-(2**31), 2**31 - 1)))
        if suffix is not None:
            self.setSuffix(suffix)


class NewComboBox(_FocusedWheelMixin, qt.QComboBox):
    """A combo box that ignores wheel input until explicitly focused."""

    def __init__(self, item_list=None, current_item=None):
        super().__init__()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        if item_list is not None:
            self.addItems(item_list)
        if current_item is not None:
            self.setCurrentText(current_item)


class NewPlot(pg.PlotWidget):
    """A plot widget configured with a four-sided grid frame."""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.showGrid(x=True, y=True)
        for side in ("top", "right"):
            self.setLabel(side)
            self.getAxis(side).setStyle(showValues=False)
        self.getAxis("bottom").enableAutoSIPrefix(False)


class NewScrollArea(qt.QScrollArea):
    """A resizable scroll area whose content layout is exposed as ``frame``."""

    def __init__(self, layout_type="grid"):
        super().__init__()
        self.setWidgetResizable(True)
        self.setFrameShape(qt.QFrame.NoFrame)

        box = NewBox(layout_type=layout_type)
        box.setObjectName("ScrollArea")
        box.setStyleSheet("QGroupBox#ScrollArea {border: 0;}")
        self.setWidget(box)
        self.frame = box.frame
