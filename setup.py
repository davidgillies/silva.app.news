# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from setuptools import setup, find_packages
import os

version = '3.0dev'


setup(name='silva.app.news',
      version=version,
      description="News extension for Silva",
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
      url='http://infrae.com/products/silva',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['silva', 'silva.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'Products.Formulator',
        'Products.Silva',
        'five.grok',
        'icalendar',
        'megrok.chameleon',
        'python-dateutil',
        'setuptools',
        'silva.app.document',
        'silva.core.conf',
        'silva.core.interfaces',
        'silva.core.references',
        'silva.core.services',
        'silva.core.smi',
        'silva.core.upgrade',
        'silva.core.views',
        'z3locales',
        'zeam.form.silva',
        'zeam.utils.batch',
        'zope.app.container',
        'zope.component',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.intid',
        'zope.lifecycleevent',
        'zope.location',
        'zope.publisher',
        'zope.schema',
        'zope.traversing',
        ],
      entry_points = """
      [zodbupdate]
      renames = silva.app.news:CLASS_CHANGES
      [zeam.form.components]
      recurrence = silva.app.widgets.recurrence:register
      """
      )
