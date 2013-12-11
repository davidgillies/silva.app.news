# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from setuptools import setup, find_packages
import os

version = '3.0.4dev'

tests_require = [
    'Products.Silva [test]',
    ]


setup(name='silva.app.news',
      version=version,
      description="News extension for Silva 3",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Message Boards",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='news silva zope2',
      author='Infrae',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/silva.app.news',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['silva', 'silva.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'Products.Silva',
        'Products.SilvaExternalSources',
        'feedparser',
        'five.grok',
        'icalendar',
        'js.jquery',
        'js.jqueryui',
        'grokcore.chameleon',
        'python-dateutil',
        'setuptools',
        'silva.app.document',
        'silva.core.conf',
        'silva.core.editor',
        'silva.core.interfaces',
        'silva.core.references',
        'silva.core.services',
        'silva.core.smi',
        'silva.core.upgrade',
        'silva.core.views',
        'silva.core.xml',
        'silva.fanstatic',
        'silva.ui',
        'z3locales',
        'zeam.form.base',
        'zeam.form.silva',
        'zeam.form.ztk',
        'zeam.utils.batch',
        'zope.cachedescriptors',
        'zope.component',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.intid',
        'zope.lifecycleevent',
        'zope.publisher',
        'zope.schema',
        'zope.traversing',
        ],
      entry_points = """
      [zeam.form.components]
      recurrence = silva.app.news.widgets.recurrence:register
      tree = silva.app.news.widgets.tree:register
      path = silva.app.news.widgets.path:register
      [Products.SilvaExternalSources.sources]
      news = silva.app.news.codesources
      """,
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )
