from RFC.args.arg_group import *
from RFC.item.item import *

class HitomiPage(ItemType):
    _defined_arg_groups = {
        RequestArgGroup(
            url=('fixed', 'https://hitomi.la/artist/mutou%20mato-all.html'),
            params=('replace_id', 'page={id}'),
        ),
        ItemArgGroup(
            save_dir=('auto', 'saves', 'subs'),
        ),
    }
    session_args = SessionArgs(
        no_session=False,
        lib='requests',
    )
    middleware_args = {
        'status_code': MiddlewareArgs(
            expected_status_codes=[200],
        ),
        'basic': MiddlewareArgs(),
        'saver': MiddlewareArgs(),
    }
    requestor_args = RequestorArgs(
        nproc=1,
        async_sema=1,
    )
    def _generate(cls, id, result):
        pass


