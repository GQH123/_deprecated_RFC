import os
from datetime import datetime

from RFC.utils.functional_utils import log, update_output_channels, load_object, save_object, get_prev_module_name, init_global_project_config, pretty_print_parser
from RFC.user.compile import run_compile
from RFC.user.project.ProjectConfig import ProjectConfig


def launch_project(
    project_config: ProjectConfig,
):
    project_name = project_config.project_name
    project_raw_path = project_config.project_raw_path
    project_config_path = project_config.project_config_path
    project_result_path = project_config.project_result_path
    project_log_path = project_config.project_log_path
    project_info_path = project_config.project_info_path
    project_run_log_path = project_config.project_run_log_path
    debug = project_config.debug
    project_debug_log_path = project_config.project_debug_log_path
    project_root = os.path.abspath(project_name)
    # project_run_log_path = os.path.join(project_name, project_run_log_path)
    # project_info_path = os.path.join(project_name, project_info_path)
    # if debug:
    #     project_debug_log_path = os.path.join(project_name, project_debug_log_path)

    if not os.path.exists(project_root):
        os.mkdir(project_root)
    
    project_config.project_root = project_root
    init_global_project_config(project_config)
    run_compile()

    if os.path.exists(os.path.join(project_root, project_info_path)):
        project_info = load_object(os.path.join(project_root, project_info_path))
        project_info.update({
            'name': project_name,
            'raw_path': project_raw_path,
            'config_path': project_config_path,
            'result_path': project_result_path,
            'log_path': project_log_path,
            'root': project_root,
            'info_path': project_info_path,
            'run_log_path': project_run_log_path,
            'debug': debug,
            'debug_log_path': project_debug_log_path,
            # 'created_time': datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
            'last_launched_time': datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
        })
    else:
        project_info = {
            'name': project_name,
            'raw_path': project_raw_path,
            'config_path': project_config_path,
            'result_path': project_result_path,
            'log_path': project_log_path,
            'root': project_root,
            'info_path': project_info_path,
            'run_log_path': project_run_log_path,
            'debug': debug,
            'debug_log_path': project_debug_log_path,
            'created_time': datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
            'last_launched_time': datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
        }
    
    if debug:
        if project_debug_log_path:
            update_output_channels('main', project_debug_log_path)
    else:
        if project_run_log_path:
            update_output_channels('main', project_run_log_path)

    save_object(project_info, project_info_path)
    log(f'Project {project_name} launched.\n', note='Project', mode='info', from_module=get_prev_module_name(1))
    log(f'Project Configurations:\n{pretty_print_parser(project_config.__dict__)}\n', pure_output=True)