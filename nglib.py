#!/usr/bin/env python
# encoding: utf-8

"""
@summary: nglib is a simple application for searching an ebook collection.
@version: 0.0.3
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

from __future__ import with_statement
import os

from model.bookdatabase import BookDatabase
from model.configurationstore import ConfigurationStore
from controller.controller import Controller
from view.consoleinterface import ConsoleInterface


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
    count = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            ext = file.split('.')[-1].lower()
            abspath = os.path.join(root, file)
            if ext in ('pdf', 'chm'):
                add_file(abspath, database)
                count += 1
                if count % add_per_run == 0:
                    yield count
    yield count


def first_run(datadir, cfgfile):
    """
    return True if this is the first time nglib is run

    datadir - path to the dir where config file and database should be stored
    cfgfile - name of the config file

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


def get_default_open_cmd():
    """
    return absolute path to the binary used for opening files
    """
    import platform
    if 'darwin' in platform.platform().lower():
        return '/usr/bin/open'
    else:
        return '/usr/bin/xdg-open'  # FIXME add windows support


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

    default_open_cmd = get_default_open_cmd()
    print 'What command should be used to open PDF files?'
    print 'PDF viewer [%s]: ' % default_open_cmd,
    pdfcmd = raw_input()
    if not pdfcmd:
        pdfcmd = default_open_cmd
    while not os.path.exists(pdfcmd):
        print "That file doesn't exist. Please try again."
        print 'PDF viewer: ',
        pdfcmd = raw_input()
        if not pdfcmd:
            pdfcmd = default_open_cmd

    print 'What command should be used to open CHM files?'
    print 'CHM viewer [%s]: ' % default_open_cmd,
    chmcmd = raw_input()
    if not chmcmd:
        chmcmd = default_open_cmd
    while not os.path.exists(chmcmd):
        print "That file doesn't exist. Please try again."
        print 'CHM viewer: ',
        chmcmd = raw_input()
        if not chmcmd:
            chmcmd = default_open_cmd

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
            print 'added %d of %d files' % (num, count)
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

    controller = Controller(db, config)
    ui = ConsoleInterface(controller)
    controller.add_view(ui, ui.run)
    controller.run()

