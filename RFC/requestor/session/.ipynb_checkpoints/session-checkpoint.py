from RFC.utils.structural_utils import leaf, get_leaves
from RFC.utils.exception_utils import NotSupportedError, ConditionOverflowError

from .SessionConfig import SessionConfig
from .RequestsSessionConfig import RequestsSessionConfig
# from .AsksSessionConfig import AsksSessionConfig
# from .AioHTTPSessionConfig import AioHTTPSessionConfig

from .Session import Session
from .RequestsSession import RequestsSession
# from .AsksSession import AsksSession
# from .AioHTTPSession import AioHTTPSession


@leaf()
def init(**kwargs):
    ...


def get_session_config(
    session_config: str
) -> SessionConfig:
    all_supported_session_configs = ['requests', 'asks', 'aiohttp']
    if session_config not in all_supported_session_configs:
        raise NotSupportedError(session_config, all_supported_session_configs, __name__)
    if session_config == 'requests':
        return RequestsSessionConfig()
    elif session_config == 'asks':
        return AsksSessionConfig()
    elif session_config == 'aiohttp':
        return AioHTTPSessionConfig()
    else:
        raise ConditionOverflowError(session_config, __name__)


@leaf(system=True)
def get_session(
    session_type: str,
    session_config: SessionConfig | str,
    use_session: bool,
    **kwargs,
) -> Session:
    if session_config is None:
        session_config = 'requests'
    if isinstance(session_config, str):
        session_config = get_session_config(session_config)

    all_supported_sessions = ['requests', 'asks', 'aiohttp']

    if session_type not in all_supported_sessions:
        raise NotSupportedError(session_type, all_supported_sessions, __name__)
    if session_type == 'requests':
        return RequestsSession(session_config, use_session)
    elif session_type == 'asks':
        return AsksSession(session_config, use_session)
    elif session_type == 'aiohttp':
        return AioHTTPSession(session_config, use_session)
    else:
        raise ConditionOverflowError(session_type, __name__)


leaves = get_leaves()