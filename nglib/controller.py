# encoding: utf-8

"""
@summary: this module contains classes for connecting model and view
@author: Haiko Schol <alsihad (at) zeropatience (dot) net>

Copyright (c) 2009, 2010 Haiko Schol alsihad (at) zeropatience (dot) net
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice,
        this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice,
        this list of conditions and the following disclaimer in the documentation
        and/or other materials provided with the distribution.
    * Neither the name of the netgarage nor the names of its contributors
        may be used to endorse or promote products derived from this software
        without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

For more Information see http://netgarage.org
"""

import os.path
from subprocess import Popen
from subprocess import STDOUT

#import simplejson
from nglib.model.configurationstore import NgLibError


def add_file(path, database):
    """
    don't try to extract any metadata, just use the filename
    (slightly prettyfied) as title and a blank string as author.
    ignore all files with no pdf or chm extension.

    path - absolute path to a file
    database - BookDatabase object

    """
    filename = os.path.basename(path)
    ext = filename.split('.')[-1].lower()
    if ext not in ('pdf', 'chm'):
        return False

    pos = filename.rfind(ext)
    title = filename[:pos]
    title = title.replace('.', ' ').strip()
    author = ''
    database.add(path, title, author)
    return True


def count_files(path, extensions=('pdf', 'chm')):
    """
    return the number of files with certain extensions in a directory tree.

    path - root of the directory tree
    extensions - iterable of file extensions to count

    """
    count = 0
    for _, _, files in os.walk(path):
        for file in files:
            ext = file.split('.')[-1].lower()
            if ext in extensions:
                count += 1
    return count


def add_books(path, database, add_per_run=5):
    """
    generator that adds all pdf and chm files in the directory tree
    "path" to the database. yields numbers denoting how many files
    have been added so far.

    path - absolute path to the directory to walk
    database - BookDatabase object
    add_per_run - how many files should be added per call

    """
    subtotal = 0
    added = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.startswith('.'):
                continue
            ext = file.split('.')[-1].lower()
            abspath = os.path.join(root, file)

            if ext in ('pdf', 'chm'):
                add_file(abspath, database)
                added += 1

                if added % add_per_run == 0:
                    subtotal += added
                    tmp = added
                    added = 0
                    yield tmp, subtotal

    yield added, subtotal


class Controller(object):
    """
    This class provides functionality of the model to the view.
    """

    def __init__(self, database, config):
        """
        create a controller

        database - an instance of BookDatabase
        config - an instance of ConfigurationStore
        """
        self._db = database
        self.config = config
        self._views = {}
        self._pos2id = [] # map a position in the view to a
                          # primary key in the book db


    def add_view(self, view, view_init=None):
        """
        add a view

        view - the view to add
        view_init - optional initialization function
        """
        self._views[view] = view_init


    def search(self, term):
        """
        search for a term in the database

        term - the term to search for
        """
        results = self._db.search(term)
        results.sort(key=lambda x: x.title)
        self._pos2id = [x.bid for x in results]
        return results


    def get_all(self):
        """
        return all books in the database
        """
        all_books = self._db.get_all()
        all_books.sort(key=lambda x: x.title)
        self._pos2id = [x.bid for x in all_books]
        return all_books


    def open_book(self, pos):
        """
        open an ebook file in the appropriate viewer application

        pos - position of the entry in the view
        """
        # FIXME add windows support, probably with os.startfile()
        book = self._db.get_by_id(self._pos2id[int(pos)])
        path = os.path.join(book.path, book.filename)
        try:
            cmd = getattr(self.config, book.filetype+'cmd')
            argv = cmd.split()
            argv.append(path)
            Popen(argv, stdout=open('/dev/null', 'w'), stderr=STDOUT)
        except:
            pass # FIXME show error msg - unsupported filetype or try default cmd


    def show_book(self, pos):
        """
        show an ebook file in a file manager
        """
        book = self._db.get_by_id(self._pos2id[int(pos)])

        import platform
        if 'darwin' in platform.platform().lower():
            path = os.path.join(book.path, book.filename)
        else:
            path = book.path

        try:
            argv = self.config.showcmd.split()
            argv.append(path)
            Popen(argv, stdout=open('/dev/null', 'w'), stderr=STDOUT)
        except:
            pass # FIXME show error msg


    def run(self):
        """
        run the application
        runs all view initializers
        """
        for view, init in self._views.items():
            if init and hasattr(init, '__call__'):
                init()


    def shutdown(self):
        """
        shutdown the application
        """
        self._db.close()
        import sys
        sys.exit(0)


    def get_setting(self, setting):
        """
        return the value of a configuration setting

        setting - the name of the setting to return
        """
        if not hasattr(self.config, setting):
            raise NgLibError('There is no setting called "%s".' % setting)
        return getattr(self.config, setting)


    def set_setting(self, setting, value):
        """
        change the value of a configuration setting

        setting - the name of the setting to change
        value - the new value of the setting
        """
        if not hasattr(self.config, setting):
            raise NgLibError('There is no setting called "%s".' % setting)
        setattr(self.config, setting, value)


    def write_settings(self):
        """
        write configuration settings to disk
        """
        self.config.save()


    def count_books(self):
        """
        return the number of PDF and CHM files in the configured library directory
        """
        return count_files(self.config.dir)


    def reload_library(self):
        """
        (re)build a BookDatabase with all files from the configured library directory
        """
        self._db.clear()
        return add_books(self.config.dir, self._db)


# there's nothing to see here, move along
#class InvalidArgumentError(Exception):
#    """
#    signal wrong and/or missing arguments from a method
#    of an RestApiAdapter object
#    """
#    pass

#class RestApiAdapter(object):
#    """
#    puts JSON marshalling around a controller
#
#    This class is used for the web frontend. Controller methods
#    that are used from the web frontend are wrapped, taking
#    and returning data in JSON format.
#    """
#
#    def __init__(self, controller):
#        """
#        create a RestApiAdapter
#
#        controller - the controller object to wrap
#        """
#        self.controller = controller
#
#
#    def search(self, json):
#        """
#        search for a book
#
#        json - { 'searchterm' : 'cooking for geeks' }
#        """
#        data = simplejson.loads(json)
#        if not 'searchterm' in data:
#            raise InvalidArgumentError('search term missing')
#
#        books = self.controller.search(data['searchterm'])
#        result = []
#
#        for book in books:
#            result.append({'id': book.id,
#                           'title': book.title,
#                           'author': book.author,})
#
#        return simplejson.dumps(result)
