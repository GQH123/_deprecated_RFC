import os
# import sys
from pprint import pprint

import RFC.requestor as requestor
import RFC.itemset as itemset
from RFC.utils.functional_utils import save_object, update_output_channels, log, get_project_prefix
from RFC.utils.structural_utils import summary_leaves

from .settings import setup_settings


def check_integrity(rootdir='RFC'):
    log('\nchecking integrity...\n\n', file=['stdout', 'compile_log'], note='Checker', pure_output=True, end='')
    for root, dirs, files in os.walk(rootdir):
        for file in files:
            if file != '__init__.py':
                continue
            filepath = os.path.join(root, file)
            if os.path.islink(filepath):
                if not os.path.exists(os.path.join(root, os.readlink(filepath))):
                    log(f'broken __init__.py for path {repr(root)}', file=['stdout', 'compile_log'], mode='warn')
                else:
                    log(f'system predefined __init__.py for path {repr(root)}', file=['stdout', 'compile_log'])
            else:
                log(f'custom __init__.py for path {repr(root)}', file=['stdout', 'compile_log'])

    log('\nDone.', file=['stdout', 'compile_log'], note='Checker', pure_output=True, end='')


def setup():
    file = ['stdout', 'compile_log']
    log('\ncompiling modules...\n\n', file=file, note='Compiler', pure_output=True, end='')
    self_kwargs = setup_settings['kwargs']

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
    result['requestor'], _module_list = requestor.setup(**setup_settings.get('requestor', {}))
    update_module_list(module_list, _module_list)
    result['itemset'], _module_list = itemset.setup(**setup_settings.get('itemset', {}))
    update_module_list(module_list, _module_list)
    # result['crawler'], _module_list = crawler.setup(**setup_settings.get('crawler', {}))
    # update_module_list(module_list, _module_list)

    save_object(result, 'references.json', 'root')
    save_object(module_list, 'module_list.json', 'root')

    module_leaves_summary = summary_leaves()
    leaves_summary_log_path = self_kwargs['leaves_summary_log_path']
    if leaves_summary_log_path:
        pprint(module_leaves_summary, stream=open(os.path.join(get_project_prefix(), leaves_summary_log_path), 'w'))

    log('\nDone.', file=file, note='Compiler', pure_output=True, end='')


def run_compile():
    log('\n', file=['stdout'], pure_output=True, end='')
    self_kwargs = setup_settings['kwargs']
    update_output_channels('compile_log', self_kwargs['compile_log_path'])
    check_integrity()
    log('\n', file=['stdout', 'compile_log'], pure_output=True, end='')
    setup()
    log('\n', file=['stdout'], pure_output=True, end='')