"""Scientific-notation input implemented for the DeMille widget package."""

from __future__ import annotations

import math
import re

from PyQt5 import QtGui

from .NewWidgets import NewDoubleSpinBox, _step_exponent


_COMPLETE_NUMBER = re.compile(
    r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$"
)
_PARTIAL_NUMBER = re.compile(
    r"^[+-]?(?:(?:\d+(?:\.\d*)?|\.\d*)(?:[eE][+-]?\d*)?|\d*\.?\d*)$"
)


def valid_float_string(text):
    """Return whether *text* is a complete finite floating-point literal."""
    if not _COMPLETE_NUMBER.fullmatch(text):
        return False
    try:
        return math.isfinite(float(text))
    except ValueError:
        return False


def valid_float_string_2(text):
    """Return whether *text* is complete or could become a valid float."""
    return bool(_PARTIAL_NUMBER.fullmatch(text))


def format_float(precision, value=None):
    """Format a number using fixed-precision scientific notation.

    ``format_float(value)`` is also accepted and uses six decimal places.
    """
    if value is None:
        value = precision
        precision = 6
    if precision < 0:
        raise ValueError("precision must be non-negative")
    if not math.isfinite(value):
        return str(value)

    coefficient, exponent = f"{value:.{precision}e}".split("e")
    exponent_value = int(exponent)
    return f"{coefficient}e{exponent_value:+d}"


class _ScientificValidator(QtGui.QValidator):
    def validate(self, text, position):
        if valid_float_string(text):
            return self.Acceptable, text, position
        if valid_float_string_2(text):
            return self.Intermediate, text, position
        return self.Invalid, text, position

    def fixup(self, text):
        return text.strip() if valid_float_string(text.strip()) else ""


class ScientificDoubleSpinBox(NewDoubleSpinBox):
    """A focus-safe double spin box that reads and writes exponent notation."""

    def __init__(self, range=None, decimals=2, suffix=None):
        self._display_decimals = decimals
        self._scientific_validator = None
        super().__init__(range=range, decimals=323, suffix=suffix)
        self._scientific_validator = _ScientificValidator(self)

    def validate(self, text, position):
        if self._scientific_validator is None:
            if valid_float_string(text):
                return QtGui.QValidator.Acceptable, text, position
            if valid_float_string_2(text):
                return QtGui.QValidator.Intermediate, text, position
            return QtGui.QValidator.Invalid, text, position
        return self._scientific_validator.validate(text, position)

    def fixup(self, text):
        return self._scientific_validator.fixup(text)

    def valueFromText(self, text):
        return float(text.strip())

    def textFromValue(self, value):
        return format_float(self._display_decimals, value)

    def stepBy(self, steps):
        text = self.cleanText().lower()
        coefficient_text, separator, exponent_text = text.partition("e")
        if not separator or not exponent_text:
            return

        cursor = max(0, self.lineEdit().cursorPosition() - len(self.prefix()))
        exponent = int(exponent_text)
        if cursor <= len(coefficient_text):
            place = _step_exponent(coefficient_text, cursor, decimal_point=True)
            coefficient = float(coefficient_text) + steps * 10.0**place
            value = coefficient * 10.0**exponent
        else:
            exponent_cursor = cursor - len(coefficient_text) - 1
            place = _step_exponent(exponent_text, exponent_cursor, decimal_point=False)
            value = float(coefficient_text) * 10.0 ** (
                exponent + steps * 10**place
            )
        self.setValue(value)
        self.lineEdit().deselect()
