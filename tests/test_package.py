import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

import demille_lab_widgets as widgets
from demille_lab_widgets.scientificspin import (
    format_float,
    valid_float_string,
    valid_float_string_2,
)


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_public_api(self):
        expected = {
            "FlexibleGridLayout",
            "NewBox",
            "NewComboBox",
            "NewDoubleSpinBox",
            "NewPlot",
            "NewScrollArea",
            "NewSpinBox",
            "NewTableWidget",
            "ScientificDoubleSpinBox",
        }
        self.assertEqual(set(widgets.__all__), expected)
        for name in expected:
            self.assertTrue(hasattr(widgets, name))

    def test_spin_box_configuration(self):
        spin = widgets.NewSpinBox(range=(-12, 34), suffix=" Hz")
        self.assertEqual(spin.minimum(), -12)
        self.assertEqual(spin.maximum(), 34)
        self.assertEqual(spin.suffix(), " Hz")
        self.assertFalse(spin.keyboardTracking())

    def test_double_spin_box_configuration(self):
        spin = widgets.NewDoubleSpinBox(range=(-1.5, 2.5), decimals=4, suffix=" V")
        self.assertEqual(spin.minimum(), -1.5)
        self.assertEqual(spin.maximum(), 2.5)
        self.assertEqual(spin.decimals(), 4)
        self.assertEqual(spin.suffix(), " V")
        self.assertFalse(spin.keyboardTracking())

    def test_new_plot_preserves_parent(self):
        parent = QWidget()
        plot = widgets.NewPlot(parent=parent)
        self.assertIs(plot.parent(), parent)

    def test_table_can_configure_frozen_sections(self):
        table = widgets.NewTableWidget(frozenRows=1, frozenCols=1)
        table.setRowCount(3)
        table.setColumnCount(4)
        self.assertEqual(table.rowCount(), 3)
        self.assertEqual(table.columnCount(), 4)
        self.assertFalse(table.frozenRowTableView.isRowHidden(0))
        self.assertTrue(table.frozenRowTableView.isRowHidden(1))
        self.assertFalse(table.frozenColTableView.isColumnHidden(0))
        self.assertTrue(table.frozenColTableView.isColumnHidden(1))

    def test_scientific_number_validation(self):
        for value in ("0", "-1.25", ".5", "1.23e+4", "-2E-3"):
            self.assertTrue(valid_float_string(value), value)
        for value in ("", "-", "1e", "1e-"):
            self.assertTrue(valid_float_string_2(value), value)
        self.assertEqual(format_float(2, 1234.0), "1.23e+3")

    def test_cursor_position_controls_integer_step(self):
        spin = widgets.NewSpinBox(range=(-9999, 9999))
        spin.setValue(1234)
        spin.lineEdit().setCursorPosition(2)
        spin.stepBy(1)
        self.assertEqual(spin.value(), 1334)

    def test_cursor_position_controls_decimal_step(self):
        spin = widgets.NewDoubleSpinBox(range=(-100, 100), decimals=2)
        spin.setValue(12.34)
        spin.lineEdit().setCursorPosition(5)
        spin.stepBy(1)
        self.assertAlmostEqual(spin.value(), 12.35)

    def test_scientific_spin_box_keeps_constructor_api(self):
        spin = widgets.ScientificDoubleSpinBox(
            range=(-1e6, 1e6), decimals=3, suffix=" Hz"
        )
        self.assertEqual(spin.suffix(), " Hz")
        self.assertEqual(spin.textFromValue(1234.0), "1.234e+3")

    def test_flexible_grid_can_be_reused_after_clear(self):
        layout = widgets.FlexibleGridLayout(grid_num=2)
        first = QLabel("first")
        layout.addWidget(first, 0, 1)
        layout.clear()
        second = QLabel("second")
        layout.addWidget(second, 0, 1)
        self.assertIs(layout._cells[0, 1].itemAt(0).widget(), second)

    def _shown_form_box(self, title):
        """Return a realized, parented form box plus its first field widget."""
        parent = QWidget()
        layout = QVBoxLayout(parent)
        box = widgets.NewBox(layout_type="form")
        if title is not None:
            box.setTitle(title)
        field = QLabel("field")
        box.frame.addRow("Voltage", field)
        layout.addWidget(box)
        parent.resize(300, 200)
        parent.show()
        self.app.processEvents()
        self.addCleanup(parent.hide)
        return box, field

    def test_titled_form_box_reserves_room_for_its_title(self):
        box, field = self._shown_form_box("Scan parameters")
        title_strip = box.getContentsMargins()[1]
        self.assertGreaterEqual(title_strip, box.fontMetrics().height())
        # The first row starts below the title rather than underneath it.
        self.assertGreaterEqual(field.geometry().top(), title_strip)

    def test_untitled_form_box_keeps_zero_margins(self):
        box, field = self._shown_form_box(None)
        self.assertEqual(box.getContentsMargins(), (0, 0, 0, 0))
        self.assertEqual(field.geometry().top(), 0)

    def test_clearing_a_form_box_title_releases_the_reserved_space(self):
        box, _ = self._shown_form_box("Scan parameters")
        box.setTitle("")
        self.app.processEvents()
        self.assertEqual(box.getContentsMargins(), (0, 0, 0, 0))

    def test_titled_box_layouts_other_than_form_are_unchanged(self):
        for layout_type in ("grid", "vbox", "hbox"):
            box = widgets.NewBox(layout_type=layout_type)
            box.setTitle("Title")
            self.assertGreater(box.getContentsMargins()[1], 0, layout_type)
            self.assertEqual(box.styleSheet(), "", layout_type)

    def test_negative_frozen_counts_are_rejected(self):
        with self.assertRaises(ValueError):
            widgets.NewTableWidget(frozenRows=-1, frozenCols=0)


if __name__ == "__main__":
    unittest.main()
