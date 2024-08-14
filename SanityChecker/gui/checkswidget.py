import traceback
from pathlib import Path
from PySide2 import QtWidgets, QtCore, QtGui
from pysideutils import get_icon, eStatusType

import sanitychecker as sc
from sanitychecker.run import get_progress_interface
from sanitychecker.gui.filterwidget import FilterWidget
from sanitychecker.gui.presetswidget import PresetsWidget
from sanitychecker.gui.collapsiblecheckwidget import (
    CollapsibleCheckWidget,
    CollapsibleCheckHeader,
)
from sanitychecker.logger import logger_gui


class ChecksWidget(QtWidgets.QWidget):
    rightClick = QtCore.Signal(QtCore.QPoint, super)

    def __init__(self, parent=None, dialog=None, status_bar=None):
        super(ChecksWidget, self).__init__(parent)
        self.status_bar = status_bar
        self.dialog = dialog
        self.check_widgets = []
        self.__setup_ui()
        self.__set_connections()

    def __setup_ui(self):
        self.setBaseSize(QtCore.QSize(self.dialog.MIN_WIDTH, self.dialog.MIN_HEIGHT))
        widget_size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.setSizePolicy(widget_size_policy)

        # Widgets
        btns_size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        btns_size_policy.setHorizontalStretch(0)
        btns_size_policy.setVerticalStretch(0)
        self.reload_BTN = QtWidgets.QPushButton(self)
        reload_BTN_size = QtCore.QSize(25, 25)
        self.reload_BTN.setSizePolicy(btns_size_policy)
        self.reload_BTN.setMinimumSize(reload_BTN_size)
        self.reload_BTN.setMaximumSize(reload_BTN_size)
        self.reload_BTN.setObjectName("reload_BTN")
        self.reload_BTN.setToolTip("Reload all checks and contexts.")
        self.reload_BTN.installEventFilter(self.dialog)
        module_dir = Path(__file__).parent
        imgs_dir = module_dir.joinpath("imgs")
        refresh_icon = QtGui.QIcon(get_icon(imgs_dir, "refresh"))
        self.reload_BTN.setIcon(refresh_icon)
        self.reload_BTN.setIconSize(
            QtCore.QSize(reload_BTN_size.width() - 5, reload_BTN_size.height() - 5)
        )
        self.presets_WIDGET = PresetsWidget(dialog=self.dialog, parent=self)
        self.checks_filter_WIDGET = FilterWidget(
            dialog=self.dialog, checks_widget=self, parent=self
        )
        self.checks_WIDGET = QtWidgets.QWidget(self)
        checks_SCROLL = QtWidgets.QScrollArea()
        checks_SCROLL.setFrameShape(QtWidgets.QFrame.NoFrame)
        checks_SCROLL.setWidgetResizable(True)
        checks_SCROLL.setWidget(self.checks_WIDGET)

        # Layouts
        container_LAYOUT = QtWidgets.QVBoxLayout()
        container_LAYOUT.setContentsMargins(0, 0, 0, 0)
        leftside_LAYOUT = QtWidgets.QVBoxLayout()
        leftside_LAYOUT.setContentsMargins(0, 0, 0, 0)
        toolbar_LAYOUT = QtWidgets.QHBoxLayout()
        toolbar_LAYOUT.setContentsMargins(0, 0, 0, 0)
        self.checks_LAYOUT = QtWidgets.QVBoxLayout()
        self.checks_LAYOUT.setContentsMargins(0, 0, 0, 0)
        self.checks_LAYOUT.setSpacing(3)
        self.checks_LAYOUT.setAlignment(QtCore.Qt.AlignTop)

        toolbar_LAYOUT.addWidget(self.reload_BTN)
        toolbar_LAYOUT.addWidget(self.presets_WIDGET)
        toolbar_LAYOUT.addWidget(self.checks_filter_WIDGET)
        self.checks_WIDGET.setLayout(self.checks_LAYOUT)

        leftside_LAYOUT.addLayout(toolbar_LAYOUT)
        leftside_LAYOUT.addWidget(checks_SCROLL)
        container_LAYOUT.addLayout(leftside_LAYOUT)

        self.setLayout(container_LAYOUT)

    def __set_connections(self):
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.rightClick.connect(self.checks_options)

    def build_widgets(self):
        checks_with_context = []
        for context in sc.SHARED_CONTEXTS_REGISTRY:
            context_header = CollapsibleCheckHeader(check_obj=context, parent=self)
            context_WIDGET = CollapsibleCheckWidget(
                text=context.name,
                check_obj=context,
                header_widget=context_header,
                dialog=self.dialog,
                children_checks=list(),
                parent=self,
            )
            context_header.setParent(context_WIDGET)
            self.check_widgets.append(context_WIDGET)
            self.checks_LAYOUT.addWidget(context_WIDGET)
            for check in context.checks:
                child_header = CollapsibleCheckHeader(check_obj=check, parent=self)
                child_WIDGET = CollapsibleCheckWidget(
                    text=check.name,
                    check_obj=check,
                    header_widget=child_header,
                    parent_context=context_WIDGET,
                    children_checks=[],
                    dialog=self.dialog,
                    parent=self,
                )
                child_header.setParent(child_WIDGET)
                child_WIDGET.main_layout.setContentsMargins(16, 0, 0, 0)
                self.check_widgets.append(child_WIDGET)
                checks_with_context.append(check)
                context_WIDGET.add_child_check(child_WIDGET)
                self.checks_LAYOUT.addWidget(child_WIDGET)

        for check in sc.CHECKS_REGISTRY:
            if check not in checks_with_context:
                check_header = CollapsibleCheckHeader(check_obj=check, parent=self)
                check_WIDGET = CollapsibleCheckWidget(
                    text=check.name,
                    check_obj=check,
                    header_widget=check_header,
                    dialog=self.dialog,
                    children_checks=[],
                    parent=self,
                )
                check_header.setParent(check_WIDGET)
                self.check_widgets.append(check_WIDGET)
                self.checks_LAYOUT.addWidget(check_WIDGET)

        for widget in self.check_widgets:
            widget.rightClick.connect(self.checks_options)

    def reset_widgets(self):
        for widget in self.check_widgets:
            widget.setVisible(False)
            widget.deleteLater()
        self.check_widgets = []
        self.build_widgets()
        self.status_bar.update(
            "Sanity check repos reloaded.", status_type=eStatusType.success
        )

    def checks_options(self, pos, widget):
        menu = QtWidgets.QMenu(self)
        actions_label = QtWidgets.QLabel("<b>Actions</b>")
        actions_action = QtWidgets.QWidgetAction(menu)
        actions_action.setDefaultWidget(actions_label)
        menu.addAction(actions_action)
        run_selected = menu.addAction("Run selected")
        run_all = menu.addAction("Run All")

        view_label = QtWidgets.QLabel("<b>View</b>")
        view_label_action = QtWidgets.QWidgetAction(menu)
        view_label_action.setDefaultWidget(view_label)
        menu.addAction(view_label_action)
        expand_all = menu.addAction("Expand All")
        collapse_all = menu.addAction("Collapse All")
        select_all = menu.addAction("Select All")
        clear_selection = menu.addAction("Clear Selection")

        menu.popup(widget.mapToGlobal(pos))

        # Actions
        run_selected.triggered.connect(self.run_selected)
        run_all.triggered.connect(self.run_all)

        # View
        expand_all.triggered.connect(self.expand_all)
        collapse_all.triggered.connect(self.collapse_all)
        select_all.triggered.connect(lambda: self.set_selection(True))
        clear_selection.triggered.connect(lambda: self.set_selection(False))

    def run_selected(self):
        checks = []
        contexts = []
        for widget in self.check_widgets:
            if widget.is_selected():
                if isinstance(widget.check_obj, sc.SanityCheck):
                    if widget.check_obj not in checks:
                        checks.append(widget.check_obj)
                elif isinstance(widget.check_obj, sc.SharedContext):
                    if widget.check_obj not in contexts:
                        contexts.append(widget.check_obj)
        self.run_checks(checks, contexts)

    def run_all(self):
        checks = sc.CHECKS_REGISTRY.get_all_checks()
        contexts = sc.SHARED_CONTEXTS_REGISTRY.get_all_contexts()
        return self.run_checks(checks, contexts)

    def run_checks(self, checks, contexts):
        # Run checks
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        progress_interface = get_progress_interface()
        self.status_bar.start_progress_bar(progress_interface)
        try:
            checks, contexts = sc.run_checks(checks=checks, contexts=contexts, try_fix=True)
        except Exception:
            exception_traceback = traceback.format_exc()
            logger_gui.exception(
                f"There was an error while running the checks.\n{exception_traceback}"
            )
        finally:
            self.status_bar.end_progress_bar()
            QtWidgets.QApplication.restoreOverrideCursor()
            return checks, contexts

    def expand_all(self):
        for widget in self.check_widgets:
            widget.set_expanded(True)

    def collapse_all(self):
        for widget in self.check_widgets:
            widget.set_expanded(False)

    def set_selection(self, selected: bool):
        for widget in self.check_widgets:
            widget.set_selected(selected)

    def mousePressEvent(self, event: QtCore.QEvent):
        if event.button() == QtCore.Qt.RightButton:
            cursor = QtGui.QCursor()
            self.rightClick.emit(self.mapFromGlobal(cursor.pos()), self)
        else:
            super(ChecksWidget, self).mousePressEvent(event)


if __name__ == "__main__":
    pass
