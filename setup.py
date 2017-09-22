#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import find_packages, setup


setup(
    name='extract_cmds_recipe',
    license='PRIVATE',
    author='Sam',
    version='0.0.1',
    author_email='mountainking@126.com',
    description='a zc.buildout recipe to extract projectz funcs to executable cmds',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    entry_points={
        'zc.buildout': [
            'default = extract_cmds_recipe:ExtractCmds'
        ]
    },
    install_requires=['zc.buildout'],
    classifiers=[
        'Framework :: Buildout',
        'Framework :: Buildout :: Recipe'
    ]
)
