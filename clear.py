import os


def system(cmd, debug=True):
    if debug:
        print(cmd)
    os.system(cmd)


def rm(path):
    system(f'rm -rf "{path}"')


def clear(path='.'):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.pyc'):
                rm(os.path.join(root, file))
        for dir in dirs:
            if dir == '__pycache__' or dir == '.ipynb_checkpoints' or dir == 'deprecated':
                rm(os.path.join(root, dir))


clear()