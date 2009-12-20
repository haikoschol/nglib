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

from cStringIO import StringIO
import stfl

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

    def __init__(self, controller):
        """
        create a ConsoleInterface object

        controller -- module providing an interface to the book database

        """
        self._ctrl = controller
        self._form = stfl.create(self.stfl_layout)
        self._fill_list(self._ctrl.get_all())


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
                self._ctrl.shutdown()
            elif e == '^D':
                self._clear_search_results()


    def _perform_search(self, term):
        self._fill_list(self._ctrl.search(term))


    def _clear_search_results(self):
        self._form.set('searchterm', '')
        self._fill_list(self._ctrl.get_all())


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

