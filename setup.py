from platform import platform
from distutils.core import setup

scripts = ['bin/nglib', 'bin/nglib-update', 'bin/nglib-search']
if 'darwin' in platform().lower():
    scripts.append('bin/reveal')

setup(
        name='nglib',
        version='0.2rc2',
        author='Haiko Schol',
        author_email='alsihad@zeropatience.net',
        packages=['nglib', 'nglib.model', 'nglib.view', 'nglib.tests'],
        scripts=scripts,
        url='http://code.google.com/p/nglib',
        license='LICENSE.txt',
        description='Simple tool for searching your eBook collection.',
        long_description=open('README.txt').read(),
)

