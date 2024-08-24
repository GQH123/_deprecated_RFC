import os
import json
import shutil
import importlib

from .types import *


SUPPORTED_PROJECT_TYPES = [x for x in os.listdir(os.path.join(os.path.split(__file__)[0], 'types')) if x not in ['__pycache__', '__init__.py']]

def mkdir(path):
    os.makedirs(path, exist_ok=False)


def traverse_config(path, config):
    for unit_name, unit in config.items():
        _path = os.path.join(path, unit_name)
        if isinstance(unit, dict):
            mkdir(_path)
            traverse_config(_path, unit)
        else:
            unit.make(_path)  # unified interface of dir structure unit types


def create_project(project_path, project_type='rfc_project_template_v1'):
    if os.path.exists(project_path):
        print(f'project path already exists: {repr(project_path)}, skipped')
        return
    if project_type not in SUPPORTED_PROJECT_TYPES:
        raise ValueError(f"unsupported project type: {repr(project_type)}, supported types: {repr(SUPPORTED_PROJECT_TYPES)}")
    os.makedirs(project_path)
    config = importlib.import_module(f'RFC.user.types.{project_type}.config').get_config(project_path)
    traverse_config(project_path, config)
    print('done')
    

def main(project_path):
    try:
        create_project(project_path)
    except (Exception, KeyboardInterrupt) as e:
        shutil.rmtree(project_path)
        raise e