from RFC.utils.structural_utils import leaf, get_leaves
from RFC.utils.exception_utils import ConditionOverflowError, ParamTypeError, ParamValueError

from .SessionConfig import SessionConfig
from .RequestsSessionConfig import RequestsSessionConfig
from .AsksSessionConfig import AsksSessionConfig
from .AioHTTPSessionConfig import AioHTTPSessionConfig

from .Session import Session
from .RequestsSession import RequestsSession
from .AsksSession import AsksSession
from .AioHTTPSession import AioHTTPSession

all_supported_sessions = ['requests', 'asks', 'aiohttp']


@leaf()
def init(**kwargs):
    ...


def get_session_config(
    session_config: str,
    **kwargs,
) -> SessionConfig:
    if session_config not in all_supported_sessions:
        raise ParamValueError('session_config', session_config, all_supported_sessions, __name__)
    if session_config == 'requests':
        return RequestsSessionConfig(**kwargs)
    elif session_config == 'asks':
        return AsksSessionConfig(**kwargs)
    elif session_config == 'aiohttp':
        return AioHTTPSessionConfig(**kwargs)
    else:
        raise ConditionOverflowError(session_config, __name__)


@leaf(system=True)
def get_session(
    session_config: SessionConfig | str,
    **kwargs,
) -> Session:
    if isinstance(session_config, str):
        session_type = session_config
        session_config = get_session_config(session_type, **kwargs)
    else:
        session_type = type(session_config).__name__
        if session_type == 'RequestsSessionConfig':
            session_type = 'requests'
        elif session_type == 'AsksSessionConfig':
            session_type = 'asks'
        elif session_type == 'AioHTTPSessionConfig':
            session_type = 'aiohttp'
        else:
            raise ParamTypeError('session_config', session_config, [SessionConfig], __name__)

    if session_type not in all_supported_sessions:
        raise ParamValueError('session_type', session_type, all_supported_sessions, __name__)
    if session_type == 'requests':
        return RequestsSession(session_config)
    elif session_type == 'asks':
        return AsksSession(session_config)
    elif session_type == 'aiohttp':
        return AioHTTPSession(session_config)
    else:
        raise ConditionOverflowError(session_type, __name__)


leaves = get_leaves()