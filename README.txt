======
nglib
======

nglib is a simple application that puts PDF and CHM files in a directory
hierarchy into a SQLite database for faster searching. Originally the plan
was to extract metadata like title and author from these files, but this turned
out to be not as straight-forward as expected. So for now, only filenames
are used. Titles are generated from filenames by stripping the file extension
and replacing "." with spaces.

Make sure you have the python bindings for the `STFL <http://www.clifford.at/stfl/>`_
library installed (``python-stfl`` on Debian/Ubuntu).

On first run, the program will ask you for some configuration settings:

* the directory where you store your PDF and CHM collection

* a command that should be used for displaying PDF files

* a command that should be used for displaying CHM files

* a command that should be used for "revealing" files (only shows the directory on linux/gnome)

Those settings will be written to ``~/.nglib/nglibrc``

Currently, there are three commands:

    * nglib: run nglib with a STFL based interface
    * nglib-update: update (actually reload) your library from the command line
    * nglib-search: search your library from the command line


Installation
============

To install, extract the release tarball and inside the directory run ``sudo python setup.py install``. This will install all command line scripts to ``/usr/local/bin/``.

If you want high-tech features like "uninstall" and you are using a debian based distribution, you can also create a debian package this way:

    * install `stdeb <http://pypi.python.org/pypi/stdeb>`_
    * run ``py2dsc nglib-<version>.tar.gz``
    * inside directory ``deb_dist/nglib-<version>`` run ``dpkg-buildpackage -rfakeroot -uc -us``
    * run ``sudo dpkg -i ../python-nglib_<some crap>.deb``

To uninstall, run ``sudo aptitude remove python-nglib``.

