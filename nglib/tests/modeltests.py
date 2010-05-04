# encoding: utf-8

"""
@summary: unit tests for classes in the model package
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
import unittest
from tempfile import gettempdir
from tempfile import mkstemp 
from os.path import join as pjoin

from nglib.model.bookdatabase import BookDatabase

class BookDatabaseTest(unittest.TestCase):
    """
    test the BookDatabase class
    """

    def setUp(self):
        self.bookspath = gettempdir() or os.path.abspath(os.getcwd())
        fd, name = mkstemp('.db', dir=self.bookspath)
        self.tmpfile = pjoin(self.bookspath, name)
        os.close(fd)
        self.db = BookDatabase(self.tmpfile)
        self.db._create_db() # cheating in tests is ok, right? :)
        self.testbooks = [(pjoin(self.bookspath, u'cooking_for_geeks.pdf'),
                           u'cooking for geeks',
                           u'jeff potter'),
                          (pjoin(self.bookspath, u'hitchhikers_guide.pdf'),
                           u'the hitchhikers guide to the galaxy',
                           u'douglas adams'),
                          (pjoin(self.bookspath, u'neuromancer.pdf'),
                           u'neuromancer',
                           u'william gibson'),
                          (pjoin(self.bookspath, u'snowcrash.pdf'),
                           u'snow crash',
                           u'neal stephenson'),]


    def tearDown(self):
        self.db.close()
        os.unlink(self.tmpfile)


    def addBooks(self, count):
        books = self.testbooks[:count]
        for book in books:
            self.db.add(*book)


    def testAdd(self):
        testbook = self.testbooks[0]
        path = testbook[0]
        title = testbook[1]
        author = testbook[2]
        filename = os.path.basename(path)
        
        self.db.add(path, title, author)
        self.db.close()
        db = sqlite3.connect(self.tmpfile)
        cursor = db.cursor()
        cursor.execute('select * from books')
        result = cursor.fetchall()
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), len(testbook)+1)
        self.assertEqual(result[0][0], title)
        self.assertEqual(result[0][1], author)
        self.assertEqual(result[0][2], filename)
        self.assertEqual(result[0][3], self.bookspath)
        
        cursor.execute('delete from books')
        cursor.close()
        db.close()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()