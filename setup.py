from distutils.core import setup

setup(
        name='nglib',
        version='0.1',
        author='Haiko Schol',
        author_email='alsihad@zeropatience.net',
        packages=['nglib', 'nglib.model', 'nglib.view', 'nglib.tests'],
        scripts=['bin/nglib'],
        url='http://code.google.com/p/nglib',
        license='LICENSE.txt',
        description='Simple tool for searching your eBook collection.',
        long_description=open('README.txt').read(),
)

