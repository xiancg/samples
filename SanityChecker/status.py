from typing import List

from sanitychecker.statussignal import StatusSignal
from sanitychecker.error import ImplementationError


class CheckStatus:
    passed = 0
    not_passed = 1
    failed = 2
    cancelled = 3
    not_ran = 4
    running = 5

    def __init__(self, code: int, message: str = None):
        """Constructor for CheckStatus.

        Args:
            code (int): Valid values are:
                0: passed
                1: not_passed
                2: failed
                3: cancelled
                4: not_ran
                5: running
            message (str): Custom message to be displayed with the status if required.
        """
        if self.__is_status_valid(code):
            self.__code = code
        if message:
            self.__message: List = [message]
        else:
            self.__message: List = []
        self.signal = StatusSignal()

    def status_as_string(self, status_code: int = -1) -> str:
        """Get the given status as its string equivalent.

        Args:
            status_code (int): Valid values are:
                0: passed
                1: not_passed
                2: failed
                3: cancelled
                4: not_ran
                5: running

        Returns:
            str: Status as its string equivalent
        """
        if status_code == -1:
            status_code = self.__code

        switcher = {
            self.passed: "passed",
            self.not_passed: "not_passed",
            self.failed: "failed",
            self.cancelled: "cancelled",
            self.not_ran: "not_ran",
            self.running: "running",
        }
        try:
            return switcher[status_code]
        except KeyError:
            raise ImplementationError(f"Invalid status code value '{status_code}'.")

    def __is_status_valid(self, code: int) -> bool:
        """Validate the given status code.

        Args:
            code (int): Integer value representing the status code.

        Raises:
            ImplementationError: If the given status code is invalid.

        Returns:
            bool: True if valid.
        """
        if code not in range(6):
            raise ImplementationError(f"Invalid status code value '{code}'.")
        return True

    def updated(self):
        """We can't generate a signal from this class without making a QObject,
        so we use this method to emit a signal when the status is updated.
        """
        if isinstance(self.signal, StatusSignal):
            self.signal.updated.emit()

    @property
    def code(self) -> int:
        return self.__code

    @code.setter
    def code(self, code: int):
        if self.__is_status_valid(code):
            self.__code = code
            self.updated()

    @property
    def message(self) -> str:
        return "\n.".join(self.__message)

    @property
    def msg(self) -> str:
        return "\n.".join(self.__message)

    @message.setter
    def message(self, m: str):
        self.__message.append(m)
        self.updated()

    @msg.setter
    def msg(self, m: str):
        self.__message.append(m)
        self.updated()

    def add_message(self, m: str):
        self.__message.append(m)
        self.updated()

    def add_msg(self, m: str):
        self.__message.append(m)
        self.updated()

    def __str__(self) -> str:
        return f"{self.status_as_string().capitalize()}"

    def __repr__(self) -> str:
        return f"{self.status_as_string().capitalize()}"

    def __eq__(self, other) -> bool:
        if isinstance(other, CheckStatus):
            return self.__code == other.__code
        return False

    def __ne__(self, other) -> bool:
        if isinstance(other, CheckStatus):
            return self.__code != other.__code
        return True

    def __len__(self) -> int:
        return len(self.__message)

    def __hash__(self) -> int:
        return hash(f"{self.__code}{tuple(self.__message)}")


class ContextStatus:
    ready = 0
    not_ready = 1
    failed = 2
    cancelled = 3
    finished = 4

    def __init__(self, code: int, message: str = None):
        """Constructor for CheckStatus.

        Args:
            code (int): Valid values are:
                0: ready
                1: not_ready
                2: failed
                3: cancelled
                4: finished
            message (str): Custom message to be displayed with the status if required.
        """
        self.__code = self.not_ready
        if self.__is_status_valid(code):
            self.__code = code
        if message:
            self.__message: List = [message]
        else:
            self.__message: List = []
        self.signal = StatusSignal()

    def status_as_string(self, status_code: int = -1) -> str:
        """Get the given status as its string equivalent.

        Args:
            status_code (int): Valid values are:
                0: ready
                1: not_ready
                2: failed
                3: cancelled
                4: finished

        Returns:
            str: Status as its string equivalent
        """
        if status_code == -1:
            status_code = self.__code
        switcher = {
            self.ready: "ready",
            self.not_ready: "not_ready",
            self.failed: "failed",
            self.cancelled: "cancelled",
            self.finished: "finished",
        }
        try:
            return switcher[status_code]
        except KeyError:
            raise ImplementationError(f"Invalid status code value '{status_code}'.")

    def __is_status_valid(self, code: int) -> bool:
        """Validate the given status code.

        Args:
            code (int): Integer value representing the status code.

        Raises:
            ImplementationError: If the given status code is invalid.

        Returns:
            bool: True if valid.
        """
        if code not in range(5):
            raise ImplementationError(f"Invalid status code value '{code}'.")
        return True

    def updated(self):
        """We can't generate a signal from this class without making a QObject,
        so we use this method to emit a signal when the status is updated.
        """
        if isinstance(self.signal, StatusSignal):
            self.signal.updated.emit()

    @property
    def code(self) -> int:
        return self.__code

    @code.setter
    def code(self, code: int):
        if self.__is_status_valid(code):
            self.__code = code
            self.updated()

    @property
    def message(self) -> str:
        return "\n.".join(self.__message)

    @property
    def msg(self) -> str:
        return "\n.".join(self.__message)

    @message.setter
    def message(self, m: str):
        self.__message.append(m)
        self.updated()

    @msg.setter
    def msg(self, m: str):
        self.__message.append(m)
        self.updated()

    def __str__(self) -> str:
        return f"{self.status_as_string().capitalize()}"

    def __repr__(self) -> str:
        return f"{self.status_as_string().capitalize()}"

    def __eq__(self, other) -> bool:
        if isinstance(other, ContextStatus):
            return self.__code == other.__code
        return False

    def __ne__(self, other) -> bool:
        if isinstance(other, ContextStatus):
            return self.__code != other.__code
        return True

    def __len__(self) -> int:
        return len(self.__message)

    def __hash__(self) -> int:
        return hash(f"{self.__code}{tuple(self.__message)}")


if __name__ == "__main__":
    pass
