import os
import fire


def system(cmd):
    print(f'>>> {cmd}')
    os.system(cmd)


def show(path='./RFC', ext='py'):
    system(f'find "{path}" -name \'*.{ext}\' | xargs wc -l')


if __name__ == '__main__':
    fire.Fire(show)