#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   GNU General Public License

#   m-TVGuide KODI Addon
#   Copyright (C) 2020 Mariusz89B
#   Copyright (C) 2020 mbebe
#   Copyright (C) 2019 Andrzej Mleczko

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

#   Disclaimer
#   This add-on is unoffical and is not endorsed or supported by WIRTUALNA POLSKA MEDIA S.A. in any way. Any trademarks used belong to their owning companies and organisations.

from __future__ import unicode_literals

import sys

if sys.version_info[0] > 2:
    PY3 = True
else:
    PY3 = False

import os
import xbmc, xbmcvfs
from strings import *
from serviceLib import *
import requests
import json

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

if PY3:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

serviceName         = 'WP Pilot'
login_url = 'https://pilot.wp.pl/api/v1/user_auth/login?device_type=android_tv'
main_url = 'https://pilot.wp.pl/api/v1/channels/list?device_type=android_tv'
video_url = 'https://pilot.wp.pl/api/v1/channel/'
close_stream_url = 'https://pilot.wp.pl/api/v1/channels/close?device_type=android_tv'

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36 Edg/98.0.1108.50'

headers = {
    'user-agent': UA,
    'content-type': 'application/json;charset=UTF-8',
    'accept': 'application/json, text/plain, */*'
}

if PY3:
    try:
        profilePath  = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
    except:
        profilePath  = xbmcvfs.translatePath(ADDON.getAddonInfo('profile')).decode('utf-8')
else:
    try:
        profilePath  = xbmc.translatePath(ADDON.getAddonInfo('profile'))
    except:
        profilePath  = xbmc.translatePath(ADDON.getAddonInfo('profile')).decode('utf-8')

cacheFile = os.path.join(profilePath, 'cache.db')

sess = requests.Session()

class WpPilotUpdater(baseServiceUpdater):
    def __init__(self):
        self.serviceName        = serviceName
        self.localMapFile       = 'basemap_pl.xml'
        baseServiceUpdater.__init__(self)
        self.serviceEnabled     = ADDON.getSetting('videostar_enabled')
        self.login              = ADDON.getSetting('videostar_username').strip()
        self.password           = ADDON.getSetting('videostar_password').strip()
        self.servicePriority    = int(ADDON.getSetting('priority_videostar'))
        self.netviapisessid     = ADDON.getSetting('videostar_netviapisessid')
        self.netviapisessval    = ADDON.getSetting('videostar_netviapisessval')
        self.remote_cookies     = ADDON.getSetting('videostar_remote_cookies')
        
    def saveToDB(self, table_name, value):
        import sqlite3
        import os
        if os.path.exists(cacheFile):
            os.remove(cacheFile)
        else:
            deb('File does not exists')
        conn = sqlite3.connect(cacheFile, detect_types=sqlite3.PARSE_DECLTYPES, cached_statements=20000)
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS Cache(%s TEXT)' % table_name)
        c.execute("INSERT INTO Cache('%s') VALUES ('%s')" % (table_name, value))
        conn.commit()
        c.close()

    def readFromDB(self):
        import sqlite3
        conn = sqlite3.connect(cacheFile, detect_types=sqlite3.PARSE_DECLTYPES, cached_statements=20000)
        c = conn.cursor()
        c.execute("SELECT * FROM Cache")
        for row in c:
            if row:
                c.close()
                return row[0]

    def cookiesToString(self, cookies):
        try:
            return "; ".join([str(x) + "=" + str(y) for x, y in cookies.items()])
        except Exception as ex:
            deb('cookiesToString exception: ' + ex)
            return ''

    def loginService(self):
        try:
            if self.netviapisessval == '' and self.netviapisessid == '':
                if len(self.password) > 0 and len(self.login) > 0:
                    data = {'device': 'android_tv',
                            'login': self.login,
                            'password': self.password}

                    response = requests.post(
                        login_url,
                        json=data,
                        verify=False,
                        headers=headers
                    )

                    meta = response.json().get('_meta', None)
                    if meta is not None:
                        if meta.get('error', {}).get('name', None) is not None:
                            self.loginErrorMessage()
                            return False

                    self.saveToDB('wppilot_cache', self.cookiesToString(response.cookies))
                    return True

                else:
                    self.loginErrorMessage()
                    return False
            else:
                if len(self.netviapisessval) > 0 and len(self.netviapisessid) > 0:
                    cookies = {'netviapisessid': self.netviapisessid, 'netviapisessval': self.netviapisessval}
                    self.saveToDB('wppilot_cache', self.cookiesToString(cookies))
                    return True

                elif len(self.remote_cookies) > 0:
                    cookies_from_url = requests.get(self.remote_cookies, verify=False, timeout=10).text
                    cookies = json.loads(cookies_from_url)
                    self.saveToDB('wppilot_cache', self.cookiesToString(cookies))
                    return True
                else:
                    self.loginErrorMessage()
                    return False

        except:
            self.connErrorMessage()
            self.log('getLogin exception: {}'.format(getExceptionString()))
        return False

    def getChannelList(self, silent):
        result = list()
        if not self.loginService():
            return result

        self.log('\n\n')
        self.log('[UPD] Downloading list of available {} channels from {}'.format(self.serviceName, self.url))
        self.log('[UPD] -------------------------------------------------------------------------------------')
        self.log('[UPD] %-12s %-35s %-35s' % ( '-CID-', '-NAME-', '-TITLE-'))

        try:
            cookies = self.readFromDB()
            headers.update({'Cookie': cookies})
            response = requests.get(main_url, verify=False, headers=headers).json()

            data = response.get('data', [])

            for channel in data:
                if channel.get('access_status', '') != 'unsubscribed':
                    cid  = channel['id']
                    name = channel['name']

                    p = re.compile(r'(\sPL$)')

                    r = p.search(name)
                    match = r.group(1) if r else None

                    if match:
                        title = channel['name']
                    else:
                        title = channel['name'] + ' PL'

                    img  = channel['thumbnail_mobile']
                    geoblocked = channel['geoblocked']
                    slug = channel['slug']
                    access = channel['access_status']
                    self.log('[UPD] %-10s %-35s %-15s %-20s %-35s' % (cid, name, geoblocked, access, img))
                    if geoblocked != True and access != 'unsubscribed':
                        program = TvCid(cid=cid, name=name, title=title, img=img, lic=slug)
                        result.append(program)

                        self.log('[UPD] %-12s %-35s %-35s' % (cid, name, title))

            if len(result) <= 0:
                self.log('Error while parsing service {}, returned data is: {}'.format(self.serviceName, str(response)))

            self.log('-------------------------------------------------------------------------------------')

        except:
            self.connErrorMessage()
            self.log('getChannelList exception: {}'.format(getExceptionString()))
        return result

    def getChannelStream(self, chann=None, vid=None, retry=False):
        if not retry:
            video_id = chann.cid
        else:
            video_id = vid

        try:
            cookies = self.readFromDB()
            if len(video_id) == 0:
                return

            url = video_url + video_id + '?format_id=2&device_type=android_tv'
            data = {'format_id': '2', 'device_type': 'android'}

            headers.update({'Cookie': cookies})
            response = requests.get(
                url,
                params=data,
                verify=False,
                headers=headers,
            ).json()

            try:
                if response['_meta']['error']['name'] == 'user_not_verified_eu':
                    self.geoBlockErrorMessage()
            except:
                pass

            meta = response.get('_meta', None)
            if meta is not None:
                token = meta.get('error', {}).get('info', {}).get('stream_token', None)
                if token is not None:
                    json = {'channelId': video_id, 't': token}
                    response = requests.post(
                        close_stream_url,
                        json=json,
                        verify=False,
                        headers=headers
                    ).json()
                    if response.get('data', {}).get('status', '') == 'ok' and not retry:
                        return self.getChannelStream(vid=chann.cid, retry=True)
                    else:
                        return

            headersx = {
                'authority': 'pilot.wp.pl',
                'rtt': '50',
                'user-agent': UA,
                'dpr': '1',
                'downlink': '10',
                'ect': '4g',
                'accept': '*/*',
                'origin': 'https://pilot.wp.pl',
                'referer': 'https://pilot.wp.pl/tv/',
                'accept-language': 'sv,en;q=0.9,en-GB;q=0.8,en-US;q=0.7,pl;q=0.6',
                }

            headersx.update({'Cookie': cookies})

            LICENSE = ''
            LICENSE_URL = 'https://pilot.wp.pl'

            headers_mpd = {}

            try:
                manifest = response[u'data'][u'stream_channel'][u'streams'][0][u'url'][0]
                widevine = response[u'data'][u'stream_channel']['drms']['widevine']

                headers_mpd = {
                    'user-agent': UA,
                    'x-qoe-cdn': manifest,
                    'accept': '*/*',
                    'origin': 'https://pilot.wp.pl',
                    'referer': 'https://pilot.wp.pl/',
                    'accept-language': 'sv,en;q=0.9,en-GB;q=0.8,en-US;q=0.7,pl;q=0.6',
                    }
                
                headers_mpd.update({'Cookie': cookies})
                
                LICENSE = LICENSE_URL + widevine + '|' + urlencode(headersx) +'|R{SSM}|'

                stream = manifest + '|' + urlencode(headers_mpd)

            except:
                if 'hls@live:abr' in response[u'data'][u'stream_channel'][u'streams'][0][u'type']:
                    manifest = response[u'data'][u'stream_channel'][u'streams'][0][u'url'][0]
                    stream = response['data']['stream_channel']['streams'][0]['url'][0] + '|user-agent=' + headers['user-agent'] + '&cookie=' + cookies
                else:
                    manifest = response[u'data'][u'stream_channel'][u'streams'][1][u'url'][0]
                    stream = response['data']['stream_channel']['streams'][1]['url'][0] + '|user-agent=' + headers['user-agent'] + '&cookie=' + cookies

            if stream is not None and stream != "":
                chann.strm = stream
                chann.lic = LICENSE, urlencode(headers_mpd)

                self.log('getChannelStream found matching channel: cid: {}, name: {}, rtmp:{}'.format(chann.cid, chann.name, chann.strm))
                return chann
            else:
                self.log('getChannelStream error getting channel stream2, result: {}'.format(str(stream)))
                return None

        except Exception:
            self.log('getChannelStream exception while looping: {}\n Data: {}'.format(getExceptionString(), str(stream)))
        return None
