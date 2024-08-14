import abc
import traceback
from pysideutils.progress import ProgressInterface

from sanitychecker.status import CheckStatus, ContextStatus
from sanitychecker.error import ImplementationError
from sanitychecker.logger import logger, logger_gui


class SanityCheck(abc.ABC):
    DESCRIPTION_CHAR_LIMIT = 140
    NAME_CHAR_LIMIT = 50
    PRIORITY_MIN = 0
    PRIORITY_MAX = 100

    def __init__(self):
        """Base class for all checks."""
        self.__name = ""
        self.__description = ""
        self.__priority = 0
        self.__status = CheckStatus(CheckStatus.not_ran)
        self.__dependencies_instances = []
        self.__dependencies_names = []
        self.__shared_context = None
        self.__actions = []
        self.progress = ProgressInterface()

    @abc.abstractmethod
    def _check(self):
        """The check method must be implemented by any subclass.
        This method shouldn't be called directly, but from run_check().
        It's even better to use run_full_check().
        """
        raise NotImplementedError(
            f"_check() method implementation it's mandatory but is missing from {self.__class__.__name__}"
        )

    def _fix(self):
        """If an automatic is possible, it should be implemented here.
        This method shouldn't be called directly, but from run_fix().
        It's even better to use run_full_check().
        """
        logger.debug(
            f"No _fix() method implemented for this check {self.__class__.__name__}."
        )

    def _setup(self):
        """If a setup is needed for running the check, it should be implemented here.
        This method shouldn't be called directly, but from run_setup().
        It's even better to use run_full_check().
        """
        logger.debug(
            f"No _setup() method implemented for this check {self.__class__.__name__}."
        )

    def _teardown(self):
        """If a teardown or cleanup is needed after running the check, it should be implemented here.
        This method shouldn't be called directly, but from run_teardown().
        It's even better to use run_full_check().
        """
        logger.debug(
            f"No _teardown() method implemented for this check {self.__class__.__name__}."
        )

    def run_full_check(self, try_fix=True, run_dependencies_first=True) -> CheckStatus:
        """Run the full check, including setup, check, teardown and fix if implemented.

        Args:
            try_fix (bool, optional): Try to fix if a fix has been implemented. Defaults to True.
            run_dependencies_first (bool, optional): Make sure all dependencies are run and passed first.
            Defaults to True.

        Returns:
            CheckStatus: CheckStatus of the current check.
        """
        if run_dependencies_first:
            self.run_denpendencies()

        # If context is not ready it means we're running the check directly and not from the context itself
        context_ran_from_check = False
        if self.has_shared_context():
            if not self.__shared_context.is_ready():
                self.__shared_context.run_setup()
                context_ran_from_check = True

        # First check
        self.__status = self.run_setup()
        self.__status = self.run_check()
        self.__status = self.run_teardown()

        # Try to fix then check again
        if self.__status.code != CheckStatus.passed and try_fix and self.has_fix():
            self.__status = self.run_fix()
            # Final check
            self.__status = self.run_setup()
            self.__status = self.run_check()
            self.__status = self.run_teardown()

        if context_ran_from_check:
            self.__shared_context.run_teardown()

        return self.__status

    def run_check(self) -> CheckStatus:
        """Encapsulates and runs the _check method so if it fails,
        it's communicated but it doesn't interrupt the application.

        Returns:
            CheckStatus: CheckStatus of the current check.
        """
        if not self.validate_dependencies_status():
            self.__status.code = CheckStatus.cancelled
            base_msg = f"Dependencies for {self.name} failed or haven't passed."
            self.__status.message = base_msg
            return self.__status

        try:
            self._check()
        except Exception:
            exception_traceback = traceback.format_exc()
            base_msg = f"Unhandled exception raised running {self.name}.check()"
            logger_gui.exception(f"EXCEPTION: {base_msg}\n{exception_traceback}")
            self.__status.code = CheckStatus.failed
            self.__status.message = base_msg
        return self.__status

    def run_fix(self) -> CheckStatus:
        """Encapsulates and runs the _fix method so if it fails,
        it's communicated but it doesn't interrupt the application.

        Returns:
            CheckStatus: CheckStatus of the current check.
        """
        if self.has_fix():
            try:
                self._fix()
            except Exception:
                exception_traceback = traceback.format_exc()
                base_msg = f"Unhandled exception raised running {self.name}.fix()"
                logger_gui.exception(f"EXCEPTION: {base_msg}\n{exception_traceback}")
                self.__status.code = CheckStatus.failed
                self.__status.message = base_msg
        return self.__status

    def run_setup(self) -> CheckStatus:
        """Encapsulates and runs the _setup method so if it fails,
        it's communicated but it doesn't interrupt the application.

        Returns:
            CheckStatus: CheckStatus of the current check.
        """
        if self.has_setup():
            try:
                self._setup()
            except Exception:
                exception_traceback = traceback.format_exc()
                base_msg = f"Unhandled exception raised running {self.name}.setup()"
                logger_gui.exception(f"EXCEPTION: {base_msg}\n{exception_traceback}")
                self.__status.code = CheckStatus.failed
                self.__status.message = base_msg
        return self.__status

    def run_teardown(self) -> CheckStatus:
        """Encapsulates and runs the _teardown method so if it fails,
        it's communicated but it doesn't interrupt the application.

        Returns:
            CheckStatus: CheckStatus of the current check.
        """
        if self.has_teardown():
            try:
                self._teardown()
            except Exception:
                exception_traceback = traceback.format_exc()
                base_msg = f"Unhandled exception raised running {self.name}.teardown()"
                logger_gui.exception(f"EXCEPTION: {base_msg}\n{exception_traceback}")
                self.__status.code = CheckStatus.failed
                self.__status.message = base_msg
        return self.__status

    def add_dependency(self, check):
        """Add a dependency to the current check.

        Args:
            check (str): SanityCheck name to add as dependency.

        Raises:
            ImplementationError: If the dependency is not a SanityCheck object.
        """
        if isinstance(check, SanityCheck):
            self.__dependencies_instances.append(check)
        else:
            raise ImplementationError(
                f"Dependency must be a SanityCheck object, not {type(check)}"
            )

    def validate_dependencies_status(self) -> bool:
        """Check if all dependencies have passed.

        Returns:
            True if all dependencies have passed, False otherwise.
        """
        for check in self.__dependencies_instances:
            if check.status.code != CheckStatus.passed:
                return False
        return True

    def run_denpendencies(self):
        """Runs all dependencies that haven't passed yet."""
        for check in self.__dependencies_instances:
            if check.status.code != CheckStatus.passed:
                check_status = check.run_full_check()
                if check_status.code != CheckStatus.passed:
                    self.__status.code = CheckStatus.cancelled
                    base_msg = f"Dependencies for {self.name} failed or haven't passed."
                    self.__status.message = base_msg
                    return self.__status

    def register_actions(self, actions=[]):
        """Register actions that the user can execute from the GUI.

        Args:
            actions (list, optional): List of Actions. Defaults to [].
        """
        for action in actions:
            self.__actions.append(action)

    def has_check(self) -> bool:
        """Subclass has a _check method implemented.

        Returns:
            bool: True if _check method is implemented, False otherwise.
        """
        return type(self)._check != SanityCheck._check

    def has_fix(self) -> bool:
        """Subclass has a _fix method implemented.

        Returns:
            bool: True if _fix method is implemented, False otherwise.
        """
        return type(self)._fix != SanityCheck._fix

    def has_setup(self) -> bool:
        """Subclass has a _setup method implemented.

        Returns:
            bool: True if _setup method is implemented, False otherwise.
        """
        return type(self)._setup != SanityCheck._setup

    def has_teardown(self) -> bool:
        """Subclass has a _teardown method implemented.

        Returns:
            bool: True if _teardown method is implemented, False otherwise.
        """
        return type(self)._teardown != SanityCheck._teardown

    def has_shared_context(self):
        """True if heck needs a shared context setup to run.

        Returns:
            bool: True if check needs a shared context setup to run, False otherwise.
        """
        if self.__shared_context is None:
            return False
        elif not isinstance(self.__shared_context, SharedContext):
            logger.debug(
                f"Check {self.name} is trying to invoke a "
                f"shared context {self.shared_context} that has not been loaded. "
                f"Please check the spelling of the shared context name."
            )
            return False
        return True

    def has_dependencies(self) -> bool:
        """Check if the current check has dependencies.

        Returns:
            bool: True if the current check has dependencies, False otherwise.
        """
        return (
            len(self.__dependencies_instances) > 0 or len(self.__dependencies_names) > 0
        )

    @staticmethod
    def is_base_SanityCheck(cls) -> bool:
        """Get if cls is the base SanityCheck class or an implementation."""
        try:
            return abc.ABC in cls.__bases__
        except AttributeError:
            return False

    @property
    def name(self) -> str:
        """If name is not set, return the class name.

        Returns:
            str: SanityCheck name.
        """
        if self.__name:
            return self.__name
        return self.__class__.__name__

    @name.setter
    def name(self, n: str):
        f"""Set the name of the SanityCheck.

        Raises:
            ImplementationError: If name is longer than NAME_CHAR_LIMIT={self.NAME_CHAR_LIMIT}.
        """
        if len(n) > self.NAME_CHAR_LIMIT:
            raise ImplementationError(
                f"Name must be less than {self.NAME_CHAR_LIMIT} characters."
            )
        self.__name = n

    @property
    def description(self) -> str:
        return self.__description

    @description.setter
    def description(self, d: str):
        f"""Set the description of the SanityCheck.

        Raises:
            ImplementationError: If description is longer than
            DESCRIPTION_CHAR_LIMIT={self.DESCRIPTION_CHAR_LIMIT}.
        """
        if len(d) > self.DESCRIPTION_CHAR_LIMIT:
            raise ImplementationError(
                f"Description must be less than {self.DESCRIPTION_CHAR_LIMIT} characters."
            )
        self.__description = d

    @property
    def shared_context(self):
        """Shared context for this check. Note that SharedContexts are first declared
        by their name and only instanced at runtime so type here might be a string or a SharedContext object.

        Returns:
            SharedContext or str: SharedContext or string with the name of the SharedContext.
        """
        return self.__shared_context

    @shared_context.setter
    def shared_context(self, sc):
        self.__shared_context = sc

    @property
    def priority(self) -> int:
        return self.__priority

    @priority.setter
    def priority(self, p: int) -> int:
        f"""Set the priority of the SanityCheck.

        Raises:
            ImplementationError: If priority is not between
            PRIORITY_MIN={self.PRIORITY_MIN} and PRIORITY_MAX={self.PRIORITY_MAX}.
        """
        if self.PRIORITY_MIN < p > self.PRIORITY_MAX:
            raise ImplementationError(
                f"Priority must be between {self.PRIORITY_MIN} and {self.PRIORITY_MAX}, not {p}"
            )
        self.__priority = p

    @property
    def status(self) -> CheckStatus:
        return self.__status

    @status.setter
    def status(self, cs: CheckStatus):
        """Set CheckStatus of the SanityCheck. If super().__init__() was called correctly
        in the implementation, then a CheckStatus object will be already created. No need to create a new one.

        Args:
            cs (CheckStatus): A CheckStatus object.

        Raises:
            ImplementationError: If cs is not a CheckStatus object.
        """
        if isinstance(cs, CheckStatus):
            self.__status = cs
        else:
            raise ImplementationError(
                f"Status must be an eCheckStatus object, not {type(cs)}"
            )

    @property
    def dependencies_names(self) -> list:
        return self.__dependencies_names

    @dependencies_names.setter
    def dependencies_names(self, dependencies: list):
        self.__dependencies_names = dependencies

    @property
    def dependencies_instances(self) -> list:
        return self.__dependencies_instances

    @property
    def actions(self) -> list:
        return self.__actions

    def __repr__(self) -> str:
        return f"{self.name}: {self.__status.status_as_string()}"

    def __str__(self) -> str:
        return f"{self.name}: {self.__status.status_as_string()}"

    def __hash__(self) -> int:
        return hash(self.name)


class SharedContext(abc.ABC):
    """A class that can be used to share context between checks."""

    NAME_CHAR_LIMIT = 50
    DESCRIPTION_CHAR_LIMIT = 140

    def __init__(self):
        super().__init__()
        self.__name = ""
        self.__description = ""
        self.__status = ContextStatus(ContextStatus.not_ready)
        self.__checks = []
        self.__actions = []
        self.progress = ProgressInterface()

    @abc.abstractmethod
    def _setup(self):
        """If a setup is needed for running some checks, it should be implemented here.
        This method shouldn't be called directly, but from run_setup().
        It's even better to use run_full_check().
        """
        logger.debug(
            f"No _setup() method implemented for this check {self.__class__.__name__}."
        )

    def _teardown(self):
        """If a teardown or cleanup is needed after running the checks, it should be implemented here.
        This method shouldn't be called directly, but from run_teardown().
        It's even better to use run_full_check().
        """
        logger.debug(
            f"No _teardown() method implemented for this check {self.__class__.__name__}."
        )

    def run_full_context(self) -> ContextStatus:
        """Runs the setup, checks and teardown methods.

        Returns:
            ContextStatus: ContextStatus of the current check.
        """
        self.run_setup()
        self.run_checks()
        self.run_teardown()
        return self.__status

    def run_checks(self) -> ContextStatus:
        """Run all the checks in the context.

        Returns:
            ContextStatus: ContextStatus of the current check.
        """
        if self.is_ready():
            for check in self.__checks:
                check.run_full_check()
            if not self.__status.code == ContextStatus.failed:
                self.__status.code = ContextStatus.finished
                self.__status.message = (
                    f"Shared context {self.name} has finished running all checks."
                )
                logger.debug(self.__status.message)
        return self.__status

    def run_setup(self) -> ContextStatus:
        """Encapsulates and runs the _setup method so if it fails,
        it's communicated but it doesn't interrupt the application.

        Returns:
            ContextStatus: ContextStatus of the current check.
        """
        if self.has_setup():
            try:
                self._setup()
                self.__status.code = ContextStatus.ready
            except Exception:
                exception_traceback = traceback.format_exc()
                base_msg = f"Unhandled exception raised running {self.name}.setup()"
                logger_gui.exception(f"EXCEPTION: {base_msg}\n{exception_traceback}")
                self.__status.code = ContextStatus.failed
                self.__status.message = base_msg
        return self.__status

    def run_teardown(self) -> ContextStatus:
        """Encapsulates and runs the _teardown method so if it fails,
        it's communicated but it doesn't interrupt the application.

        Returns:
            ContextStatus: ContextStatus of the current check.
        """
        if self.has_teardown() and self.__status.code != ContextStatus.finished:
            try:
                self._teardown()
                self.__status.code = ContextStatus.finished
            except Exception:
                exception_traceback = traceback.format_exc()
                base_msg = f"Unhandled exception raised running {self.name}.teardown()"
                logger_gui.exception(f"EXCEPTION: {base_msg}\n{exception_traceback}")
                self.__status.code = ContextStatus.failed
                self.__status.message = base_msg
        return self.__status

    def is_ready(self) -> bool:
        """Check if the context is ready to run the checks.

        Returns:
            bool: True if ready, False otherwise.
        """
        return self.__status.code == ContextStatus.ready

    def has_finished(self) -> bool:
        """Check if the context has been finished.

        Returns:
            bool: True if finished, False otherwise.
        """
        return self.__status.code == ContextStatus.finished

    def has_setup(self) -> bool:
        """Subclass has a _setup method implemented.

        Returns:
            bool: True if _setup method is implemented, False otherwise.
        """
        return type(self)._setup != SharedContext._setup

    def has_teardown(self) -> bool:
        """Subclass has a _teardown method implemented.

        Returns:
            bool: True if _teardown method is implemented, False otherwise.
        """
        return type(self)._teardown != SharedContext._teardown

    def __validate_checks(self, checks: list):
        """Validate that all the checks are SanityCheck objects.

        Args:
            checks (list): List of SanityCheck objects.

        Raises:
            ImplementationError: If any of the checks is not a SanityCheck object.
        """
        for check in checks:
            if not issubclass(check, SanityCheck):
                raise ImplementationError(
                    f"Checks must be SanityCheck objects, not {type(check)}"
                )

    def add_check(self, check: SanityCheck):
        """Add a check to the context.

        Args:
            check (SanityCheck): SanityCheck object to be added to the context.
        """
        if isinstance(check, SanityCheck):
            if check not in self.__checks:
                self.__checks.append(check)
        else:
            raise ImplementationError(
                f"check object must be a SanityCheck object, not {type(check)}"
            )

    @staticmethod
    def is_base_SharedContext(cls) -> bool:
        """Get if cls is the base SharedContext class or an implementation."""
        try:
            return abc.ABC in cls.__bases__
        except AttributeError:
            return False

    def register_actions(self, actions=[]):
        """Register actions that the user can execute from the GUI.

        Args:
            actions (list, optional): List of Actions. Defaults to [].
        """
        for action in actions:
            self.__actions.append(action)

    @property
    def name(self) -> str:
        """If name is not set, return the class name.

        Returns:
            str: SanityCheck name.
        """
        if self.__name:
            return self.__name
        return self.__class__.__name__

    @name.setter
    def name(self, n: str):
        f"""Set the name of the SanityCheck.

        Raises:
            ImplementationError: If name is longer than NAME_CHAR_LIMIT={self.NAME_CHAR_LIMIT}.
        """
        if len(n) > self.NAME_CHAR_LIMIT:
            raise ImplementationError(
                f"Name must be less than {self.NAME_CHAR_LIMIT} characters."
            )
        self.__name = n

    @property
    def description(self) -> str:
        return self.__description

    @description.setter
    def description(self, d: str):
        f"""Set the description of the SanityCheck.

        Raises:
            ImplementationError: If description is longer than
            DESCRIPTION_CHAR_LIMIT={self.DESCRIPTION_CHAR_LIMIT}.
        """
        if len(d) > self.DESCRIPTION_CHAR_LIMIT:
            raise ImplementationError(
                f"Description must be less than {self.DESCRIPTION_CHAR_LIMIT} characters."
            )
        self.__description = d

    @property
    def status(self) -> ContextStatus:
        return self.__status

    @status.setter
    def status(self, cs: ContextStatus):
        """Set CheckStatus of the SanityCheck. If super().__init__() was called correctly
        in the implementation, then a CheckStatus object will be already created. No need to create a new one.

        Args:
            cs (ContextStatus): A ContextStatus object.

        Raises:
            ImplementationError: If cs is not a ContextStatus object.
        """
        if isinstance(cs, ContextStatus):
            self.__status = cs
        else:
            raise ImplementationError(
                f"Status must be a ContextStatus object, not {type(cs)}"
            )

    @property
    def checks(self) -> list:
        return self.__checks

    @checks.setter
    def checks(self, chks: list):
        if self.__validate_checks(chks):
            self.__checks = chks

    @property
    def actions(self) -> list:
        return self.__actions

    def __repr__(self) -> str:
        return f"{self.name}: {self.__status.status_as_string()}"

    def __str__(self) -> str:
        return f"{self.name}: {self.__status.status_as_string()}"


if __name__ == "__main__":
    pass
