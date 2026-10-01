"""A table widget with independently frozen leading rows and columns."""

from __future__ import annotations

from contextlib import contextmanager

from PyQt5 import QtCore
from PyQt5 import QtWidgets as qt


class NewTableWidget(qt.QTableWidget):
    """Display leading rows and columns in synchronized overlay views."""

    def __init__(self, frozenRows=1, frozenCols=1, parent=None):
        super().__init__(parent)
        if frozenRows < 0 or frozenCols < 0:
            raise ValueError("frozen row and column counts cannot be negative")

        self.frozenRows = frozenRows
        self.frozenCols = frozenCols
        self.frozenColTableView = self._make_overlay()
        self.frozenRowTableView = self._make_overlay()
        self.frozenCornerTableView = self._make_overlay()

        self.frozenColTableView.verticalHeader().hide()
        self.frozenRowTableView.horizontalHeader().hide()

        self.setHorizontalScrollMode(self.ScrollPerPixel)
        self.setVerticalScrollMode(self.ScrollPerPixel)
        self.frozenColTableView.setVerticalScrollMode(self.ScrollPerPixel)
        self.frozenRowTableView.setHorizontalScrollMode(self.ScrollPerPixel)

        self.verticalScrollBar().valueChanged.connect(
            self.frozenColTableView.verticalScrollBar().setValue
        )
        self.frozenColTableView.verticalScrollBar().valueChanged.connect(
            self.verticalScrollBar().setValue
        )
        self.horizontalScrollBar().valueChanged.connect(
            self.frozenRowTableView.horizontalScrollBar().setValue
        )
        self.frozenRowTableView.horizontalScrollBar().valueChanged.connect(
            self.horizontalScrollBar().setValue
        )

        self.horizontalHeader().sectionResized.connect(self._column_resized)
        self.verticalHeader().sectionResized.connect(self._row_resized)
        self.frozenColTableView.horizontalHeader().sectionResized.connect(
            self.updateSectionWidthFrozenCols
        )
        self.frozenRowTableView.verticalHeader().sectionResized.connect(
            self.updateSectionHeightFrozenRows
        )
        self.frozenCornerTableView.horizontalHeader().sectionResized.connect(
            self.updateSectionWidthFrozenCorner
        )
        self.frozenCornerTableView.verticalHeader().sectionResized.connect(
            self.updateSectionHeightFrozenCorner
        )
        self._refresh_overlays()

    @property
    def _overlays(self):
        return (
            self.frozenColTableView,
            self.frozenRowTableView,
            self.frozenCornerTableView,
        )

    def _make_overlay(self):
        view = qt.QTableView(self)
        view.setModel(self.model())
        view.setSelectionModel(self.selectionModel())
        view.setFocusPolicy(QtCore.Qt.NoFocus)
        view.setFrameShape(qt.QFrame.NoFrame)
        view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        view.setStyleSheet("QTableView {border: 0; padding: 0;}")
        for header in (view.horizontalHeader(), view.verticalHeader()):
            header.setSectionResizeMode(qt.QHeaderView.Interactive)
            # An overlay only mirrors this table's section sizes. A minimum of
            # its own would clamp them (a 30 px row drawn 31 px tall), and the
            # frozen cells would drift further off their rows with every row.
            header.setMinimumSectionSize(0)
        view.show()
        return view

    @contextmanager
    def _overlay_sizes_detached(self):
        """Stop the overlays from echoing section sizes back into this table.

        Hiding a section resizes it to zero, and an overlay's ``sectionResized``
        signal is wired to resize the matching section here. Without this the
        overlays would collapse every row and column they hide.
        """
        headers = [
            header
            for view in self._overlays
            for header in (view.horizontalHeader(), view.verticalHeader())
        ]
        previous = [header.blockSignals(True) for header in headers]
        try:
            yield
        finally:
            for header, state in zip(headers, previous):
                header.blockSignals(state)

    def _refresh_overlays(self):
        row_count = self.model().rowCount()
        column_count = self.model().columnCount()
        frozen_rows = min(self.frozenRows, row_count)
        frozen_columns = min(self.frozenCols, column_count)

        # Read this table's sizes before touching the overlays, which hide
        # sections and would otherwise report those hidden sizes back.
        heights = [self.rowHeight(row) for row in range(row_count)]
        widths = [self.columnWidth(column) for column in range(column_count)]

        with self._overlay_sizes_detached():
            for row in range(row_count):
                frozen = row < frozen_rows
                for view in self._overlays:
                    view.setRowHeight(row, heights[row])
                self.frozenRowTableView.setRowHidden(row, not frozen)
                self.frozenCornerTableView.setRowHidden(row, not frozen)
                self.frozenColTableView.setRowHidden(row, False)

            for column in range(column_count):
                frozen = column < frozen_columns
                for view in self._overlays:
                    view.setColumnWidth(column, widths[column])
                self.frozenColTableView.setColumnHidden(column, not frozen)
                self.frozenCornerTableView.setColumnHidden(column, not frozen)
                self.frozenRowTableView.setColumnHidden(column, False)

        self._update_geometries()

    def _frozen_width(self):
        count = min(self.frozenCols, self.columnCount())
        return sum(self.columnWidth(column) for column in range(count))

    def _frozen_height(self):
        count = min(self.frozenRows, self.rowCount())
        return sum(self.rowHeight(row) for row in range(count))

    def _update_geometries(self):
        frame = self.frameWidth()
        vertical, horizontal = self.verticalHeader(), self.horizontalHeader()
        header_width = 0 if vertical.isHidden() else vertical.width()
        header_height = 0 if horizontal.isHidden() else horizontal.height()
        viewport = self.viewport()
        width = self._frozen_width()
        height = self._frozen_height()

        # Each overlay sizes its headers from the sections it shows, so a
        # frozen row would otherwise get a header only wide enough for "1"
        # and its cells would sit left of the columns they belong to.
        for view in self._overlays:
            view.verticalHeader().setFixedWidth(header_width)
            view.horizontalHeader().setFixedHeight(header_height)
            view.updateGeometries()

        self.frozenColTableView.setGeometry(
            header_width + frame,
            frame,
            width,
            viewport.height() + header_height,
        )
        self.frozenRowTableView.setGeometry(
            frame,
            header_height + frame,
            viewport.width() + header_width,
            height,
        )
        self.frozenCornerTableView.setGeometry(
            frame,
            frame,
            width + header_width,
            height + header_height,
        )
        for view in self._overlays:
            view.raise_()

    def updateFrozenColTableGeometry(self):
        self._update_geometries()

    def updateFrozenRowTableGeometry(self):
        self._update_geometries()

    def updateFrozenCornerTableGeometry(self):
        self._update_geometries()

    def _column_resized(self, index, old_size, new_size):
        for view in self._overlays:
            view.setColumnWidth(index, new_size)
        self._update_geometries()

    def _row_resized(self, index, old_size, new_size):
        for view in self._overlays:
            view.setRowHeight(index, new_size)
        self._update_geometries()

    def updateSectionWidth(self, logicalIndex, oldSize, newSize):
        self._column_resized(logicalIndex, oldSize, newSize)

    def updateSectionHeight(self, logicalIndex, oldSize, newSize):
        self._row_resized(logicalIndex, oldSize, newSize)

    def updateSectionWidthFrozenCols(self, logicalIndex, oldSize, newSize):
        self.setColumnWidth(logicalIndex, newSize)

    def updateSectionHeightFrozenRows(self, logicalIndex, oldSize, newSize):
        self.setRowHeight(logicalIndex, newSize)

    def updateSectionWidthFrozenCorner(self, logicalIndex, oldSize, newSize):
        self.setColumnWidth(logicalIndex, newSize)

    def updateSectionHeightFrozenCorner(self, logicalIndex, oldSize, newSize):
        self.setRowHeight(logicalIndex, newSize)

    def hideFrozenCols(self, columns):
        with self._overlay_sizes_detached():
            for column in columns:
                self.frozenColTableView.setColumnHidden(column, True)
                self.frozenCornerTableView.setColumnHidden(column, True)

    def hideFrozenRows(self, rows):
        with self._overlay_sizes_detached():
            for row in rows:
                self.frozenRowTableView.setRowHidden(row, True)
                self.frozenCornerTableView.setRowHidden(row, True)

    def setColumnCount(self, columnCount):
        super().setColumnCount(columnCount)
        if hasattr(self, "frozenColTableView"):
            self._refresh_overlays()

    def setRowCount(self, rowCount):
        super().setRowCount(rowCount)
        if hasattr(self, "frozenRowTableView"):
            self._refresh_overlays()

    def updateGeometries(self):
        # Qt calls this whenever the headers or viewport change size, e.g. when
        # a new row count needs another digit in the row header.
        super().updateGeometries()
        if hasattr(self, "frozenCornerTableView"):
            self._update_geometries()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "frozenColTableView"):
            self._update_geometries()

    def scrollTo(self, index, hint=qt.QAbstractItemView.EnsureVisible):
        if index.column() >= self.frozenCols or index.row() >= self.frozenRows:
            super().scrollTo(index, hint)
