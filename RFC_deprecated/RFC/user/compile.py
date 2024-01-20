import os
# import sys
from pprint import pprint

import RFC.requestor as requestor
import RFC.itemset as itemset
from RFC.utils.functional_utils import save_object, update_output_channels, log, get_project_prefix
from RFC.utils.structural_utils import summary_leaves
from RFC.settings import setup_settings
from RFC.user.user import all_supported_configs, get_config


log_file = ['stdout', 'compile_log']


def check_integrity(rootdir='RFC'):
    log('\nchecking integrity...\n\n', file=log_file, note='Checker', pure_output=True, end='')
    for root, dirs, files in os.walk(rootdir):
        for file in files:
            if file != '__init__.py':
                continue
            filepath = os.path.join(root, file)
            if os.path.islink(filepath):
                if not os.path.exists(os.path.join(root, os.readlink(filepath))):
                    log(f'broken __init__.py for path {repr(root)}', file=log_file, mode='warn')
                else:
                    log(f'system predefined __init__.py for path {repr(root)}', file=log_file)
            else:
                log(f'custom __init__.py for path {repr(root)}', file=log_file)

    log('\nDone.', file=log_file, note='Checker', pure_output=True, end='')


def setup():
    log('\ncompiling modules...\n\n', file=log_file, note='Compiler', pure_output=True, end='')
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

    save_object(result, 'references.json', 'meta')
    save_object(module_list, 'module_list.json', 'meta')

    module_leaves_summary = summary_leaves()
    leaves_summary_log_path = self_kwargs['leaves_summary_log_path']
    if leaves_summary_log_path:
        pprint(module_leaves_summary, stream=open(os.path.join(get_project_prefix('meta'), leaves_summary_log_path), 'w'))

    log('\nDone.', file=log_file, note='Compiler', pure_output=True, end='')


def check_all_config(rootdir='RFC'):
    config_structure = {}
    all_supported_config_names = [config.__name__ for config in all_supported_configs.values()]
    for root, dirs, files in os.walk(rootdir):
        for file in files:
            if not file.endswith('.py') or 'Config' not in file or file.startswith('Base'):
                continue
            config_name = file[:-len('.py')]
            assert config_name in all_supported_config_names, f'config {config_name} not registered in RFC.user.user.all_supported_configs'
            root_parts = root.split(os.sep)
            _config_structure = config_structure
            for part in root_parts:
                if part == 'RFC':
                    continue
                if part not in _config_structure:
                    _config_structure[part] = {}
                _config_structure = _config_structure[part]
            _config_structure[config_name] = get_config(config_name, exact_match=True)._to_str(include_sub=False, return_attr=True)
    save_object(config_structure, 'config_references.json', 'meta')
    
    log('\nDone.', file=log_file, note='Compiler', pure_output=True, end='')


def run_compile():
    log('\n', file=['stdout'], pure_output=True, end='')
    self_kwargs = setup_settings['kwargs']
    update_output_channels('compile_log', self_kwargs['compile_log_path'], 'meta')
    check_integrity()
    log('\n', file=log_file, pure_output=True, end='')
    setup()
    log('\n', file=log_file, pure_output=True, end='')
    check_all_config()
    log('\n', file=['stdout'], pure_output=True, end='')