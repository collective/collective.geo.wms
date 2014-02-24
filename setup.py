from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='collective.geo.wms',
      version=version,
      description="WMS Support for Collective Geo",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: GIS",
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        ],
      keywords='GIS WMS WMTS Openlayers Dexterity',
      author='Christian Ledermann',
      author_email='christian.ledermann@gmail.com',
      url='https://github.com/collective/collective.geo.wms',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.geo'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'OWSLib',
          'plone.app.dexterity [grok,relations]',
          'plone.namedfile [blobs]',
          'collective.autopermission',
          'collective.geo.mapwidget',
          'collective.geo.settings',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
