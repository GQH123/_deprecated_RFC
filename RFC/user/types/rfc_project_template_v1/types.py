import os
import shutil
from collections import namedtuple
from distutils.dir_util import copy_tree


__all__ = ['file', 'link', 'cp', 'cpdir']


def dir_structrue(name, fields, f_make, **kwargs):
    def make(self, path):
        kwargs = {}
        for field in fields:
            kwargs[field] = getattr(self, field)
        f_make(_path=path, **kwargs)
    result = namedtuple(name, fields, **kwargs)
    result.make = make
    return result


def copy_dir(_path, cp_path):
    cp_path = os.path.join(os.path.split(__file__)[0], 'templates', cp_path)
    copy_tree(cp_path, _path)
cpdir = dir_structrue('cpdir', ['cp_path'], copy_dir)


def copy(_path, cp_path):
    cp_path = os.path.join(os.path.split(__file__)[0], 'templates', cp_path)
    shutil.copy(cp_path, _path)
cp = dir_structrue('cp', ['cp_path'], copy)


def touch(_path, content=None, binary=False):
    content = content or ('' if not binary else b'')
    mode = 'w' if not binary else 'wb'
    with open(_path, mode) as f:
        f.write(content)
file = dir_structrue('file', ['content', 'binary'], touch, defaults=[None, False])
        

def symlink(_path, target):
    os.symlink(target, _path)
link = dir_structrue('link', ['target'], symlink)
    


