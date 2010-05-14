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

To install run the script install.sh. To uninstall, run uninstall.sh.

