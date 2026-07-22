# SPDX-License-Identifier: LGPL-2.1-or-later
"""Reusable dimension task panel for BramHome creators."""

from __future__ import annotations

try:
    from PySide import QtGui  # noqa: F401
    try:
        from PySide import QtWidgets
    except ImportError:
        QtWidgets = QtGui  # PySide1: widgets lived in QtGui
except ImportError:
    from PySide2 import QtWidgets  # type: ignore


class DimensionTaskPanel:
    """Form with label + spinbox (mm) pairs and Create / Cancel."""

    def __init__(self, title, fields, on_accept):
        self._on_accept = on_accept
        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle(title)
        layout = QtWidgets.QVBoxLayout(self.form)

        heading = QtWidgets.QLabel(title)
        heading.setStyleSheet("font-weight: 600; font-size: 13px;")
        layout.addWidget(heading)

        hint = QtWidgets.QLabel("All dimensions in millimetres (mm).")
        hint.setStyleSheet("color: #666;")
        layout.addWidget(hint)

        self._widgets = {}
        form = QtWidgets.QFormLayout()
        for field in fields:
            if field.get("integer"):
                spin = QtWidgets.QSpinBox()
                spin.setRange(int(field.get("minimum", 0)), int(field.get("maximum", 99)))
                spin.setValue(int(field["value"]))
            else:
                spin = QtWidgets.QDoubleSpinBox()
                spin.setDecimals(int(field.get("decimals", 1)))
                spin.setRange(float(field.get("minimum", 0.1)), float(field.get("maximum", 1e6)))
                spin.setSingleStep(float(field.get("step", 10)))
                spin.setSuffix(" mm")
                spin.setValue(float(field["value"]))
            form.addRow(field["label"], spin)
            self._widgets[field["key"]] = spin

        layout.addLayout(form)
        layout.addStretch(1)

        buttons = QtWidgets.QHBoxLayout()
        ok = QtWidgets.QPushButton("Create")
        cancel = QtWidgets.QPushButton("Cancel")
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        buttons.addWidget(ok)
        buttons.addWidget(cancel)
        layout.addLayout(buttons)

    def get_values(self):
        return {key: widget.value() for key, widget in self._widgets.items()}

    def accept(self):
        self._on_accept(self.get_values())
        self._close()

    def reject(self):
        self._close()

    def _close(self):
        import FreeCADGui as Gui

        Gui.Control.closeDialog()

    def getStandardButtons(self):
        return 0
