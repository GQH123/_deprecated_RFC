""" Logging utilities."""

import inspect
import logging
import os
import sys
import threading
from logging import (
    CRITICAL,  # NOQA
    DEBUG,  # NOQA
    ERROR,  # NOQA
    FATAL,  # NOQA
    INFO,  # NOQA
    NOTSET,  # NOQA
    WARN,  # NOQA
    WARNING,  # NOQA
)
from typing import Optional


_lock = threading.Lock()
_default_handler: Optional[logging.Handler] = None

log_levels = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

_default_log_level = logging.INFO

_tqdm_active = True

__all__ = [
    "get_log_levels_dict",
    "get_logger",
    "get_verbosity",
    "set_verbosity",
    "set_verbosity_info",
    "set_verbosity_warning",
    "set_verbosity_debug",
    "set_verbosity_error",
    "disable_default_handler",
    "enable_default_handler",
    "add_handler",
    "remove_handler",
    "disable_propagation",
    "enable_propagation",
    "enable_explicit_format",
    "reset_format",
    "warning_advice",
]


class _RFCLogRecord(logging.LogRecord):
    """
    Custom LogRecord class with additional attributes.

    This class is used to override the `getMessage` method of the `LogRecord` class.
    """
    def __init__(self, name, level, pathname, lineno,
                 msg, args, exc_info, func=None, sinfo=None, **kwargs):
        super().__init__(name, level, pathname, lineno,
                         msg, args, exc_info, func, sinfo, **kwargs)
        try:
            st = inspect.stack()[5]
            self.last_funcName = st.function
            self.last_filename = os.path.split(st.filename)[-1]
            self.last_lineno = st.lineno
        except Exception:
            unknown = '<unknown>'
            self.last_funcName = unknown
            self.last_filename = unknown
            self.last_lineno = unknown


logging.setLogRecordFactory(_RFCLogRecord)


def _get_default_logging_level():
    """
    If RFC_VERBOSITY env var is set to one of the valid choices return that as the new default level. If it is
    not - fall back to `_default_log_level`
    """
    env_level_str = os.getenv("RFC_VERBOSITY", None)
    if env_level_str:
        if env_level_str in log_levels:
            return log_levels[env_level_str]
        else:
            logging.getLogger().warning(
                f"Unknown option RFC_VERBOSITY={env_level_str}, "
                f"has to be one of: { ', '.join(log_levels.keys()) }"
            )
    return _default_log_level


def _get_library_name() -> str:
    return __name__.split(".")[0]


def _get_library_root_logger() -> logging.Logger:
    return logging.getLogger(_get_library_name())


def _configure_library_root_logger() -> None:
    global _default_handler

    with _lock:
        if _default_handler:
            # This library has already configured the library root logger.
            return
        _default_handler = logging.StreamHandler()  # Set sys.stderr as stream.
        _default_handler.flush = sys.stderr.flush

        # Apply our default configuration to the library root logger.
        library_root_logger = _get_library_root_logger()
        library_root_logger.addHandler(_default_handler)
        library_root_logger.setLevel(_get_default_logging_level())
        library_root_logger.propagate = False


def _reset_library_root_logger() -> None:
    global _default_handler

    with _lock:
        if not _default_handler:
            return

        library_root_logger = _get_library_root_logger()
        library_root_logger.removeHandler(_default_handler)
        library_root_logger.setLevel(logging.NOTSET)
        _default_handler = None


def get_log_levels_dict():
    return log_levels


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Return a logger with the specified name.

    This function is not supposed to be directly accessed unless you are writing a custom RFC module.
    """
    
    if name is None:
        name = _get_library_name()

    # _configure_library_root_logger()
    logger = logging.getLogger(name)
    
    # _default_handler = logging.StreamHandler()  # Set sys.stderr as stream.
    # _default_handler.flush = sys.stderr.flush

    # Apply our default configuration to the library root logger.
    # logger.addHandler(_default_handler)
    logger.setLevel(_get_default_logging_level())
    logger.propagate = True
    
    return logger


def get_verbosity() -> int:
    """
    Return the current level for the RFC's root logger as an int.

    Returns:
        `int`: The logging level.

    <Tip>

    RFC has following logging levels:

    - 50: `RFC.logging.CRITICAL` or `RFC.logging.FATAL`
    - 40: `RFC.logging.ERROR`
    - 30: `RFC.logging.WARNING` or `RFC.logging.WARN`
    - 20: `RFC.logging.INFO`
    - 10: `RFC.logging.DEBUG`

    </Tip>"""

    _configure_library_root_logger()
    return _get_library_root_logger().getEffectiveLevel()


def set_verbosity(verbosity: int) -> None:
    """
    Set the verbosity level for the RFC's root logger.

    Args:
        verbosity (`int`):
            Logging level, e.g., one of:

            - `RFC.logging.CRITICAL` or `RFC.logging.FATAL`
            - `RFC.logging.ERROR`
            - `RFC.logging.WARNING` or `RFC.logging.WARN`
            - `RFC.logging.INFO`
            - `RFC.logging.DEBUG`
    """

    _configure_library_root_logger()
    _get_library_root_logger().setLevel(verbosity)


def set_verbosity_info():
    """Set the verbosity to the `INFO` level."""
    return set_verbosity(INFO)


def set_verbosity_warning():
    """Set the verbosity to the `WARNING` level."""
    return set_verbosity(WARNING)


def set_verbosity_debug():
    """Set the verbosity to the `DEBUG` level."""
    return set_verbosity(DEBUG)


def set_verbosity_error():
    """Set the verbosity to the `ERROR` level."""
    return set_verbosity(ERROR)


def disable_default_handler() -> None:
    """Disable the default handler of the root logger."""

    _configure_library_root_logger()

    assert _default_handler is not None
    _get_library_root_logger().removeHandler(_default_handler)


def enable_default_handler() -> None:
    """Enable the default handler of the root logger."""

    _configure_library_root_logger()

    assert _default_handler is not None
    _get_library_root_logger().addHandler(_default_handler)


def add_handler(handler: logging.Handler) -> None:
    """adds a handler to the root logger."""

    _configure_library_root_logger()

    assert handler is not None
    _get_library_root_logger().addHandler(handler)


def remove_handler(handler: logging.Handler) -> None:
    """removes given handler from the root logger."""

    _configure_library_root_logger()

    assert handler is not None and handler not in _get_library_root_logger().handlers
    _get_library_root_logger().removeHandler(handler)


def disable_propagation() -> None:
    """
    Disable propagation of the library log outputs. Note that log propagation is disabled by default.
    """

    _configure_library_root_logger()
    _get_library_root_logger().propagate = False


def enable_propagation() -> None:
    """
    Enable propagation of the library log outputs. Please disable the default handler to prevent
    double logging if the root logger has been configured.
    """

    _configure_library_root_logger()
    _get_library_root_logger().propagate = True


def enable_explicit_format(logger=None) -> None:
    """
    Enable explicit formatting for every logger. The explicit formatter is as follows:
    ```
        [LEVELNAME|FILENAME|LINE NUMBER] TIME >> MESSAGE
    ```
    All handlers currently bound to the root logger are affected by this method.
    """

    if logger is None:
        logger = _get_library_root_logger()
        
    handlers = logger.handlers

    for handler in handlers:
        # formatter = logging.Formatter("[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s >> %(message)s")
        formatter = logging.Formatter("%(asctime)s <%(processName)s:%(process)d, %(threadName)s:%(thread)d> (%(last_filename)s:%(last_funcName)s:%(last_lineno)s -> %(filename)s:%(funcName)s:%(lineno)s) from logger `%(name)s`\n[%(levelname)s] %(message)s\n")
        handler.setFormatter(formatter)
        
        
def set_formatter(formatter: logging.Formatter) -> None:
    """
    Set the format for every logger.
    All handlers currently bound to the root logger are affected by this method.
    """
    handlers = _get_library_root_logger().handlers

    for handler in handlers:
        handler.setFormatter(formatter)


def reset_format() -> None:
    """
    Resets the formatting for loggers.

    All handlers currently bound to the root logger are affected by this method.
    """
    handlers = _get_library_root_logger().handlers

    for handler in handlers:
        handler.setFormatter(None)


def warning_advice(self, *args, **kwargs):
    """
    This method is identical to `logger.warning()`, but if env var RFC_NO_ADVISORY_WARNINGS=1 is set, this
    warning will not be printed
    """
    no_advisory_warnings = os.getenv("RFC_NO_ADVISORY_WARNINGS", False)
    if no_advisory_warnings:
        return
    self.warning(*args, **kwargs)
    
    
def _add_file_handler_to_root_logger(
    logger=None,
    log_path=None,
    enable_format=True,
):
    if logger is None:
        logger = _get_library_root_logger()
    if log_path is None:
        log_path = '.'
    log_path = os.path.join(log_path, logger.name+'.log')
    log_dir = os.path.dirname(log_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logger.addHandler(logging.FileHandler(log_path, mode='w', encoding='utf-8', delay=True))
    if enable_format:
        enable_explicit_format(logger)


logging.Logger.warning_advice = warning_advice
_configure_library_root_logger()
_add_file_handler_to_root_logger()
enable_explicit_format()
# print(_get_library_root_logger().handlers)