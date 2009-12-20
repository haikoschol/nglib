# encoding: utf-8

"""
Copyright (c) 2009, Haiko Schol alsihad (at) zeropatience (dot) net
All rights reserved.

@summary: nglib is a simple application for searching an ebook collection.
@version: 0.0.1

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

class Controller(object):
    """This class provides functionality of the model to the view."""

    def __init__(self, database, config):
        """
        TODO: Fill me in

        database - an instance of BookDatabase
        config - an instance of ConfigurationStore
        """
        self._db = database
        self.config = config
        self._views = {}


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
        return self._db.get_all()


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

