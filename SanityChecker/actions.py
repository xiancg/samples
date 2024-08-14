import abc
import traceback

from sanitychecker.error import ImplementationError
from sanitychecker.logger import logger, logger_gui


class Action(abc.ABC):
    DESCRIPTION_CHAR_LIMIT = 140
    NAME_CHAR_LIMIT = 50

    def __init__(self):
        super(Action, self).__init__()
        self.__name = ""
        self.__description = ""

    @abc.abstractmethod
    def _execute(self):
        """The _execute method must be implemented by any subclass.
        This method shouldn't be called directly, but from run_action().
        """
        raise NotImplementedError(
            f"_execute() method implementation it's mandatory but is missing from {self.__class__.__name__}"
        )

    def run_action(self):
        """Encapsulates and runs the _execute method so if it fails,
        it's communicated but it doesn't interrupt the application.
        """
        if self.has_execute():
            try:
                self._execute()
            except Exception:
                exception_traceback = traceback.format_exc()
                base_msg = f"Unhandled exception raised running {self.name}._execute()"
                logger_gui.exception(f"EXCEPTION: {base_msg}\n{exception_traceback}")

        else:
            logger.debug(f"WARNING: Action {self.name} has no _execute() method implemented")

    def has_execute(self) -> bool:
        """Subclass has an _execute method implemented.

        Returns:
            bool: True if _execute method is implemented, False otherwise.
        """
        return type(self)._execute != Action._execute

    @property
    def name(self) -> str:
        """If name is not set, return the class name.

        Returns:
            str: Action name.
        """
        if self.__name:
            return self.__name
        return self.__class__.__name__

    @name.setter
    def name(self, n: str):
        f"""Set the name of the Action.

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
        f"""Set the description of the Action.

        Raises:
            ImplementationError: If description is longer than
            DESCRIPTION_CHAR_LIMIT={self.DESCRIPTION_CHAR_LIMIT}.
        """
        if len(d) > self.DESCRIPTION_CHAR_LIMIT:
            raise ImplementationError(
                f"Description must be less than {self.DESCRIPTION_CHAR_LIMIT} characters."
            )
        self.__description = d
