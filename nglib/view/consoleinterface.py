# encoding: utf-8

"""
@summary: implements a console-based UI using STFL
@author: Haiko Schol alsihad (at) zeropatience (dot) net

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

from cStringIO import StringIO
import stfl


class ProgressBar(object):
    """
    Display a progress bar on the console.
    """

    def __init__(self, total, initial=0.0, block='=', cur_block='>',
                 start_delim='[', end_delim=']', width=52):
        """
        Create a progress bar.

        total - total amount of progress to be made
        initial - initial amount of progress
        block - character used for the "filled" part of the bar
        cur_block - character used for the current block
        start_delim - character used for the left border
        end_delim - character used for the right border
        width - width of the progress bar in characters, incl. delimiters
        """
        self.total = total
        self.current = float(initial)
        self.block = block
        self.cur_block = cur_block
        self.start_delim = start_delim
        self.end_delim = end_delim
        self.width = width
        self._net_width = width - len(start_delim) + len(end_delim)
        self._done = False


    def show(self):
        """
        Display the progress bar.

        newline_when_done - print a newline at 100% progress
        """
        if self._done:
            return

        blocks = self._get_blocks()
        empty = (self._net_width - len(blocks)) * ' '
        bar = '\r%s%s%s%s' % (self.start_delim, blocks, empty, self.end_delim)
        print bar,

        if self.current == self.total:
            self._done = True

        import sys
        sys.stdout.flush()


    def progress(self, amount=1):
        """
        Increase the progress by the given amount and update the progress
        bar on the screen.
        """
        if (amount > self.total) or (amount + self.current > self.total):
            self.current = self.total
        elif amount > 0:
            self.current = self.current + amount

        self.show()


    def _get_blocks(self):
        """
        Figure out how many blocks to display for the current amount.
        """
        if self.current == self.total:
            return self._net_width * self.block

        percent = self.current / self.total * 100
        scaled = int(percent / (100.0 / self._net_width))
        return '%s%s' % (scaled * self.block, self.cur_block)


class ReloadLibraryDialog(object):
    """
    display progress on reloading the library
    """
    stfl_layout = """
vbox
    modal:1
    table
        .tie:c
        label
            .colspan:2 .expand:0 .tie:c .border:lrtb
            text:"Reloading Library..."
        tablebr
        label
            .colspan:2 .expand:0 .tie:c .border:lrtb
            text[bookcount]:"Books found:"
        tablebr
        label
            .colspan:2 .expand:0 .tie:c .border:lrtb
            text[progress]:"Books added:"
"""

    def __init__(self, controller):
        """
        construct and display a reload library dialog

        controller - an object which provides methods for reloading the library
        """
        self._ctrl = controller
        self._form = stfl.create(self.stfl_layout)
        self._form.run(1)


    def run(self):
        """
        perform the reload and display progress
        """
        bookcount = self._ctrl.count_books()
        self._form.set('bookcount', 'Books found: %i' % bookcount)

        for num in self._ctrl.reload_library():
            self._form.set('progress', 'Books added: %i' % num[1])
            self._form.run(1)


class SettingsDialog(object):
    """
    provide a dialog for editing configuration settings
    """
    stfl_layout = """
table
    modal:1
    label
        .colspan:2 .expand:0 .tie:c .border:lrtb
        text:"Settings"
    tablebr
    label
        .border:lb .expand:0
        text:"eBook Library Location:"
    input[dir]
        .border:rb .expand:h
        style_normal:fg=blue,bg=black
        style_focus:fg=white,bg=black
        text[dirtxt]:
        on_DOWN:focus_pdfcmd
        on_TAB:focus_pdfcmd
    tablebr
    label
        .border:lb .expand:0
        text:"Open PDF files with:"
    input[pdfcmd]
        .border:rb .expand:h
        style_normal:fg=blue,bg=black
        style_focus:fg=white,bg=black
        text[pdfcmdtxt]:
        on_UP:focus_dir
        on_DOWN:focus_chmcmd
        on_TAB:focus_chmcmd
    tablebr
    label
        .border:lb .expand:0
        text:"Open CHM files with:"
    input[chmcmd]
        .border:rb .expand:h
        style_normal:fg=blue,bg=black
        style_focus:fg=white,bg=black
        text[chmcmdtxt]:
        on_UP:focus_pdfcmd
        on_DOWN:focus_showcmd
        on_TAB:focus_showcmd
    tablebr
    label
        .border:lb .expand:0
        text:"Reveal files in:"
    input[showcmd]
        .border:rb .expand:h
        style_normal:fg=blue,bg=black
        style_focus:fg=white,bg=black
        text[showcmdtxt]:
        on_UP:focus_chmcmd
    tablebr
    label
        .colspan:2 .tie:c .border:lr .expand:0
        text:"Ctrl-U - Cancel    Ctrl-R: Reload Library"
    tablebr
    label
        .colspan:2 .tie:c .border:lrb .expand:0
        text:"Ctrl-X - Save settings and close"
"""

    def __init__(self, controller):
        """
        construct a settings dialog

        controller - an object which provides methods for reading and writing settings
        """
        self._ctrl = controller


    def show(self):
        """
        display the dialog and run the event loop
        """
        self._form = stfl.create(self.stfl_layout)
        self._update_view(self._form, self._ctrl)
        self._form.set_focus('dir')

        while True:
            e = self._form.run(0)
            if e == 'focus_dir':
                self._form.set_focus('dir')
            elif e == 'focus_pdfcmd':
                self._form.set_focus('pdfcmd')
            elif e == 'focus_chmcmd':
                self._form.set_focus('chmcmd')
            elif e == 'focus_showcmd':
                self._form.set_focus('showcmd')
            elif e == '^R':
                if self._ctrl.get_setting('dir') != self._form.get('dirtxt'):
                    self._form.set('dirtxt', self._ctrl.get_setting('dir'))
                self._reload_library(self._ctrl)
            elif e == '^U':
                return
            elif e == '^X':
                oldlibdir = self._ctrl.get_setting('dir')
                self._save(self._form, self._ctrl)
                if oldlibdir != self._ctrl.get_setting('dir'):
                    self._reload_library(self._ctrl)
                return


    def _save(self, form, ctrl):
        """
        save the content of dialog widgets to a ConfigurationStore object
        FIXME do sanity checking on the values: check whether dirs and files exist

        form - a form from which the data should be read
        ctrl - a controller object, that provides a set_setting() method
        """
        ctrl.set_setting('dir', form.get('dirtxt'))
        ctrl.set_setting('pdfcmd', form.get('pdfcmdtxt'))
        ctrl.set_setting('chmcmd', form.get('chmcmdtxt'))
        ctrl.set_setting('showcmd', form.get('showcmdtxt'))
        ctrl.write_settings()


    def _update_view(self, form, ctrl):
        """
        put the data from a ConfigurationStore object into dialog widgets

        form - a stfl form to which the data should be written
        ctrl - an object which provides a get_setting() method
        """
        form.set('dirtxt', ctrl.get_setting('dir'))
        form.set('pdfcmdtxt', ctrl.get_setting('pdfcmd'))
        form.set('chmcmdtxt', ctrl.get_setting('chmcmd'))
        form.set('showcmdtxt', ctrl.get_setting('showcmd'))


    def _reload_library(self, ctrl):
        """
        reload the library

        ctrl - an object which provides methods for reloading the library
        """
        reloader = ReloadLibraryDialog(self._ctrl)
        reloader.run()


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
    style_normal:fg=blue,bg=black
    style_focus:fg=white,bg=black
    text[searchterm]:
  tablebr
  !list[booklist]
    on_TAB:focussearch
    on_ENTER:openbook
    bind_up:"** k"
    bind_down:"** j"
    bind_page_up:"** ^U"
    bind_page_down:"** ^F"
    bind_home:"** g"
    bind_end:"** G"
    .colspan:2 .border:rltb
    style_focus:fg=blue
    pos_name[listposname]:
    pos[listpos]:0
  tablebr
  label
    .colspan:2 .border:rlt .expand:0 .tie:c
    text:"TAB: Search/List    Ctrl-D: Clear Search    Enter: Open File"
  tablebr
  label
    .colspan:2 .border:rlb .expand:0 .tie:c
    text:"Ctrl-R: Reveal File    Ctrl-P: Settings    Ctrl-X: Quit"
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
            if e == 'focussearch':
                self._form.set_focus('search')
            elif e == 'focuslist':
                self._form.set_focus('booklist')
            elif e == 'performsearch':
                self._perform_search(self._form.get('searchterm'))
            elif e == 'openbook':
                self._ctrl.open_book(self._form.get('listpos'))
            elif e == '^X':
                self._ctrl.shutdown()
            elif e == '^D':
                self._clear_search_results()
            elif e == '^P':
                settings = SettingsDialog(self._ctrl)
                settings.show()
                self._fill_list(self._ctrl.get_all())
            elif e == '^R':
                self._ctrl.show_book(self._form.get('listpos'))


    def _perform_search(self, term):
        self._fill_list(self._ctrl.search(term))


    def _clear_search_results(self):
        self._form.set('searchterm', '')
        self._fill_list(self._ctrl.get_all())


    def _fill_list(self, items):
        items = [x.title for x in items]
        buf = StringIO()
        buf.write('{list')
        count = 0
        for item in items:
            val = item.encode('utf8')
            buf.write('{listitem[%d] text:"%s"}' % (count, val))
        buf.write('}')
        self._form.modify('booklist', 'replace_inner', buf.getvalue())
        buf.close()
        self._form.set('listpos', '0')

