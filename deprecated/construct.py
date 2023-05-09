import os
import fire


def construct(path):
    try:
        path = str(path)
    except Exception:
        print(f'input \'{path}\' is not a legal path!')
        return

    splitted_path = path.split(os.sep)
    path = 'RFC'
    utils_path = 'utils/structural_initializer.py'
    utils_py = 'RFC/utils/structural_template.py'
    for part in splitted_path:
        if part == '':
            continue
        utils_path = os.path.join('..', utils_path)
        path = os.path.join(path, part)
        if os.path.exists(path):
            print(f'path {path} already exists, skipped')
            continue
        print(f'constructing new path {path}')
        os.makedirs(path)
        _py = os.path.join(path, part+'.py')
        _init = os.path.join(path, '__init__.py')
        os.system(f'cp "{utils_py}" "{_py}"&&ln -s "{utils_path}" "{_init}"')
    print('Quit.')


if __name__ == '__main__':
    fire.Fire(construct)