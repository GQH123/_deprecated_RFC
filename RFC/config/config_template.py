from .attrdict import AttrDict
from .primitive import Type, Value


"""
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
"""


TEMPLATE = AttrDict({
    'RFC': {
        Value("DEFAULT_VALUE"): {
            Value("Project"): {
                Value("name"):          Type(str, help="project name"),
                Value("date_format"):   Type(str, help="date format"),
                Value("desc"):          Type(str, help="project description"),
                Value("logdir"):        Type(str, help="log directory"),
                Value("author"):        Type(str, help="author of the project"),
                Value("host"):          Type(str, help="host of the project"),
            },
            Value("RFC"): {
                Value("logging_level"):     Type(str, help="logging level"),
            },
        },
        Value("PATH_REGISTER"): {
            Value("config_utils_module"):   Type(str, help="module path of config utils"),
        },
        Value("DEFAULT_BEHAVIOUR"): {
            Value("prefixed_middlewares"): {
                Value("basic_info"): {},
            },
            Value("project_log_enable"):    Type(bool, help="enable project log"),
            Value("project_log_limit"):     Type(int, help="limit of project log size"),
            
        },
    }
})