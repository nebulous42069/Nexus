#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   GNU General Public License

#   m-TVGuide KODI Addon
#   Copyright (C) 2020 Mariusz89B
#   Copyright (C) 2016 Andrzej Mleczko

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see https://www.gnu.org/licenses.

#   MIT License

#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:

#   The above copyright notice and this permission notice shall be included in all
#   copies or substantial portions of the Software.

#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#   SOFTWARE.

from __future__ import unicode_literals

import sys

if sys.version_info[0] > 2:
    PY3 = True
else:
    PY3 = False

import requests
import codecs

import os, datetime
import xbmc, xbmcgui, xbmcvfs
from strings import *

URL      = 'https://paste.ubuntu.com/'
if PY3:
    LOGPATH  = xbmcvfs.translatePath('special://logpath')
else:
    LOGPATH  = xbmc.translatePath('special://logpath')
LOGFILE  = os.path.join(LOGPATH, 'kodi.log')
LOGFILE2 = os.path.join(LOGPATH, 'spmc.log')
LOGFILE3 = os.path.join(LOGPATH, 'xbmc.log')

class LogUploader:
    def __init__(self):
        if os.path.isfile(LOGFILE):
            logContent = self.getLog(LOGFILE)
        elif os.path.isfile(LOGFILE2):
            logContent = self.getLog(LOGFILE2)
        elif os.path.isfile(LOGFILE3):
            logContent = self.getLog(LOGFILE3)
        else:
            xbmcgui.Dialog().ok(strings(30150),"\n" + "Unable to find kodi log file")
            return

        logUrl = self.upload(logContent)

        try:
            self.copy2clip(logUrl)
        except:
            deb('LogUploader ERROR not supported OS')

        if logUrl:
            xbmcgui.Dialog().ok(strings(69020),"\n" + strings(69033) + logUrl + strings(69055))
        else:
            xbmcgui.Dialog().ok(strings(30150),"\n" + strings(69034))

    def getLog(self, filename):
        if os.path.isfile(filename):
            content = None
            try:
                if PY3:
                    with open(filename, 'r', encoding='utf-8') as content_file:
                        content = content_file.read()
                else:
                    with codecs.open(filename, 'r', encoding='utf-8') as content_file:
                        content = content_file.read()
            except:
                with open(filename, 'rb') as f:
                    content = f.read().decode(errors='replace')

            if content is None:
                deb('LogUploader upload ERROR could not get content of log file')
            return content
        return None

    def upload(self, data):
        if data is None:
            return None

        startTime = datetime.datetime.now()

        try:
            data = {
              'poster': 'anonymous',
              'syntax': 'text',
              'expiration': 'week',
              'content': data[-1500000:]
            }

            page = requests.post('https://paste.ubuntu.com/', data=data, verify=False)

        except Exception as ex:
            deb('LogUploader upload failed to connect to the server, exception: %s' % getExceptionString())
            deb('LogUploader Uploading files took: %s' % (datetime.datetime.now() - startTime).seconds)
            return None

        deb('LogUploader Uploading files took: %s' % (datetime.datetime.now() - startTime).seconds)

        try:
            page_url = page.url.strip()
            deb('LogUploader success: %s' % str(page_url))
            return page_url
        except Exception as ex:
            deb('LogUploader unable to retrieve the paste url, exception: %s' % getExceptionString())

        return None

    def copy2clip(self, txt):
        import subprocess
        cmd = 'echo '+txt.strip()+'|clip'
        return subprocess.check_call(cmd, shell=True)

logup = LogUploader()
