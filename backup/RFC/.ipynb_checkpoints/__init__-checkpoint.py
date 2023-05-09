from . import network_layer as n, middleware_layer as m, crawler_layer as c
from .settings import settings


def init(**kwargs):
    network_layer.init(**kwargs['network_layer'])


init(**settings)