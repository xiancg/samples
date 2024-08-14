import re
from PySide2 import QtWidgets, QtCore


class FilterWidget(QtWidgets.QWidget):
    def __init__(self, dialog=None, checks_widget=None, parent=None):
        super(FilterWidget, self).__init__(parent)
        self.dialog = dialog
        self.checks_widget = checks_widget
        self.__setup_ui()
        self.__set_connections()

    def __setup_ui(self):
        # Container
        main_size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        main_size_policy.setHorizontalStretch(0)
        main_size_policy.setVerticalStretch(0)
        self.setSizePolicy(main_size_policy)
        self.setObjectName("filter_WIDGET")
        self.filter_LAYOUT = QtWidgets.QHBoxLayout()
        self.filter_LAYOUT.setObjectName("filter_LAYOUT")
        self.filter_LAYOUT.setContentsMargins(4, 4, 4, 4)

        # Widgets
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed
        )
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        filter_LINEEDIT_size = QtCore.QSize(130, 22)
        self.filter_LINEEDIT = QtWidgets.QLineEdit(self)
        self.filter_LINEEDIT.setSizePolicy(size_policy)
        self.filter_LINEEDIT.setMinimumSize(filter_LINEEDIT_size)
        self.filter_LINEEDIT.setMaximumSize(filter_LINEEDIT_size)
        self.filter_LINEEDIT.setObjectName("filter_LINEEDIT")
        self.filter_LINEEDIT.setToolTip('Filter by name')
        self.filter_LINEEDIT.installEventFilter(self.dialog)
        filter_LABEL_size = QtCore.QSize(36, 22)
        self.filter_LABEL = QtWidgets.QLabel(self)
        self.filter_LABEL.setSizePolicy(size_policy)
        self.filter_LABEL.setMinimumSize(filter_LABEL_size)
        self.filter_LABEL.setMaximumSize(filter_LABEL_size)
        self.filter_LABEL.setObjectName("filter_LABEL")
        self.filter_LABEL.setText("Filter: ")

        # Layout
        self.filter_LAYOUT.insertStretch(0, 1)
        self.filter_LAYOUT.addWidget(self.filter_LABEL)
        self.filter_LAYOUT.addWidget(self.filter_LINEEDIT)
        self.setLayout(self.filter_LAYOUT)

        QtCore.QMetaObject.connectSlotsByName(self)

    def __set_connections(self):
        self.filter_LINEEDIT.textChanged.connect(self.filter_by_text)

    def filter_by_text(self):
        """Filters items shown in targets tree view with user input.
        Comparisons are made using the start of the string for each item.

        Args:
            ``view`` (QAbstractItemView or subclass): The view where filtering
            will be used.
        """
        filter_text = self.filter_LINEEDIT.text().lower()
        if filter_text != "":
            if "*" in filter_text:
                filter_text = r"\b" + filter_text.replace("*", r"\w*") + r"\b"
            else:
                filter_text = r"\b\w*" + filter_text + r"\w*\b"
            filter_pattern = re.compile(filter_text)
            self.checks_widget.expand_all()
            self.hide_unhide(self.checks_widget.check_widgets, True)
            self.__process_filter_by_text(self.checks_widget.check_widgets, filter_pattern)
        else:
            self.hide_unhide(self.checks_widget.check_widgets, True)

    def hide_unhide(self, widgets: list, hide: bool):
        for widget in widgets:
            widget.setVisible(hide)

    def __process_filter_by_text(self, widgets: list, filter_pattern: re.Pattern):
        for widget in widgets:
            check_obj_name = widget.check_obj.name
            match = filter_pattern.match(check_obj_name.lower())
            if match:
                widget.setVisible(True)
                if widget.parent_context:
                    widget.parent_context.setVisible(True)
            else:
                widget.setVisible(False)


if __name__ == "__main__":
    pass
