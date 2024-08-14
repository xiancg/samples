from functools import partial

from PySide2 import QtWidgets, QtGui, QtCore

from pysideutils import CollapsibleWidget, CollapsibleHeader, RightClickButton
from sanitychecker.status import CheckStatus, ContextStatus
from sanitychecker.sanitycheck import SanityCheck, SharedContext


class CollapsibleCheckWidget(CollapsibleWidget):
    CHECK_PASSED_COLOR = QtGui.QColor(0, 255, 0, 80)
    CHECK_NOT_PASSED_COLOR = QtGui.QColor(255, 128, 0, 80)
    CHECK_FAILED_COLOR = QtGui.QColor(255, 0, 0, 80)
    CHECK_CANCELLED_COLOR = QtGui.QColor(0, 0, 0, 0)
    CHECK_NOT_RAN_COLOR = QtGui.QColor(0, 0, 0, 0)
    CHECK_RUNNING_COLOR = QtGui.QColor(255, 255, 255, 32)

    CONTEXT_READY_COLOR = QtGui.QColor(0, 0, 255, 80)
    CONTEXT_NOT_READY_COLOR = QtGui.QColor(0, 0, 0, 0)
    CONTEXT_FAILED_COLOR = QtGui.QColor(255, 0, 0, 80)
    CONTEXT_CANCELLED_COLOR = QtGui.QColor(0, 0, 0, 0)
    CONTEXT_FINISHED_COLOR = QtGui.QColor(0, 255, 0, 80)

    def __init__(
        self,
        text,
        check_obj,
        header_widget: CollapsibleHeader,
        parent_context=None,
        children_checks=list(),
        dialog=None,
        parent=None,
    ):
        super(CollapsibleCheckWidget, self).__init__(text, header_widget, parent)
        self.__children_checks = children_checks
        self.__parent_context = parent_context
        self.__check_obj = check_obj
        self.dialog = dialog

        self.setup_widgets()
        self.setup_layout()
        self.__set_connections()

    def setup_widgets(self):
        # TODO: Improve this layout to make it a bit more compact
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.setSizePolicy(size_policy)

        # Description
        if self.__check_obj.description != "":
            self.description_LABEL = QtWidgets.QLabel(self.body_WIDGET)
            self.description_LABEL.setText(
                f"Description: {self.__check_obj.description}"
            )
        if isinstance(self.__check_obj, SanityCheck):
            if len(self.__check_obj.dependencies_names):
                self.dependencies_LABEL = QtWidgets.QLabel(self.body_WIDGET)
                self.dependencies_LABEL.setText(
                    f"Dependencies: {', '.join(self.__check_obj.dependencies_names)}"
                )

        self.check_GRPBOX = QtWidgets.QGroupBox(self.body_WIDGET)
        self.check_GRPBOX.setFlat(True)
        self.check_GRPBOX.setCheckable(False)
        self.check_GRPBOX.setToolTip("Check, fix, setup, teardown")
        check_btns_layout = QtWidgets.QHBoxLayout()
        check_btns_layout.setContentsMargins(0, 0, 0, 0)
        self.check_GRPBOX.setLayout(check_btns_layout)

        # Check, fix, setup, teardown
        if self.__check_obj.has_setup():
            self.setup_BUTTON = QtWidgets.QPushButton("Setup", self.check_GRPBOX)
            check_btns_layout.addWidget(self.setup_BUTTON)
        if isinstance(self.__check_obj, SanityCheck):
            if self.__check_obj.has_check():
                self.check_BUTTON = RightClickButton(self.check_GRPBOX)
                self.check_BUTTON.setText("Check")
                self.check_BUTTON.setToolTip("Right click for more options.")
                self.check_BUTTON.installEventFilter(self.dialog)
                check_btns_layout.addWidget(self.check_BUTTON)
                self.check_BUTTON.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            if self.__check_obj.has_fix():
                self.fix_BUTTON = QtWidgets.QPushButton("Fix", self.check_GRPBOX)
                check_btns_layout.addWidget(self.fix_BUTTON)
        if self.__check_obj.has_teardown():
            self.teardown_BUTTON = QtWidgets.QPushButton("Teardown", self.check_GRPBOX)
            check_btns_layout.addWidget(self.teardown_BUTTON)

        # Messages
        if isinstance(self.__check_obj, SanityCheck):
            self.msgs_LINEEDIT = QtWidgets.QTextEdit(self.body_WIDGET)
            self.msgs_LINEEDIT.setReadOnly(True)
            self.msgs_LINEEDIT.setVisible(False)
            self.msgs_LINEEDIT.setSizePolicy(size_policy)
            self.msgs_LINEEDIT.setMinimumHeight(20)
            self.msgs_LINEEDIT.setMaximumHeight(100)

        # Actions
        self.action_btns = []
        if len(self.__check_obj.actions):
            self.actions_GRPBOX = QtWidgets.QGroupBox(self.body_WIDGET)
            self.actions_GRPBOX.setFlat(True)
            self.actions_GRPBOX.setCheckable(False)
            self.actions_GRPBOX.setToolTip("Optional actions")
            self.actions_GRPBOX.installEventFilter(self.dialog)

            for action in self.__check_obj.actions:
                action_BUTTON = QtWidgets.QPushButton(action.name, self.actions_GRPBOX)
                action_BUTTON.setText(action.name)
                action_BUTTON.setToolTip(action.description)
                self.action_btns.append(action_BUTTON)

    def setup_layout(self):
        self.main_layout.setSpacing(0)
        self.body_layout.setContentsMargins(4, 0, 4, 0)
        self.body_layout.setSpacing(0)
        if isinstance(self.__check_obj, SanityCheck):
            msg_layout = QtWidgets.QVBoxLayout()
            msg_layout.setContentsMargins(0, 0, 0, 0)
            msg_layout.addWidget(self.msgs_LINEEDIT)
        btns_layout = QtWidgets.QHBoxLayout()
        if self.__check_obj.description != "":
            self.add_widget(self.description_LABEL)
        if isinstance(self.__check_obj, SanityCheck):
            if len(self.__check_obj.dependencies_names):
                self.add_widget(self.dependencies_LABEL)
        self.add_layout(btns_layout)
        btns_layout.addWidget(self.check_GRPBOX)
        btns_layout.setContentsMargins(0, 0, 0, 0)
        self.add_layout(msg_layout)

        if len(self.action_btns):
            action_btns_layout = QtWidgets.QHBoxLayout()
            action_btns_layout.setContentsMargins(0, 0, 0, 0)
            self.actions_GRPBOX.setLayout(action_btns_layout)
            for btn in self.action_btns:
                action_btns_layout.addWidget(btn)
            btns_layout.addWidget(self.actions_GRPBOX)

    def __set_connections(self):
        if isinstance(self.__check_obj, SanityCheck):
            self.check_BUTTON.rightClick.connect(self.check_btn_options)
            if self.__check_obj.has_check():
                self.check_BUTTON.clicked.connect(self.run_check_only)
            if self.__check_obj.has_fix():
                self.fix_BUTTON.clicked.connect(self.run_fix_only)
        if self.__check_obj.has_setup():
            self.setup_BUTTON.clicked.connect(self.run_setup_only)
        if self.__check_obj.has_teardown():
            self.teardown_BUTTON.clicked.connect(self.run_teardown_only)

        for action, action_btn in zip(self.__check_obj.actions, self.action_btns):
            action_btn.clicked.connect(partial(action.run_action))

        self.__check_obj.status.signal.updated.connect(self.update_check_widget)
        self.__check_obj.status.signal.updated.connect(self.process_events)
        if isinstance(self.header_WIDGET, CollapsibleCheckHeader):
            self.header_WIDGET.select_CHKBOX.stateChanged.connect(self.update_selected)

    def update_check_widget(self):
        self.update_msg(self.__check_obj.status)
        if isinstance(self.__check_obj.status, CheckStatus):
            self.update_bg_color_for_check(self.__check_obj.status)
        elif isinstance(self.__check_obj.status, ContextStatus):
            self.update_bg_color_for_context(self.__check_obj.status)

    def update_msg(self, status_obj):
        if len(status_obj):
            self.msgs_LINEEDIT.setText(status_obj.message)
            self.msgs_LINEEDIT.resize(
                QtCore.QSize(self.msgs_LINEEDIT.width(), (len(status_obj) + 1) * 20)
            )
            self.msgs_LINEEDIT.setVisible(True)
        self.header_WIDGET.update_check(status_obj)

    def process_events(self):
        QtCore.QCoreApplication.processEvents()

    def update_bg_color_for_check(self, status: CheckStatus):
        if status.code == CheckStatus.passed:
            self.set_header_background_color(self.CHECK_PASSED_COLOR)
        if status.code == CheckStatus.not_passed:
            self.set_header_background_color(self.CHECK_NOT_PASSED_COLOR)
        if status.code == CheckStatus.failed:
            self.set_header_background_color(self.CHECK_FAILED_COLOR)
        if status.code == CheckStatus.cancelled:
            self.set_header_background_color(self.CHECK_CANCELLED_COLOR)
        if status.code == CheckStatus.not_ran:
            self.set_header_background_color(self.CHECK_NOT_RAN_COLOR)
        if status.code == CheckStatus.running:
            self.set_header_background_color(self.CHECK_RUNNING_COLOR)

    def update_bg_color_for_context(self, status: ContextStatus):
        if status.code == ContextStatus.ready:
            self.set_header_background_color(self.CONTEXT_READY_COLOR)
        if status.code == ContextStatus.not_ready:
            self.set_header_background_color(self.CONTEXT_NOT_READY_COLOR)
        if status.code == ContextStatus.failed:
            self.set_header_background_color(self.CONTEXT_FAILED_COLOR)
        if status.code == ContextStatus.cancelled:
            self.set_header_background_color(self.CONTEXT_CANCELLED_COLOR)
        if status.code == ContextStatus.finished:
            self.set_header_background_color(self.CONTEXT_FINISHED_COLOR)

    def check_btn_options(self, pos):
        if isinstance(self.__check_obj, SanityCheck):
            menu = QtWidgets.QMenu(self.check_BUTTON)
            actions_label = QtWidgets.QLabel("<b>Options</b>")
            actions_action = QtWidgets.QWidgetAction(menu)
            actions_action.setDefaultWidget(actions_label)
            menu.addAction(actions_action)
            run_full_check = menu.addAction("Run full check")
            run_full_check.setToolTip(
                "Run setup, check, fix and teardown if available."
            )
            run_check_only = menu.addAction("Run check only")
            run_check_only.setToolTip("Ignore setup, fix and teardown if available.")

            menu.popup(self.check_BUTTON.mapToGlobal(pos))

            run_full_check.triggered.connect(self.run_full_check)
            run_check_only.triggered.connect(self.run_check_only)

    def set_expanded(self, expanded: bool):
        super(CollapsibleCheckWidget, self).set_expanded(expanded)
        if len(self.__children_checks) and isinstance(self.__check_obj, SharedContext):
            for child in self.__children_checks:
                child.set_expanded(expanded)

    def update_selected(self):
        if len(self.__children_checks) and isinstance(self.__check_obj, SharedContext):
            for child in self.__children_checks:
                child.set_selected(self.is_selected())

    def is_selected(self):
        if isinstance(self.header_WIDGET, CollapsibleCheckHeader):
            return self.header_WIDGET.is_selected()
        return False

    def set_selected(self, selected: bool):
        if isinstance(self.header_WIDGET, CollapsibleCheckHeader):
            self.header_WIDGET.set_selected(selected)

    def run_full_check(self):
        self.__check_obj.run_full_check()

    def run_check_only(self):
        self.__check_obj.run_check()

    def run_fix_only(self):
        self.__check_obj.run_fix()

    def run_setup_only(self):
        self.__check_obj.run_setup()

    def run_teardown_only(self):
        self.__check_obj.run_teardown()

    def add_child_check(self, check: SanityCheck):
        self.__children_checks.append(check)

    @property
    def check_obj(self):
        return self.__check_obj

    @property
    def children_checks(self):
        return self.__children_checks

    @property
    def parent_context(self):
        return self.__parent_context

    @parent_context.setter
    def parent_context(self, context):
        self.__parent_context = context


class CollapsibleCheckHeader(CollapsibleHeader):
    def __init__(self, check_obj, parent):
        super(CollapsibleCheckHeader, self).__init__(check_obj.name, parent)
        self.__check_obj = check_obj
        self.__progress_interface = None
        if check_obj.progress:
            self.__progress_interface = check_obj.progress
        self.setup_contents()
        self.update_check(self.__check_obj.status)

    def setup_contents(self):
        self.message_LABEL = QtWidgets.QLabel(self)
        self.select_CHKBOX = QtWidgets.QCheckBox(self)
        self.select_CHKBOX.setChecked(True)
        self.prog_WIDGET = QtWidgets.QProgressBar(self)
        self.prog_WIDGET.setVisible(False)
        if self.__progress_interface:
            self.__progress_interface.guiwidget = self.prog_WIDGET

        self.main_layout.insertWidget(0, self.select_CHKBOX)
        self.main_layout.setAlignment(self.select_CHKBOX, QtCore.Qt.AlignLeft)
        self.main_layout.addWidget(self.message_LABEL)
        self.main_layout.setAlignment(self.message_LABEL, QtCore.Qt.AlignRight)
        self.main_layout.addWidget(self.prog_WIDGET)
        self.main_layout.setAlignment(self.prog_WIDGET, QtCore.Qt.AlignRight)
        self.main_layout.setContentsMargins(4, 2, 4, 2)

    def update_check(self, status_obj):
        self.message_LABEL.setText(str(status_obj))

    def is_selected(self):
        return self.select_CHKBOX.isChecked()

    def set_selected(self, selected: bool):
        self.select_CHKBOX.setChecked(selected)

    def start_progress_bar(self):
        if self.__progress_interface:
            self.__progress_interface.reset_progress()
            self.message_LABEL.setVisible(False)
            self.prog_WIDGET.setVisible(True)

    def end_progress_bar(self):
        if self.__progress_interface:
            self.prog_WIDGET.setVisible(False)
            self.message_LABEL.setVisible(True)
            self.__progress_interface.reset_progress()
