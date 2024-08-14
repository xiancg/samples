from io import StringIO
from pprint import pprint
from pathlib import Path

from sanitychecker.sanitycheck import SanityCheck, SharedContext


class ChecksRegistry:
    """SanityCheck registry holds all SanityCheck instances that have been generated.
    This is implemented to aid in reloading all repos and checks without having to restart the application.

    The registry structure is as follows:

    repo_path: {
        py_module: [SanityCheck1, SanityCheck2]
    }

    """
    def __init__(self):
        self.__checks = {}

    def get_check(self, check_name: str, repo_path: Path = None):
        """Get a SanityCheck instance by name and repo.

        Args:
            check_name (str): SanityCheck name

            repo_path (Path, optional): If repo is passed, the check will be searched in it only.
            Defaults to None.

        Returns:
            SanityCheck or None: SanityCheck instance if found, None otherwise.
        """
        if not repo_path:
            repo_checks = self.get_all_checks()
            for check in repo_checks:
                if check.name == check_name:
                    return check
        elif repo_path in self.__checks:
            repo_checks = self.get_checks_by_repo(repo_path)
            for check in repo_checks:
                if check.name == check_name:
                    return check
        return None

    def get_all_checks(self):
        """Get all registered checks

        Returns:
            list: List of SanityCheck instances.
        """
        all_checks = []
        for repo_path, repo_data in self.__checks.items():
            for py_module, checks in repo_data.items():
                all_checks.extend(checks)
        return all_checks

    def get_checks_by_repo(self, repo_path: Path):
        """Get all checks of a particular repo.

        Args:
            repo_path (Path): Repository path

        Returns:
            list: List of SanityCheck instances.
        """
        result = []
        for py_module, checks in self.__checks.get(repo_path, {}).items():
            result.extend(checks)
        return result

    def add_check(self, check: SanityCheck, py_module: str, repo_path: Path):
        """Add check to register

        Args:
            check (SanityCheck): Sanity check instance to add.

            py_module (str): Python module name where the SanityCheck instance is defined.

            repo_path (Path): Repository path where py_module is located.
        """
        checks = self.__checks.get(repo_path, {})
        checks[py_module] = check
        self.__checks[repo_path] = checks

    def extend_checks(self, checks: list, py_module: str, repo_path: Path):
        """Extend checks of a particular repo.

        Args:
            checks (list): List of SanityCheck instances to add.

            py_module (str): Python module name where the SanityCheck instances are defined.

            repo_path (Path): Repository path where py_module is located.
        """
        repo_data = self.__checks.get(repo_path, {})
        repo_data[py_module] = checks
        self.__checks[repo_path] = repo_data

    def remove_check(self, check: SanityCheck, repo_path: Path):
        """Remove a particular check from a repo in the register.

        Args:
            check (SanityCheck): Sanity check instance to remove.
            repo_path (Path): Repository path where the SanityCheck instance is located.
        """
        checks = self.__checks.get(repo_path, [])
        if check in checks:
            checks.remove(check)
            self.__checks[repo_path] = checks

    def clear_registry(self):
        """Clear the registry, useful for reloading all repos.
        """
        self.__checks.clear()

    @property
    def checks(self):
        return self.__checks

    @checks.setter
    def checks(self, checks: dict):
        self.__checks = checks

    def __str__(self):
        placeholder = StringIO()
        pprint(self.__checks, stream=placeholder, compact=True)
        result = placeholder.getvalue()
        placeholder.close()
        return result

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return len(self.get_all_checks())

    def __iter__(self):
        return iter(self.get_all_checks())


class SharedContextsRegistry:
    """SharedContexts registry holds all SharedContext instances that have been generated.
    This is implemented to aid in reloading all repos and SharedContexts
    without having to restart the application.

    The registry structure is as follows:

    repo_path: {
        py_module: [SharedContext1, SharedContext2]
    }

    """
    def __init__(self):
        self.__contexts = {}

    def get_context(self, context_name: str, repo_path: Path = None):
        """Get a SharedContext instance by name and repo.

        Args:
            check_name (str): SharedContext name

            repo_path (Path, optional): If repo is passed, the check will be searched in it only.

            Defaults to None.

        Returns:
            SharedContext or None: SharedContext instance if found, None otherwise.
        """
        if not repo_path:
            repo_contexts = self.get_all_contexts()
            for context in repo_contexts:
                if context.name == context_name:
                    return context
        elif repo_path in list(self.__contexts.keys()):
            repo_context = self.get_contexts_by_repo(repo_path)
            for context in repo_context:
                if context.name == context_name:
                    return context
        return None

    def get_all_contexts(self):
        """Get all registered contexts

        Returns:
            list: List of SharedContext instances.
        """
        all_contexts = []
        for repo_path, repo_data in self.__contexts.items():
            for py_module, contexts in repo_data.items():
                all_contexts.extend(contexts)
        return all_contexts

    def get_contexts_by_repo(self, repo_path: Path):
        """Get all contexts of a particular repo.

        Args:
            repo_path (Path): Repository path

        Returns:
            list: List of SharedContext instances.
        """
        result = []
        for py_module, contexts in self.__contexts.get(repo_path, {}).items():
            result.extend(contexts)
        return result

    def add_context(self, context: SanityCheck, py_module: str, repo_path: Path):
        """Add SharedContext to register

        Args:
            check (SharedContext): SharedContext instance to add.
            py_module (str): Python module name where the SharedContext instance is defined.
            repo_path (Path): Repository path where py_module is located.
        """
        contexts = self.__contexts.get(repo_path, {})
        contexts[py_module] = context
        self.__contexts[repo_path] = contexts

    def extend_contexts(self, contexts: list, py_module: str, repo_path: Path):
        """Extend SharedContexts of a particular repo.

        Args:
            checks (list): List of SharedContext instances to add.
            py_module (str): Python module name where the SharedContext instances are defined.
            repo_path (Path): Repository path where py_module is located.
        """
        repo_data = self.__contexts.get(repo_path, {})
        repo_data[py_module] = contexts
        self.__contexts[repo_path] = repo_data

    def remove_context(self, context: SharedContext, repo_path: Path):
        """Remove a particular SharedContext from a repo in the register.

        Args:
            check (SharedContext): SharedContext instance to remove.
            repo_path (Path): Repository path where the SharedContext instance is located.
        """
        contexts = self.__contexts.get(repo_path, [])
        if contexts in contexts:
            contexts.remove(context)
            self.__contexts[repo_path] = contexts

    def clear_registry(self):
        """Clear the registry, useful for reloading all repos.
        """
        self.__contexts.clear()

    @property
    def contexts(self):
        return self.__contexts

    @contexts.setter
    def contexts(self, contexts: dict):
        self.__contexts = contexts

    def __str__(self):
        placeholder = StringIO()
        pprint(self.__contexts, stream=placeholder, compact=True)
        result = placeholder.getvalue()
        placeholder.close()
        return result

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return len(self.get_all_contexts())

    def __iter__(self):
        return iter(self.get_all_contexts())
