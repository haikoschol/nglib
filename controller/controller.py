# encoding: utf-8

"""
@summary: this module contains classes for connecting model and view
@author: Haiko Schol <alsihad (at) zeropatience (dot) net>

Copyright (c) 2009, Haiko Schol alsihad (at) zeropatience (dot) net
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

import simplejson


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
        return self._db.search(term)


    def get_all(self):
        """
        return all books in the database
        """
        all_books = self._db.get_all()
        self._pos2id = [x.book_id for x in all_books]
        return all_books


    def open_book_at_position(self, pos):
        """
        open an ebook file in the appropriate viewer application

        pos - position of the entry in the view
        """
        # ***FIXME*** implement KDE, Mac OS X and Windows support
        book = self._db.get_by_id(self._pos2id[pos])
        path = os.path.join(book.path, book.filename)
        Popen(['gnome-open', path], close_fds=True)


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


class InvalidArgumentError(Exception):
    """
    signal wrong and/or missing arguments from a method
    of an RestApiAdapter object
    """
    pass

    
class RestApiAdapter(object):
    """
    puts JSON marshalling around a controller
    
    This class is used for the web frontend. Controller methods
    that are used from the web frontend are wrapped, taking
    and returning data in JSON format. 
    """
    
    def __init__(self, controller):
        """
        create a RestApiAdapter
        
        controller - the controller object to wrap
        """
        self.controller = controller
        
    
    def search(self, json):
        """
        search for a book
        
        json - { 'searchterm' : 'cooking for geeks' }
        """
        data = simplejson.loads(json)
        if not 'searchterm' in data:
            raise InvalidArgumentError('search term missing')
        
        books = self.controller.search(data['searchterm'])
        result = []
        
        for book in books:
            result.append({'id': book.id,
                           'title': book.title,
                           'author': book.author,})
        
        return simplejson.dumps(result)
