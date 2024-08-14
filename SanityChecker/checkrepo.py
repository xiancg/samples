import inspect
import traceback
import sys
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

from sanitychecker.sanitycheck import SanityCheck, SharedContext
from sanitychecker.registry import ChecksRegistry, SharedContextsRegistry
from sanitychecker.logger import logger, logger_gui
from sanitychecker.error import RepoError


CHECKS_REGISTRY = ChecksRegistry()
SHARED_CONTEXTS_REGISTRY = SharedContextsRegistry()


def load_sanitycheck_repo(repo_path: Path) -> list:
    """Load all checks from a repo.

    Args:
        repo_path (Path): Path object to the repo directory.

    Raises:
        RepoError: If the repo path doesn't exist or is invalid.

    Returns:
        tuple: [0] List of SanityCheck instances found in repo in no particular order.
        [1] List of SharedContext instances found in repo in no particular order.

    """
    if not repo_path.exists() or not repo_path.is_dir():
        msg = f"Invalid repo path. Make sure the directory exists. {repo_path}"
        logger_gui.exception(f"EXCEPTION: {msg}")
        raise RepoError(msg)

    num_checks = 0
    num_contexts = 0
    for py_module in repo_path.glob('**/*.py'):
        if not (py_module.name.startswith('__') or py_module.is_dir()):
            logger_gui.debug(f"Loading checks from {py_module}")
            module_checks, module_contexts = __get_classes_from_module(py_module)
            CHECKS_REGISTRY.extend_checks(module_checks, py_module.name, repo_path)
            SHARED_CONTEXTS_REGISTRY.extend_contexts(module_contexts, py_module.name, repo_path)
            num_checks += len(module_checks)
            num_contexts += len(module_contexts)
    logger_gui.info(
        f"Finished loading {num_checks} checks and {num_contexts} contexts from repo {repo_path}."
    )

    # Set the context for each check that has a shared context from a single context instance
    for check in CHECKS_REGISTRY:
        if type(check.shared_context) is str:
            found_context = register_check_with_context(check)
            if not found_context:
                CHECKS_REGISTRY.remove_check(check, repo_path)
        if check.has_dependencies():
            register_dependencies(check)
    return (
        CHECKS_REGISTRY.get_checks_by_repo(repo_path),
        SHARED_CONTEXTS_REGISTRY.get_contexts_by_repo(repo_path)
    )


def register_check_with_context(check: SanityCheck):
    """ Register a check with a shared context.

    Args:
        check (SanityCheck): Check to register.

    Returns:
        bool: True if the context was found and check was registered, False otherwise.
    """
    found_context = False
    if isinstance(check.shared_context, SharedContext):
        found_context = True
    else:
        for context in SHARED_CONTEXTS_REGISTRY:
            if check.shared_context == context.name:
                check.shared_context = context
                context.add_check(check)
                found_context = True
                break
    if not found_context:
        logger.warning(
            f"Check '{check.name}' is trying to invoke a "
            f"shared context '{check.shared_context}' that has not been registered. "
            f"Please check the spelling of the shared context name."
        )
    return found_context


def register_dependencies(check: SanityCheck):
    """Register dependencies for a check.

    Args:
        check (SanityCheck): Check to register dependencies for.
    """
    for sanity_check in CHECKS_REGISTRY:
        if sanity_check.name in check.dependencies_names:
            check.add_dependency(sanity_check)


def __get_classes_from_module(py_module: Path) -> list:
    """Get all checks and contexts from a module.

    Args:
        py_module (Path): Path object to the module.

    Returns:
        tuple: SanityCheck instanced, SharedContext instances.
    """
    check_classes = []
    context_classes = []
    try:
        spec = spec_from_file_location(py_module.name, py_module)
        check_module = module_from_spec(spec)
        sys.modules[py_module.name] = check_module
        spec.loader.exec_module(check_module)
        class_members = inspect.getmembers(check_module, inspect.isclass)
    except Exception:
        exception_traceback = traceback.format_exc()
        logger_gui.exception(
            f"Failed to load classes from module {py_module.name}\n{exception_traceback}"
        )
        return check_classes, context_classes

    if len(class_members) == 0:
        return check_classes, context_classes

    skip_imported_statements = []
    for class_member in class_members:
        if class_member[0] not in skip_imported_statements:
            if issubclass(class_member[1], SharedContext):
                if is_context_class_valid(class_member[1]):
                    logger.debug(f"Valid context: {class_member[0]}")
                    try:
                        context_classes.append(class_member[1]())
                    except Exception:
                        exception_traceback = traceback.format_exc()
                        logger_gui.exception(
                            f"EXCEPTION: Couldn't instantiate context class. \n{exception_traceback}"
                        )
                    skip_imported_statements.append(class_member[0])
                else:
                    logger.debug(f"Invalid context: {class_member[0]}")
            if issubclass(class_member[1], SanityCheck):
                if is_check_class_valid(class_member[1]):
                    logger.debug(f"Valid check: {class_member[0]}")
                    try:
                        check_classes.append(class_member[1]())
                    except Exception:
                        exception_traceback = traceback.format_exc()
                        logger_gui.exception(
                            f"EXCEPTION: Couldn't instantiate check class. \n{exception_traceback}"
                        )
                    skip_imported_statements.append(class_member[0])
                else:
                    logger.debug(f"Invalid check: {class_member[0]}")

    return check_classes, context_classes


def is_context_class_valid(context: SharedContext) -> list:
    """Validate if a SharedContext subclass is correctly implemented.
    If given context is not a subclass of SharedContext, it won't validate the rest of the requirements.

    Args:
        check (SharedContext): SharedContext subclass to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    # ! Validate if context is subclass first and foremost
    if not issubclass(context, SharedContext) or SharedContext.is_base_SharedContext(context):
        logger.debug(f"Invalid check. Expected SharedContext subclass, got {type(context)}")
        return False

    validation_warning = False
    setup_method = getattr(context, "_setup", None)
    if not setup_method:
        logger.debug(
            f"Invalid context {context.__class__.__name__}. Setup method is empty."
        )
        validation_warning = True
    else:
        if not callable(context._setup):
            logger.debug(
                f"Invalid context {context.__class__.__name__}. Setup function is not callable."
            )
            validation_warning = True

    if validation_warning:
        return False
    return True


def is_check_class_valid(check: SanityCheck) -> bool:
    """Validate if a SanityCheck subclass is correctly implemented.
    If given check is not a subclass of SanityCheck, it won't validate the rest of the requirements.

    Args:
        check (SanityCheck): SanityCheck subclass to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    # ! Validate if check is subclass first and foremost
    if not issubclass(check, SanityCheck) or SanityCheck.is_base_SanityCheck(check):
        logger.debug(f"Invalid check. Expected SanityCheck subclass, got {type(check)}")
        return False

    validation_warning = False
    check_method = getattr(check, "_check", None)
    if not check_method:
        logger.debug(
            f"Invalid check {check.__class__.__name__}. Check method is empty."
        )
        validation_warning = True
    else:
        if not callable(check._check):
            logger.debug(
                f"Invalid check {check.__class__.__name__}. Check function is not callable."
            )
            validation_warning = True

    if validation_warning:
        return False
    return True


if __name__ == "__main__":
    pass
