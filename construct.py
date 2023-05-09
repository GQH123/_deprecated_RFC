import os
import fire


def construct(path):
    try:
        path = str(path)
    except Exception:
        print(f'input {repr(path)} is not a legal path!')
        return

    splitted_path = [part for part in path.split(os.sep) if part]
    if splitted_path[0] != 'RFC':
        print(f"path {repr(path)} must starts with 'RFC'")
    splitted_path = splitted_path[1:]
    path = 'RFC'
    utils_path = 'utils/structural_initializer.py'
    utils_py = 'RFC/utils/structural_template.py'
    for part in splitted_path:
        if part == '':
            continue
        utils_path = os.path.join('..', utils_path)
        path = os.path.join(path, part)
        if os.path.exists(path):
            print(f'path {repr(path)} already exists, skipped')
            continue
        print(f'construct new path {repr(path)}')
        os.makedirs(path)
        _py = os.path.join(path, part+'.py')
        _init = os.path.join(path, '__init__.py')
        os.system(f'cp "{utils_py}" "{_py}"&&ln -s "{utils_path}" "{_init}"')
    print('Quit.')


if __name__ == '__main__':
    fire.Fire(construct)