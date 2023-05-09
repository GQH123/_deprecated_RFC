import os
# import sys
from pprint import pprint

import RFC.requestor as requestor
import RFC.itemset as itemset
from RFC.utils.functional_utils import save_object, update_output_channels, switch_output_channel, log
from RFC.utils.structural_utils import summary_leaves

from settings import setup_settings


def check_integrity(rootdir='RFC'):
    switch_output_channel('compile_log', True)
    log('\nchecking integrity...\n\n', note='Checker', pure_output=True, end='')
    for root, dirs, files in os.walk(rootdir):
        for file in files:
            if file != '__init__.py':
                continue
            filepath = os.path.join(root, file)
            if os.path.islink(filepath):
                if not os.path.exists(os.path.join(root, os.readlink(filepath))):
                    log(f'broken __init__.py for path {repr(root)}', mode='warn')
                else:
                    log(f'system predefined __init__.py for path {repr(root)}')
            else:
                log(f'custom __init__.py for path {repr(root)}')

    log('\nDone.', note='Checker', pure_output=True, end='')

    switch_output_channel('compile_log', False)
    print()


def setup(**kwargs):
    log('\n', pure_output=True, end='')
    self_kwargs = kwargs['kwargs']
    update_output_channels({
        'compile_log': (open(self_kwargs['compile_log_path'], 'w'), True),
    })

    log('compiling modules...\n\n', note='Compiler', pure_output=True, end='')

    def update_module_list(module_list, _module_list):
        for module_name in _module_list:
            _module_name = module_name
            step = 0
            while _module_name in module_list:
                step += 1
                _module_name = f'{module_name}_{step}'
            module_list[_module_name] = _module_list[module_name]

    result = {}
    module_list = {}
    result['requestor'], _module_list = requestor.setup(**kwargs.get('requestor', {}))
    update_module_list(module_list, _module_list)
    result['itemset'], _module_list = itemset.setup(**kwargs.get('itemset', {}))
    update_module_list(module_list, _module_list)
    # result['crawler'], _module_list = crawler.setup(**kwargs.get('crawler', {}))
    # update_module_list(module_list, _module_list)

    save_object(result, 'references.json')
    save_object(module_list, 'module_list.json')

    module_leaves_summary = summary_leaves()
    leaves_summary_log_path = self_kwargs['leaves_summary_log_path']
    if leaves_summary_log_path:
        pprint(module_leaves_summary, stream=open(leaves_summary_log_path, 'w'))

    log('\nDone.\n', note='Compiler', pure_output=True, end='')


if __name__ == '__main__':
    setup(**setup_settings)
    check_integrity()