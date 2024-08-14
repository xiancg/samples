from pathlib import Path

from sanitychecker.checkrepo import (
    load_sanitycheck_repo, register_check_with_context,
    CHECKS_REGISTRY
)
from pysideutils import ProgressInterface
from sanitychecker.sanitycheck import SanityCheck
from sanitychecker.logger import logger


__progress_interface = ProgressInterface()


def run_checks_from_repo(repo_path: Path, try_fix: bool = True) -> list:
    """Run all checks from a repo (a directory containing modules with classes that implement SanityCheck)

    Args:
        repo_path (Path): Path object to the repo directory.
        try_fix (bool, optional): Try to fix if a fix has been implemented. Defaults to True.

    Returns:
        tuple: [0]List of SanityCheck instances that have been run.
        [1]List of SharedContext instances that have been run.
    """
    checks, contexts = load_sanitycheck_repo(repo_path)
    return run_checks(checks, contexts, try_fix)


def run_checks(checks: list = [], contexts: list = [], try_fix: bool = True) -> list:
    """Run all given checks.

    Args:
        checks (list): SanityCheck instances to run.
        contexts (list, optional): SharedContext instances to run.
        try_fix (bool, optional): Try to fix if a fix has been implemented. Defaults to True.

    Returns:
        tuple: [0]List of SanityCheck instances that have been run.
        [1]List of SharedContext instances that have been run.
    """
    # Run all contexts first
    logger.debug("Running all shared contexts and their checks.")
    checks_runned_by_contexts = []

    __progress_interface.reset_progress()
    if len(contexts):
        __progress_interface.maximum = len(contexts)
    for context in contexts:
        context.run_full_context()
        checks_runned_by_contexts.extend(context.checks)
        __progress_interface.add_progress()

    # Skip checks that have dependencies and run them later
    checks_with_dependencies = []
    logger.debug("Running checks without dependencies or contexts.")
    __progress_interface.reset_progress()
    if len(checks):
        __progress_interface.maximum = len(checks)
    for check in checks:
        if check not in checks_runned_by_contexts:
            if not check.has_dependencies():
                check.run_full_check(try_fix)
            else:
                checks_with_dependencies.append(check)
        __progress_interface.add_progress()

    logger.debug("Running checks with dependencies and no context.")
    __progress_interface.reset_progress()
    if len(checks_with_dependencies):
        __progress_interface.maximum = len(checks_with_dependencies)
    for check in checks_with_dependencies:
        if check not in checks_runned_by_contexts:
            check.run_full_check(try_fix, run_dependencies_first=True)
        __progress_interface.add_progress()

    return checks, contexts


def run_check(check_name: str, repo_path: Path, try_fix: bool = True) -> SanityCheck:
    """Run a specific check from a repo.

    Args:
        check_name (str): Name of the check to run.
        repo_path (Path): Path object to the repo directory.
        try_fix (bool, optional): Try to fix if a fix has been implemented. Defaults to True.

    Returns:
        SanityCheck: The SanityCheck instance that has been run.
        None if the check or its context were not found.
    """
    load_sanitycheck_repo(repo_path)
    check = CHECKS_REGISTRY.get_check(check_name, repo_path)
    if check:
        if check.shared_context:
            found_context = register_check_with_context(check)
            if found_context:
                check.run_full_check(try_fix)
                return check
            else:
                logger.warning(
                    f"Context {check.shared_context} not found in contexts register. "
                    f"Not possible to run {check.name}."
                )
        else:
            check.run_full_check(try_fix)
            return check
    else:
        logger.warning(f"Check {check_name} not found in repo {repo_path}")

    return


def get_progress_interface():
    return __progress_interface


if __name__ == "__main__":
    pass
