======
nglib
======

nglib is a simple application that puts PDF and CHM files in a directory
hierarchy into a SQLite database for faster searching. Originally the plan
was to extract metadata like title and author from these files, but this turned
out to be not as straight-forward as expected. So for now, only filenames
are used. Titles are generated from filenames by stripping the file extension
and replacing "." with spaces.

Make sure you have the Python bindings for the STFL library installed.
On Debian/Ubuntu grab the package python-stfl. Otherwise get the source from
http://www.clifford.at/stfl/.

On first run, the program will ask you for some configuration settings:

* the directory where you store your PDF and CHM collection

* a command that should be used for displaying PDF files

* a command that should be used for displaying CHM files

* a command that should be used for "revealing" files (only shows the directory on linux/gnome)

Those settings will be written to ~/.nglib/nglibrc

Currently, there are three commands:

    * nglib: run nglib with a STFL based interface
    * nglib-update: update (actually reload) your library from the command line
    * nglib-search: search your library from the command line


Installation
============

The tarball is a standard Python distutils package that can be installed by running
sudo python setup.py install

This will install all command line scripts to /usr/local/bin/.

There is no way to uninstall a distutils package and the location where the files
will be installed is platform dependent. So just delete /usr/local/bin/nglib*.
If you want to get rid of the configuration and database to, delete ~/.nglib as well.

