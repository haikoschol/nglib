#!/usr/bin/env python
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

from __future__ import with_statement
import os
import sqlite3
from cStringIO import StringIO

import stfl

from pyPdf import PdfFileReader
#from chm import chm


class NgLibError(Exception):
    pass


class BookDatabase(object):
    """
    thin wrapper around sqlite for adding, removing and searching
    pdf and chm files
    all strings assumed to be utf-8 encoded bytestrings
    """
    def __init__(self, path):
        """
        create a BookDatabase object
                
        path -- absoulte path to the sqlite db file
                (if it doesn't exist a new one will be created)
        """
        path = path.decode('utf8')
        self._dbfile = path
        empty = not os.path.exists(path)
        self._dbcon = sqlite3.connect(path)
        if empty:
            self._create_db()
        

    def close(self):
        """
        close the underlying sqlite connection
        (should not be part of the API, RAII would be cool...)
        """
        self._dbcon.close()
        
        
    def add(self, path, title, author):
        """
        add a book to the database
                
        path -- absolute path to the file
        title -- title of the book
        author -- author of the book
                
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
        
        path -- absolute path to the file
        
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
        
        term -- the search term
        
        """
        term = u'%' + term.decode('utf8') + u'%'
        cursor = self._dbcon.cursor()
        t = (term, term, term)
        sql = u"""select * from books where (title like ?) or
                  (author like ?) or (filename like ?)"""
        cursor.execute(sql, t)
        result = cursor.fetchall()
        cursor.close()
        return result
    
    
    def get_all(self):
        """
        return all books in the database
        """
        cursor = self._dbcon.cursor()
        cursor.execute(u"select * from books")
        result = cursor.fetchall()
        cursor.close()
        return result
    
   
    def _create_db(self):
        cursor = self._dbcon.cursor()
        cursor.execute(u"""create table books
                           (title text, author text, filename text, path text)
                       """)
        self._dbcon.commit()
        cursor.close()
        
    
def add_pdf(path, database):
    """
    add metadata (title and author) from a pdf file to the database
    
    path -- absolute path to a pdf file
    database -- BookDatabase object
    
    """
    result = False
    try:
        f = open(path, 'rb')
        doc = PdfFileReader(f)
        title = doc.getDocumentInfo().title
        author = doc.getDocumentInfo().author
        if title: # if title is empty, rather use the filename
            database.add(path, title, author)
            result = True
    except:
        pass
    finally:
        f.close()
    return result


def add_chm(path, database):
    """
    add metadata (title) from a chm file to the database
    
    path -- absolute path to a chm file
    database -- BookDatabase object
    
    """
    try:
        chmfile = chm.CHMFile()
        if not chmfile.LoadCHM(path):
            database.add(path, '', '')
            return True
        database.add(path, chmfile.title, '')
        chmfile.CloseCHM()
        return True
    except:
        return False


def add_file(path, database):
    """
    don't try to extract any metadata, just use the filename
    (slightly prettyfied) as title and a blank string as author.
    ignore all files with no pdf or chm extension.
    
    path -- absolute path to a file
    database -- BookDatabase object
    
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
    
    path -- root of the directory tree
    extensions -- iterable of file extensions to count
    
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
    have been added in the last call.
    
    path -- absolute path to the directory to walk
    database -- BookDatabase object
    add_per_run -- how many files should be added per call
    
    """
    count = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            ext = file.split('.')[-1].lower()
            abspath = os.path.join(root, file)
            if ext in ('pdf', 'chm'):
                added = False
                if ext == 'pdf':
                    added = add_pdf(abspath, database)
                if not added:
                    add_file(abspath, database)
                count += 1
            if count == add_per_run:
                yield count
                count = 0
    yield count


class ConfigurationStore(object):
    """
    This class represents configuration data that can be stored
    and loaded to/from disk.
    """

    def __init__(self, config_file=os.path.join(os.path.expanduser('~'),
                                                '.nglib',
                                                'nglibrc')):
        """
        Constructor.
        
        config_file -- absolute path to the configuration file
        """
        self._config_file = config_file
        self.config_values = ['dir', 'dbfile', 'pdfcmd', 'chmcmd']
        for value in self.config_values:
            setattr(self, value, None)


    def load(self, check_complete=True):
        """
        Load configuration data from the config file.

        check_complete -- raise exception if not all values are present
        """
        with open(self._config_file, 'r') as f:
            config_data = f.read()
            self._parse_config(config_data, check_complete)
       

    def save(self, check_complete=True):
        """
        Store the configuration in the config file.

        check_complete -- only write the data if all values are present
        """
        if check_complete and not self.is_complete():
            raise NgLibError('configuration is not complete')

        with open(self._config_file, 'w') as f:
            for val in self.config_values:
                f.write('%s = %s\n' % (val, getattr(self, val)))


    def _parse_config(self, config_data, check_complete=True):
        """
        Parse a string from the config file.
        
        config_data -- string read from the config file
        check_complete -- raise exception if not all values are present
        """
        lines = [l.strip() for l in config_data.split('\n')]
        for line in lines:
            if line.startswith('#'):
                continue

            splitat = line.find('=')
            key = line[:splitat].strip()
            value = line[splitat+1:].strip()

            if not key or key not in self.config_values:
                continue

            setattr(self, key, value)

        if check_complete and not self.is_complete():
            raise NgLibError('config is not complete')


    def is_complete(self):
        """
        Return true if no config values are None.
        """
        for value in self.config_values:
            if getattr(self, value) is None:
                return False
        return True


class ConsoleInterface(object):
    """
    display a console user interface using STFL
    """
    stfl_layout = """
table
  label
    .colspan:2 .expand:0 .tie:c
    text:"nglib - eBook Library Search"
  tablebr
  label
    .border:ltb .expand:0
    text:"Search: "
  input[search]
    on_TAB:focuslist
    on_ENTER:performsearch
    .border:rtb .expand:h
    style_normal:attr=underline
    style_focus:fg=blue,attr=underline
    text[searchterm]:
  tablebr
  !list[booklist]
    on_TAB:focussearch
    on_ENTER:openbook
    .colspan:2 .border:rltb
    style_focus:fg=blue
    pos_name[listposname]:
    pos[listpos]:0
  tablebr
  label
    .colspan:2 .border:rltb .expand:0
    text:"TAB: Search/List  Ctrl-D: Clear Search  Ctrl-O: Open File  Ctrl-X: Quit" 
  tablebr
"""
    
    def __init__(self, database, config):
        """
        create a ConsoleInterface object
        
        database -- BookDatabase object
        config -- ConfigurationStore object
        
        """
        self._db = database
        self._config = config
        self._form = stfl.create(self.stfl_layout)
        self._fill_list(self._db.get_all())
       
    
    def run(self):
        self._form.set_focus('search')
        while True:
            try:
                e = self._form.run(0)
            except KeyboardInterrupt:
                pass
            f.write('%s\n' % e)
            if e == 'focussearch':
                self._form.set_focus('search')
            elif e == 'focuslist':
                self._form.set_focus('booklist')
            elif e == 'performsearch':
                self._perform_search(self._form.get('searchterm'))
            elif e == 'openbook':
                pass # ***FIXME*** open file in external viewer
            elif e == '^X':
                self._db.close()
                return
            elif e == '^D':
                self._clear_search_results()
                
    
    def _perform_search(self, term):
        self._fill_list(self._db.search(term))
        
    
    def _clear_search_results(self):
        self._form.set('searchterm', '')
        self._fill_list(self._db.get_all())
    
    
    def _fill_list(self, items):
        buf = StringIO()
        buf.write('{list')
        count = 0
        for item in items:
            val = item[0].encode('utf8')
            buf.write('{listitem[%d] text:"%s"}' % (count, val))
        buf.write('}')
        self._form.modify('booklist', 'replace_inner', buf.getvalue())
        buf.close()
        self._form.set('listpos', '0')


def first_run(datadir, cfgfile):
    """
    return True if this is the first time nglib is run

    datadir -- path to the dir where config file and database should be stored
    cfgfile -- name of the config file
    
    """
    if not os.path.exists(datadir):
        return True
    
    cfgfile = os.path.join(datadir, cfgfile)
    if not os.path.exists(cfgfile):
        return True
    
    config = ConfigurationStore(cfgfile)
    try:
        config.load()
    except:
        return True
    
    return False
    
    
def first_run_wizard(config, datadir):
    """
    ask user for configuration settings
    """
    print 'It seems like this is the first time you run nglib.'
    print 'Let me ask you some questions real quick...'
    print 'Please tell me the absolute path to your eBook collection.'
    print 'eBook library location: ',
    dir = raw_input()
    while not os.path.exists(dir):
        print "That directory doesn't exist. Please try again."
        print 'eBook library location: ',
        dir = raw_input()
    
    print 'What command should be used to open PDF files?'
    print 'PDF viewer [/usr/bin/evince]: ',
    pdfcmd = raw_input()
    if not pdfcmd:
        pdfcmd = '/usr/bin/evince'
    while not os.path.exists(pdfcmd):
        print "That file doesn't exist. Please try again."
        print 'PDF viewer [/usr/bin/evince]: ',
        pdfcmd = raw_input()
        if not pdfcmd:
            pdfcmd = '/usr/bin/evince'
    
    print 'What command should be used to open CHM files?'
    print 'CHM viewer [/usr/bin/gnochm]: ',
    chmcmd = raw_input()
    if not chmcmd:
        chmcmd = '/usr/bin/gnochm'
    while not os.path.exists(chmcmd):
        print "That file doesn't exist. Please try again."
        print 'CHM viewer [/usr/bin/gnochm]: ',
        chmcmd = raw_input()
        if not chmcmd:
            chmcmd = '/usr/bin/gnochm'
    
    config.dir = dir
    config.dbfile = os.path.join(datadir, 'books.db')
    config.pdfcmd = pdfcmd
    config.chmcmd = chmcmd
    

def perform_first_run(datadir, cfgfile):
        try:
            os.mkdir(datadir)
        except:
            pass # dir might already exist
        config = ConfigurationStore(os.path.join(datadir, cfgfile))
        first_run_wizard(config, datadir)
        config.save()
        print 'adding PDF and CHM files in directory %s' % config.dir
        db = BookDatabase(config.dbfile)
        count = count_files(config.dir)
        print '%d files found' % count
        print 'adding files to database %s' % config.dbfile
        added = 0
        for num in add_books(config.dir, db):
            added += num
            print 'added %d of %d files' % (added, count)
        print 'done'
        return db, config


if __name__ == '__main__':
    datadir = os.path.join(os.path.expanduser('~'), '.nglib')
    cfgfile = 'nglibrc'
    
    if first_run(datadir, cfgfile):
        db, config = perform_first_run(datadir, cfgfile)
    else:
        config = ConfigurationStore(os.path.join(datadir, cfgfile))
        config.load()
        db = BookDatabase(config.dbfile)
        
    ui = ConsoleInterface(db, config)
    ui.run()
    
