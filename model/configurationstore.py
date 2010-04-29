# encoding: utf-8

"""
@summary: pointless config file reader/writer
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

class NgLibError(Exception):
    pass


# ***FIXME*** replace with ConfigParser from stdlib
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

        config_file - absolute path to the configuration file
        """
        self._config_file = config_file
        self.config_values = ['dir', 'dbfile', 'pdfcmd', 'chmcmd']
        for value in self.config_values:
            setattr(self, value, None)


    def load(self, check_complete=True):
        """
        Load configuration data from the config file.

        check_complete - raise exception if not all values are present
        """
        with open(self._config_file, 'r') as f:
            config_data = f.read()
            self._parse_config(config_data, check_complete)


    def save(self, check_complete=True):
        """
        Store the configuration in the config file.

        check_complete - only write the data if all values are present
        """
        if check_complete and not self.is_complete():
            raise NgLibError('configuration is not complete')

        with open(self._config_file, 'w') as f:
            for val in self.config_values:
                f.write('%s = %s\n' % (val, getattr(self, val)))


    def _parse_config(self, config_data, check_complete=True):
        """
        Parse a string from the config file.

        config_data - string read from the config file
        check_complete - raise exception if not all values are present
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


