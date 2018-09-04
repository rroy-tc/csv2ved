import distutils.command.clean
import os
import setuptools
import subprocess
from distutils.core import setup


def read_first_line(file_name):
    with open(os.path.join(os.path.dirname(__file__), file_name)) as f:
        return f.readline().strip()


def read_file(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


class Clean(distutils.command.clean.clean):
    def run(self):
        subprocess.call('find . -name *.pyc -delete'.split())
        subprocess.call('rm -rf *.egg/'.split())
        distutils.command.clean.clean.run(self)


REQUIREMENTS = [
    'click==6.7',
    'python-dateutil==2.6.1',
    'python-gnupg==0.4.1',
    'six==1.11.0'
]

setup(name='csv2ved',
      version=read_first_line('version_number.txt'),
      description="Python command line utility to convert csv files into ved format.",
      long_description=read_file('README.md'),
      author='Rajan Roy',
      author_email='rroy@tucowsinc.com',
      license='',
      url='https://www.tucows.com',
      packages=setuptools.find_packages(exclude=('tests',)),
      include_package_data=True,
      zip_safe=False,
      install_requires=REQUIREMENTS,
      entry_points={
          'console_scripts': [
              'csv2ved = csv2ved.csv2ved:csv2ved',
          ],
      },
      cmdclass={
          'clean': Clean
      },
      )
