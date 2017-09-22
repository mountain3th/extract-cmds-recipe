# -*- coding: utf-8 -*-

# @Author: Sam 
# @CreateTime: 2017-09-07 16:31:07 
# @Last Mofified Time: 2017-09-07 16:31:07

import os
import stat
import sys
import logging
from contextlib import contextmanager
from importlib import import_module

import zc.buildout


@contextmanager
def ignore_site_packages_paths():
    paths = sys.path
    # remove all third-party paths
    # so that only stdlib imports will succeed
    sys.path = list(filter(
        None,
        filter(lambda i: 'site-packages' not in i, sys.path)
    ))
    yield
    sys.path = paths


def is_std_lib(module):
    if module in sys.builtin_module_names:
        return True

    with ignore_site_packages_paths():
        imported_module = sys.modules.pop(module, None)
        try:
            import_module(module)
        except ImportError:
            return False
        else:
            return True
        finally:
            if imported_module:
                sys.modules[module] = imported_module


scripts_template = '''#!%(python)s

import sys
sys.path[0:0] = %(path)s

%(initialization)s
import %(module_name)s

def string2builtintype(string):
    print string, type(string)
    if (string.startswith("\'") and string.endswith("\'"))or (string.startswith('\"') and string.endswith('\"')):
        return str(string[1:-1])

    if string == 'None':
        return None

    try:
        integer = int(string)
        return integer
    except:
        pass
    try:
        floating = float(string)
        return floating
    except:
        pass

for index, value in enumerate(sys.argv):
    if index == 0:
        continue
    sys.argv[index] = string2builtintype(value)

if __name__ == '__main__':
    ret = %(module_name)s.%(attrs)s(*tuple(sys.argv[1:]))
    print ret
    sys.exit(0)
'''


class ExtractCmds(object):

    def __init__(self, buildout, name, options):
        options['path'] = os.path.join(
            buildout['buildout']['parts-directory'],
            name,
        )
        self.options = options
        self.buildout = buildout
        # self.syspath = []

        # for egg in os.listdir(buildout['buildout']['eggs-directory']):
        #     egg_path = os.path.join(buildout['buildout']['eggs-directory'], egg)
        #     self.syspath.append(egg_path)

        self.cmds_path = os.path.join(self.buildout['buildout']['bin-directory'], 'cmds')
        if not os.path.exists(self.cmds_path):
            os.mkdir(self.cmds_path)

    def install(self):
        self.options.created(self.options['path'])
        with open(self.options['path'], 'w') as f:
            includes = self.options['include'].split('\n')
            for cmd in includes:
                name, cmd_path = cmd.split('=')
                module, func = cmd_path.split(':')
                self._write_modules_to_func(name, module, func)
        return self.options.created()

    update = install

    def _script_install(self, script_name, script_content):
        script_path = os.path.join(self.cmds_path, script_name)
        with open(script_path, 'w') as f:
            f.write(script_content)
        st = os.stat(script_path)
        os.chmod(script_path, st.st_mode | stat.S_IEXEC)

    def _write_modules_to_func(self, cmd_name, module, attr):
        top_module = module.split('.')[0]
        if is_std_lib(top_module):
            reqs = ['zc.recipe.egg']
        else:
            reqs = [top_module]

        ws = zc.buildout.easy_install.working_set(
            reqs, [self.buildout['buildout']['eggs-directory'], self.buildout['buildout']['develop-eggs-directory']]
        )

        path = [dist.location for dist in ws]

        script_content = scripts_template % dict(python=sys.executable, path=path, initialization='', module_name=module, attrs=attr)

        self._script_install(cmd_name, script_content)
