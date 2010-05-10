# encoding: utf-8

"""
@summary: database of books
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

import os
import sqlite3


class Book(object):
    """
    represents a book
    """
    def __init__(self, title, filename, path, author='', pages=0,
                 tags=[], filetype='pdf', bid=None):
        """
        title - title of the book
        filename - filename of the book, excluding path
        path - absolute path to the file, excluding filename
        author - optional, author of the book
        pages - optional, number of pages of the book
        tags - optional, tags describing the book
        filetype - filetype of the book
        bid - optional, unique id
        """
        self.title = title
        self.filename = filename
        self.path = path
        self.author = author
        self.pages = pages
        self.tags = tags
        self.filetype = filetype
        self.bid = bid


    def __str__(self):
        return self.title


class BookDatabase(object):
    """
    thin wrapper around sqlite for adding, removing and searching
    pdf and chm files
    all strings assumed to be utf-8 encoded bytestrings
    """
    def __init__(self, path, db_backend_factory=sqlite3.connect):
        """
        create a BookDatabase object

        path - absoulte path to the sqlite db file
                (if it doesn't exist a new one will be created)

        db_backend_factory - callable that takes path as an argument
                              and returns something that conforms to
                              the Python DBAPI
        """
        path = path.decode('utf8')
        self._dbfile = path
        empty = not os.path.exists(path)
        self._dbcon = db_backend_factory(path)
        self._dbopen = True
        if empty:
            self._create_db()


    def close(self):
        """
        close the underlying sqlite connection
        does nothing if db is not open
        """
        if self._dbopen:
            self._dbcon.close()


    def add(self, path, title, author):
        """
        add an ebook to the database

        path - absolute path to the file
        title - title of the book
        author - author of the book

        """
        path = path.decode('utf8')
        title = title.decode('utf8')
        author = author.decode('utf8')
        cursor = self._dbcon.cursor()
        filename = os.path.basename(path)
        dirname = os.path.dirname(path)
        t = (title, author, filename, dirname)
        sql = u"insert into books values (?, ?, ?, ?)"
        cursor.execute(sql, t)
        self._dbcon.commit()
        cursor.close()


    def remove(self, path):
        """
        remove a book from the database

        path - absolute path to the file

        """
        path = path.decode('utf8')
        cursor = self._dbcon.cursor()
        filename = os.path.basename(path)
        dirname = os.path.dirname(path)
        t = (dirname, filename)
        sql = u"delete from books where path = ? and filename = ?"
        cursor.execute(sql, t)
        self._dbcon.commit()
        cursor.close()


    def clear(self):
        """
        clear the entire database
        """
        cursor = self._dbcon.cursor()
        cursor.execute(u"delete from books")
        self._dbcon.commit()
        cursor.close()


    def search(self, term):
        """
        search the database for books containing the search term in the
        filename, title or author column

        term - the search term

        """
        term = u'%' + term.decode('utf8') + u'%'
        cursor = self._dbcon.cursor()
        t = (term, term, term)
        sql = u"""select rowid, * from books where (title like ?) or
                  (author like ?) or (filename like ?)"""
        cursor.execute(sql, t)
        result = cursor.fetchall()
        cursor.close()
        return [self._book_from_query_result(x) for x in result]


    def get_all(self):
        """
        return all books in the database
        """
        cursor = self._dbcon.cursor()
        cursor.execute(u"select rowid,* from books")
        result = cursor.fetchall()
        cursor.close()
        return [self._book_from_query_result(x) for x in result]


    def get_by_id(self, book_id):
        """
        fetch data about an ebook by primary key

        book_id - primary key of the book in the db
        """
        if not isinstance(book_id, str):
            book_id = str(book_id)

        cursor = self._dbcon.cursor()
        sql = u"select rowid,* from books where rowid = %s" % book_id
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        return self._book_from_query_result(result[0])


    def _create_db(self):
        cursor = self._dbcon.cursor()
        cursor.execute(u"""create table books
                           (title text, author text, filename text, path text)
                       """)
        self._dbcon.commit()
        cursor.close()


    def _book_from_query_result(self, result):
        filename = result[3]
        filetype = filename[filename.rfind('.')+1:]
        return Book(bid=result[0], title=result[1], author=result[2],
                    filename=filename, filetype=filetype, path=result[4])

