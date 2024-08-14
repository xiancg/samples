import webbrowser
import logging
from pathlib import Path
from PySide2 import QtCore, QtWidgets
from pysideutils import (
    get_icon,
    StatusBarWidget,
    LogWidget,
    eStatusType,
    RightClickButton,
)

import sanitychecker as sc
from sanitychecker.error import RepoError, ImplementationError
from sanitychecker.gui.checkswidget import ChecksWidget
from sanitychecker.logger import logger, logger_gui


class SanityChecker_GUI(QtWidgets.QDialog):
    TOOL_NAME = "sanitychecker"
    TOOL_NICE_NAME = "Sanity Checker"
    DEFAULT_WIDTH = 950
    DEFAULT_HEIGHT = 850
    MIN_WIDTH = DEFAULT_WIDTH / 2
    MIN_HEIGHT = DEFAULT_HEIGHT / 2
    DEFAULT_LOGGING_LEVEL = logging.INFO

    def __init__(self, parent, *args, **kwargs):
        super(SanityChecker_GUI, self).__init__(parent)
        self.__processing = False
        self.repos = []
        self.__setup_ui()
        self.__set_connections()
        if "repos" in kwargs:
            self.load_repos(kwargs.get("repos", []))

    def __setup_ui(self):
        # Main setup
        self.setWindowTitle(self.TOOL_NICE_NAME)
        self.setObjectName(f"{self.TOOL_NAME}_DIALOG")
        win_default_size = QtCore.QSize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        self.resize(win_default_size)
        self.setMinimumWidth(self.MIN_WIDTH)
        self.setMinimumHeight(self.MIN_HEIGHT)
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)
        module_dir = Path(__file__).parent
        imgs_dir = module_dir.joinpath("imgs")
        self.setWindowIcon(get_icon(imgs_dir, self.TOOL_NAME))
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setObjectName("main_layout")
        main_layout.setContentsMargins(0, 0, 0, 0)
        statusbar_layout = QtWidgets.QVBoxLayout(self)
        statusbar_layout.setContentsMargins(0, 0, 0, 0)
        central_layout = QtWidgets.QVBoxLayout(self)

        # Menu and Status Bar
        self.main_menubar = QtWidgets.QMenuBar(self)
        self.edit_menu = self.main_menubar.addMenu("Edit")
        logging_label = QtWidgets.QLabel("<b>Logging</b>")
        logging_action = QtWidgets.QWidgetAction(self.edit_menu)
        logging_action.setDefaultWidget(logging_label)
        self.edit_menu.addAction(logging_action)
        levels_menu = self.edit_menu.addMenu("Set level")
        self.log_to_file = self.edit_menu.addAction("Log to file")
        self.log_to_file.setCheckable(True)
        self.log_to_file.setChecked(False)

        self.action_grp_levels = QtWidgets.QActionGroup(levels_menu)
        no_log_level = self.action_grp_levels.addAction("No log")
        no_log_level.setCheckable(True)
        critical_level = self.action_grp_levels.addAction("Critical")
        critical_level.setCheckable(True)
        error_level = self.action_grp_levels.addAction("Error")
        error_level.setCheckable(True)
        warning_level = self.action_grp_levels.addAction("Warning")
        warning_level.setCheckable(True)
        info_level = self.action_grp_levels.addAction("Info")
        info_level.setCheckable(True)
        debug_level = self.action_grp_levels.addAction("Debug")
        debug_level.setCheckable(True)
        self.action_grp_levels.setExclusive(True)
        info_level.setChecked(True)
        levels_menu.addAction(no_log_level)
        levels_menu.addAction(critical_level)
        levels_menu.addAction(error_level)
        levels_menu.addAction(warning_level)
        levels_menu.addAction(info_level)
        levels_menu.addAction(debug_level)

        self.docs_action = self.main_menubar.addAction("Docs")

        self.status_bar = StatusBarWidget(self)

        # Widgets
        btn_size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        btn_size_policy.setHorizontalStretch(0)
        btn_size_policy.setVerticalStretch(0)

        self.log_WIDGET = LogWidget(logger_gui, parent=self)
        self.checks_WIDGET = ChecksWidget(
            parent=self, dialog=self, status_bar=self.status_bar
        )
        self.run_checks_BTN = RightClickButton(self)
        run_checks_BTN_size = QtCore.QSize(160, 40)
        self.run_checks_BTN.setText("Run Checks")
        self.run_checks_BTN.setToolTip("Run Checks. Right click for more options.")
        self.run_checks_BTN.setMinimumSize(run_checks_BTN_size)
        self.run_checks_BTN.setMaximumSize(run_checks_BTN_size)
        self.run_checks_BTN.setSizePolicy(btn_size_policy)
        self.run_checks_BTN.installEventFilter(self)

        # Layout setup
        splitter_size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        splitter_size_policy.setVerticalStretch(2)
        self.splitter = QtWidgets.QSplitter(self)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.checks_WIDGET)
        self.splitter.addWidget(self.log_WIDGET)
        self.splitter.setCollapsible(0, False)
        self.splitter.setSizes([self.checks_WIDGET.width(), self.DEFAULT_WIDTH * 0.3])
        self.splitter.setSizePolicy(splitter_size_policy)

        btns_layout = QtWidgets.QHBoxLayout(self)

        btns_layout.addWidget(self.run_checks_BTN)
        btns_layout.setAlignment(self.run_checks_BTN, QtCore.Qt.AlignCenter)
        statusbar_layout.addWidget(self.status_bar)
        central_layout.addWidget(self.splitter)
        central_layout.addLayout(btns_layout)

        main_layout.setMenuBar(self.main_menubar)
        main_layout.addLayout(central_layout)
        main_layout.addLayout(statusbar_layout)

        self.setLayout(main_layout)
        self.status_bar.update(f"{self.TOOL_NICE_NAME} loaded!", eStatusType.success)

    def __set_connections(self):
        self.checks_WIDGET.reload_BTN.clicked.connect(
            lambda: self.load_repos(self.repos)
        )
        self.run_checks_BTN.clicked.connect(self.checks_WIDGET.run_all)
        self.run_checks_BTN.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.run_checks_BTN.rightClick.connect(self.run_checks_options)
        self.action_grp_levels.triggered.connect(self.set_logging_level)
        self.log_to_file.triggered.connect(self.start_logging_to_file)
        self.docs_action.triggered.connect(self.open_docs)

    def eventFilter(self, widget, event):
        """Event filter mainly used for tooltip display in status bar.
        Event filter installing is execute by setupUi

        Args:
            ``widget`` (QtQwidgets.QWidget): Passed by PySyde

            ``event`` (QtCore.QEvent): Passed by PySyde

        Returns:
            [bool]: True if event was handled out by any of our widgets.
            Pass the event on to the parent class otherwise.
        """
        if event.type() == QtCore.QEvent.Enter:
            self.status_bar.update(widget.toolTip(), eStatusType.tooltip)
            return True
        elif event.type() == QtCore.QEvent.Leave:
            self.status_bar.update()
            return True
        elif event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Escape and self.__processing:
                self.__processing = False
                return True

        return QtCore.QObject.eventFilter(self, widget, event)

    def load_repos(self, repos):
        self.repos = repos
        try:
            sc.CHECKS_REGISTRY.clear_registry()
            sc.SHARED_CONTEXTS_REGISTRY.clear_registry()
            for repo_path in self.repos:
                sc.load_sanitycheck_repo(Path(repo_path))
            self.checks_WIDGET.reset_widgets()
            self.checks_WIDGET.expand_all()
            self.checks_WIDGET.presets_WIDGET.load_presets_gui(self.repos)
        except (RepoError, ImplementationError):
            self.status_bar.update(
                "Failed to load repos! Please check log for more info.",
                eStatusType.warning,
            )

    def run_checks_options(self, pos):
        menu = QtWidgets.QMenu(self.run_checks_BTN)
        actions_label = QtWidgets.QLabel("<b>Actions</b>")
        actions_action = QtWidgets.QWidgetAction(menu)
        actions_action.setDefaultWidget(actions_label)
        menu.addAction(actions_action)
        run_selected = menu.addAction("Run selected")
        run_all = menu.addAction("Run All")

        menu.popup(self.run_checks_BTN.mapToGlobal(pos))

        # Actions
        run_selected.triggered.connect(self.checks_WIDGET.run_selected)
        run_all.triggered.connect(self.checks_WIDGET.run_all)

    def set_logging_level(self):
        for action in self.action_grp_levels.actions():
            if action.isChecked():
                if action.text() == "No log":
                    logger.set_level(logging.NOTSET)
                    logger_gui.set_level(logging.NOTSET)
                elif action.text() == "Critical":
                    logger.set_level(logging.CRITICAL)
                    logger_gui.set_level(logging.CRITICAL)
                elif action.text() == "Error":
                    logger.set_level(logging.ERROR)
                    logger_gui.set_level(logging.ERROR)
                elif action.text() == "Warning":
                    logger.set_level(logging.WARNING)
                    logger_gui.set_level(logging.WARNING)
                elif action.text() == "Info":
                    logger.set_level(logging.INFO)
                    logger_gui.set_level(logging.INFO)
                elif action.text() == "Debug":
                    logger.set_level(logging.DEBUG)
                    logger_gui.set_level(logging.DEBUG)
                break

    def start_logging_to_file(self):
        if self.log_to_file.isChecked():
            logger.log_to_file(logging.DEBUG)
            logger.set_level(logging.DEBUG)
            msg = f"Logging level set to 'Debug' and saving logs to {logger.get_log_file_path()}"
            logger.debug(msg)
            self.status_bar.update(msg, eStatusType.success)
        else:
            logger.set_level(self.DEFAULT_LOGGING_LEVEL)
            logger.stop_logging_to_file()
            msg = "Logging level set back to default and stopped saving logs to file."
            logger.debug(msg)
            self.status_bar.update(msg, eStatusType.success)

    def open_docs(self):
        docs_location = Path(f"V:/Pipe/DOCS/{self.TOOL_NAME}/index.html")
        if docs_location.exists():
            webbrowser.open(str(docs_location), new=2)
        else:
            msg = f"Documentation couldn't be found at {str(docs_location)}."
            logger_gui.error(msg)
            self.status_bar.update(msg, eStatusType.warning)


if __name__ == "__main__":
    pass
