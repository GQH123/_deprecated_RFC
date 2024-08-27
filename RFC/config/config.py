from .attrdict import AttrDict
from .primitive import FuncCall


RFC_CONFIG = AttrDict({
    "DEFAULT_VALUE": {
        "Project": {
            "name": "anonymous",
            "date_format": "%Y-%m-%d %H:%M:%S",
            "desc": "nothing here :)",
            "logdir": "./logs/project",
            "author": FuncCall("get_username", {}),
            "host": FuncCall("get_hostname", {}),
        },
        # this is RFC Low-Level Config, which is different from the High-Level one
        "RFC": {
            "logging_level": "info"
        },
    },
    "PATH_REGISTER": {
        "config_utils_module": "RFC.config.utils",
    },
    "DEFAULT_BEHAVIOUR": {
        "prefixed_middlewares": {
            "basic_info": {},
        },
        "project_log_enable": True,
        "project_log_limit": None,
    },
})