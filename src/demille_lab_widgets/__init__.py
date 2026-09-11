"""Improved PyQt5 widgets used by DeMille Lab control systems."""

from .NewWidgets import (
    FlexibleGridLayout,
    NewBox,
    NewComboBox,
    NewDoubleSpinBox,
    NewPlot,
    NewScrollArea,
    NewSpinBox,
)
from .NewTableWidget import NewTableWidget
from .scientificspin import ScientificDoubleSpinBox

__version__ = "0.1.0"

__all__ = [
    "FlexibleGridLayout",
    "NewBox",
    "NewComboBox",
    "NewDoubleSpinBox",
    "NewPlot",
    "NewScrollArea",
    "NewSpinBox",
    "NewTableWidget",
    "ScientificDoubleSpinBox",
]
