# -*- coding: utf-8 -*-

# @Author: Sam
# @CreateTime: 2017-09-08 14:42:46 
# @Last Mofified Time: 2017-09-08 14:42:46

import os
import shutil
import tempfile
import unittest
import zc.buildout.testing

class RecipeTests(unittest.TestCase):

    def setUp(self):
        self.here = os.getcwd()
        self.tmp = tempfile.mkdtemp(prefix='testdemoconfigrecipe-')
        os.chdir(self.tmp)
        self.buildout = buildout = zc.buildout.testing.Buildout()
        self.config = 'some config text\n'
        buildout['config'] = dict(contents=self.config)
        from extract_cmds_recipe import ExtractCmds
        self.recipe = democonfigrecipe.Recipe(
            buildout, 'config', buildout['config'])

    def tearDown(self):
        os.chdir(self.here)
        shutil.rmtree(self.tmp)

    def test_path_option(self):
        buildout = self.buildout
        self.assertEqual(os.path.join(buildout['buildout']['parts-directory'],
                                      'config'),
                         buildout['config']['path'])

    def test_install(self):
        buildout = self.buildout
        self.assertEqual(self.recipe.install(), [buildout['config']['path']])
        with open(buildout['config']['path']) as f:
            self.assertEqual(self.config, f.read())

if __name__ == '__main__':
    unittest.main()