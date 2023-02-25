#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   GNU General Public License

#   m-TVGuide KODI Addon
#   Copyright (C) 2022 Mariusz89B
#   Copyright (C) 2022 rysson
#   Copyright (C) 2018 primaeval
#   Copyright (C) 2016 Andrzej Mleczko
#   Copyright (C) 2014 Krzysztof Cebulski
#   Copyright (C) 2013 Szakalit
#   Copyright (C) 2013 Tommy Winther

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

if PY3:
    import urllib.request, urllib.error, urllib.parse
    import configparser
else:
    import urllib
    import ConfigParser

from collections import Counter
import threading
import requests
import urllib3
import os, re, time, io, zipfile

from datetime import datetime, timedelta
try:
    from datetime import timezone
except ImportError:
    pass

import xbmc, xbmcgui, xbmcvfs
import shutil
import playService
import serviceLib
import sqlite3
import codecs

from xml.etree import ElementTree
from strings import *
import strings as strings2

from itertools import chain
from skins import Skin
from random import uniform
from unidecode import unidecode

from groups import *

UA = xbmc.getUserAgent()

if PY3:
    try:
        PROFILE_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
    except:
        PROFILE_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('profile')).decode('utf-8')
else:
    try:
        PROFILE_PATH = xbmc.translatePath(ADDON.getAddonInfo('profile'))
    except:
        PROFILE_PATH = xbmc.translatePath(ADDON.getAddonInfo('profile')).decode('utf-8')

PREDEFINED_CATEGORIES = []
EPG_LIST = []

EPG_DICT = {}

CC_DICT = ccDict()

for k, v in CC_DICT.items():
    epg = ADDON.getSetting('epg_{cc}'.format(cc=k)).strip()
    cc = ADDON.getSetting('country_code_{}'.format(k.lower()))

    if cc == 'true' and cc != '':
        EPG_DICT.update({k: v})
        if epg and epg != '':
            EPG_LIST.append(epg)

    if k == 'all':
        all_channels = strings(30325)
        PREDEFINED_CATEGORIES.append(all_channels)
    else:
        if cc == 'true' and cc != '':
            PREDEFINED_CATEGORIES.append(k.upper())

# ADDON settings
SOURCE = ADDON.getSetting('source')
if SOURCE == '0':
    GET_SOURCE = '0'
else:
    GET_SOURCE = '1'

PARSER = ADDON.getSetting('useCustomParser')
if PARSER == 'true':
    CUSTOM_PARSER = True
else:
    CUSTOM_PARSER = False

AUTO_CID = ADDON.getSetting('AutoUpdateCid')
if AUTO_CID == 'true':
    UPDATE_CID = True
else:
    UPDATE_CID = False

DATABASE_CLEARED = ADDON.getSetting("database_cleared")
if DATABASE_CLEARED == 'true':
    GET_DATABASE_CLEARED = True
else:
    GET_DATABASE_CLEARED = False

PRAGMA_MODE = ADDON.getSetting("pragma_mode")
if PRAGMA_MODE == 'true':
    GET_PRAGMA_MODE = True
else:
    GET_PRAGMA_MODE = False

ALT_CHANN = ADDON.getSetting('epg_display_name')
if ALT_CHANN == 'true':
    CH_DISP_NAME = True
else:
    CH_DISP_NAME = False

EPG_INTERVAL = ADDON.getSetting('epg_interval')
if EPG_INTERVAL == '0':
    GET_EPG_INTERVAL = 0
elif EPG_INTERVAL == '1':
    GET_EPG_INTERVAL = 1
elif EPG_INTERVAL == '2':
    GET_EPG_INTERVAL = 2
elif EPG_INTERVAL == '3':
    GET_EPG_INTERVAL = 3
elif EPG_INTERVAL == '4':
    GET_EPG_INTERVAL = 4
elif EPG_INTERVAL == '5':
    GET_EPG_INTERVAL = 5
else:
    GET_EPG_INTERVAL = 6

CHANNEL_FILTER = ADDON.getSetting('channel_filter_sort')
if CHANNEL_FILTER == '0':
    GET_CHANNEL_FILTER = "0"
elif CHANNEL_FILTER == '1':
    GET_CHANNEL_FILTER = "1"
else:
    GET_CHANNEL_FILTER = "2"

NUMBER_OF_SERVICE_PRIORITIES = 12
SETTINGS_TO_CHECK = ['source', 'xmltv_file', 'xmltv_logo_folder',
                     'm-TVGuide', 'm-TVGuide2', 'm-TVGuide3',
                     'XXX_EPG', 'VOD_EPG', 'time_zone',
                     'country_code_be', 'epg_be',
                     'country_code_cz', 'epg_cz',
                     'country_code_hr', 'epg_hr',
                     'country_code_dk', 'epg_dk',
                     'country_code_uk', 'epg_uk',
                     'country_code_fr', 'epg_fr',
                     'country_code_de', 'epg_de',
                     'country_code_it', 'epg_it',
                     'country_code_no', 'epg_no',
                     'country_code_srb', 'epg_srb',
                     'country_code_se', 'epg_se',
                     'country_code_us', 'epg_us',
                     'country_code_radio', 'epg_radio']

def unidecodeStr(s):
    if PY3:
        return s
    else:
        return unidecode(s)

class proxydt(datetime):
    @staticmethod
    def strptime(date_string, format):
        import time
        try:
            res = datetime.strptime(date_string, format)
        except:
            res = datetime(*(time.strptime(date_string, format)[0:6]))
        return res

proxydt = proxydt

class Progress(object):
    """Simple class to keep progrees."""

    def __init__(self, total, callback=None):
        self.n = 0
        self.total = total
        self.callback = callback


class Channel(object):
    def __init__(self, id, title, logo = None, titles = None, streamUrl = None, visible = True, weight = -1):
        self.id = id
        self.title = title
        self.logo = logo
        self.titles = titles
        self.streamUrl = streamUrl
        self.visible = visible
        self.weight = weight
        self.channelList = list()
        self.channelListAll = list()

    def isPlayable(self):
        return hasattr(self, 'streamUrl') and self.streamUrl

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return 'Channel(id={}, title={}, logo={}, titles={}, streamUrl={})' \
               .format(self.id, self.title, self.logo, self.titles, self.streamUrl)

class Program(object):
    def __init__(self, channel, title, startDate, endDate, description, productionDate = None, director = None, actor = None, episode = None, rating = None, imageLarge = None, imageSmall = None, categoryA = None, categoryB = None, notificationScheduled = None, recordingScheduled = None, fileName = None):
        """
        @param channel:
        @type channel: source.Channel
        @param title:
        @param startDate:
        @param endDate:
        @param description:
        @param imageLarge:
        @param imageSmall:
        """
        self.channel = channel
        self.title = title
        self.startDate = startDate
        self.endDate = endDate
        self.description = description
        self.productionDate = productionDate
        self.director = director
        self.actor = actor
        self.episode = episode
        self.rating = rating
        self.imageLarge = imageLarge
        self.imageSmall = imageSmall
        self.categoryA = categoryA
        self.categoryB = categoryB
        self.notificationScheduled = notificationScheduled
        self.recordingScheduled = recordingScheduled
        self.fileName = fileName

    def __repr__(self):
        return 'Program(channel={}, title={}, startDate={}, endDate={}, description={}, productionDate={}, director={}, actor={}, episode{}, rating{}, imageLarge={}, imageSmall={}, categoryA={}, categoryB={})' \
            .format(self.channel, self.title, self.startDate, self.endDate, self.description, self.productionDate, self.director, self.actor, self.episode, self.rating, self.imageLarge, self.imageSmall, self.categoryA, self.categoryB)


class ProgramDescriptionParser(object):
    DECORATE_REGEX = re.compile(r'\[COLOR\s*\w*\]|\[/COLOR\]|\[B\]|\[/B\]|\[I\]|\[/I\]',      re.IGNORECASE)
    CATEGORY_REGEX = re.compile(r'((G:|Kategoria:|Genre:|Genere:|Category:|Kategori:|Cat.?gorie:|Kategorie:|Kategorija:|Sjanger:)(.*?\[\/B\]|.*?[^\.]*)(\.)?)',        re.IGNORECASE)

    def __init__(self, description):
        self.description = description

    def extractCategory(self):
        try:
            category = ProgramDescriptionParser.CATEGORY_REGEX.search(self.description).group(1)
            category = ProgramDescriptionParser.DECORATE_REGEX.sub("", category)
            category = re.sub('G:|Kategoria:|Genre:|Category:|Kategori:|Cat.?gorie:|Kategorie:|Kategorija:|Sjanger:|Genere:', '', category).strip()

            self.description = ProgramDescriptionParser.CATEGORY_REGEX.sub("", self.description).strip()
        except:
            category = ''

        return category

    def extractProductionDate(self):
        try:
            productionDate = re.search(r'((R:|Rok produkcji:|Producerat .?r:|Production date:|Produktions dato:|Date de production:|Produktionsdatum:|Godina proizvodnje:|Datum proizvodnje:|Produksjonsdato:|Productie datum:|Datum v.?roby:|Anno prodotto:)\s*(\[B\])?(\d{2,4}|live)(\[\/B\])?(\.)?)', self.description).group(4)
            productionDate = ProgramDescriptionParser.DECORATE_REGEX.sub("", productionDate)
            productionDate = re.sub('R:|Rok produkcji:|Producerat .?r:|Production date:|Produktions dato:|Date de production:|Produktionsdatum:|Godina proizvodnje:|Datum proizvodnje:|Produksjonsdato:|Productie datum:|Datum v.?roby:|Anno prodotto:', '', productionDate).strip()

            self.description = re.sub(r'((R:|Rok produkcji:|Producerat .?r:|Production date:|Produktions dato:|Date de production:|Produktionsdatum:|Godina proizvodnje:|Datum proizvodnje:|Produksjonsdato:|Productie datum:|Datum v.?roby:|Anno prodotto:)\s*(\[B\])?(\d{2,4}|live)(\[\/B\])?(\.)?)', '', self.description).strip()
        except:
            productionDate = ''

        return productionDate

    def extractDirector(self):
        try:
            director = re.search(r'.*((Re.?yser:|Regiss.?r:|Director:|Instrukt.?r:|R.?alisateur:|Regisseur:|Direktor:|Re.?is.?r:|Direttore:)(.*?\[\/B\]|.*?[^\.]*)).*', self.description).group(1)
            director = ProgramDescriptionParser.DECORATE_REGEX.sub("", director)
            director = re.sub(r'Re.?yser:|Regiss.?r:|Director:|Instrukt.?r:|R.?alisateur:|Regisseur:|Direktor:|Re.?is.?r:|Direttore:', '', director).strip()

            self.description = re.sub(r'(Re.?yser:|Regiss.?r:|Director:|Instrukt.?r:|R.?alisateur:|Regisseur:|Direktor:|Re.?is.?r:|Direttore:)(.*?\[\/B\]|.*?[^\.]*)(\.)?', '', self.description).strip()
        except:
            director = ''

        return director

    def extractEpisode(self):
        try:
            episode = re.search(r'.*((Odcinek:|Avsnitt:|Episode:|Episode:|.?pisode:|Folge:|Odjeljak:|Epizoda:|Aflevering:|Sezione:)\s*(\[B\])?(.*?\/B\]|.*?[^\.]*)(\.)?).*', self.description).group(1)
            episode = ProgramDescriptionParser.DECORATE_REGEX.sub("", episode)
            episode = re.sub('Odcinek:|Avsnitt:|Episode:|.?pisode:|Folge:|Odjeljak:|Epizoda:|Aflevering:|Sezione:', '', episode).strip()

            self.description = re.sub(r'(Odcinek:|Avsnitt:|Episode:|.?pisode:|Folge:|Odjeljak:|Epizoda:|Aflevering:|Sezione:)\s*(\[B\])?(.*?\/B\]|.*?[^\.]*)(\.)?', '', self.description).strip()

            p = re.compile(r'([*S|E]((S)?(\d{1,3})?\s*((E)?\d{1,5}(\/\d{1,5})?)))')
            episode = p.search(self.description).group(1)

        except:
            episode = ''

        return episode

    def extractAllowedAge(self):
        if PY3:
            addonPath = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))
        else:
            addonPath = xbmc.translatePath(ADDON.getAddonInfo('path'))
        try:
            icon = ''
            age = ''
            try:
                age = re.search(r'(W:|Od lat:|.?r:|Rating:|Pendant des ann.?es:|.?ber die Jahre:|Godinama:|Jaar:|Rok:|Anni:).*?(\[B\])?(\d+)(\[\/B\])?(\.)?', self.description).group(3)
                if age == '3':
                    age = '0'
                icon = os.path.join(addonPath, 'icons', 'age_rating', 'icon_{}.png'.format(age))

            except:
                age = re.search(r'(W:|Od lat:|.?r:|Rating:|Pendant des ann.?es:|.?ber die Jahre:|Godinama:|Jaar:|Rok:|Anni:).*?(\[B\])?(\w+)(\[\/B\])?(\.)?', self.description).group(3)

            age = ProgramDescriptionParser.DECORATE_REGEX.sub("", age)

            self.description = re.sub(r'(W:|Od lat:|.?r:|Rating:|Pendant des ann.?es:|.?ber die Jahre:|Godinama:|Jaar:|Rok:|Anni:).*?(\[B\])?({Age}|.*)\s*(\+)?(\[\/B\])?(\.)?'.format(Age=age), '', self.description).strip()
        except:
            icon = ''
            age = ''

        return icon, age

    def extractRating(self):
        try:
            rating = re.search(r'((O:|Ocena:|Betyg:|Starrating:|Bewertung:|Bed.?mmelse:|Bewertung:|Ocjena:|Notation:|Valutazione:|Hodnocen.?:)\s*(\[B\])?(\d+/\d+)(\[\/B\])?(\.)?)', self.description).group(4)
            rating = ProgramDescriptionParser.DECORATE_REGEX.sub("", rating)
            rating = re.sub('O:|Ocena:|Betyg:|Starrating:|Bewertung:|Bed.?mmelse:|Bewertung:|Ocjena:|Notation:|Valutazione:|Hodnocen.?:', '', rating).strip()

            self.description = re.sub(r'((O:|Ocena:|Betyg:|Bewertung:|Bed.?mmelse:|Ocjena:|Bewertung:|Ocjena:|Notation:|Valutazione:|Hodnocen.?:)\s*(\[B\])?(\d+/\d+)(\[\/B\])?(\.)?)', '', self.description).strip()
        except:
            rating = ''

        return rating

    def extractActors(self):
        try:
            actors = re.search(r'.*((Aktorzy:|Sk.?despelare:|Actors:|Skuespillere:|Acteurs:|Schauspiel:|Glumci:|Herec:|Attori:)(.*?\[\/B\]|.*?[^\.]*)).*', self.description).group(1)
            actors = ProgramDescriptionParser.DECORATE_REGEX.sub("", actors)
            actors = re.sub('Aktorzy:|Sk.?despelare:|Actors:|Skuespillere:|Acteurs:|Schauspiel:|Glumci:|Herec:|Attori:', '', actors).strip()

            self.description = re.sub(r'(Aktorzy:|Sk.?despelare:|Actors:|Skuespillere:|Acteurs:|Schauspiel:|Glumci:|Herec:|Attori:)(.*?\[\/B\]|.*?[^\.]*)(\.)?', '', self.description).strip()
        except:
            actors = ''

        return actors

class SourceException(Exception):
    pass

class SourceUpdateCanceledException(SourceException):
    pass

class SourceNotConfiguredException(SourceException):
    pass

class RestartRequired(SourceException):
    pass

class SourceFaultyEPGException(SourceException):
    def __init__(self, epg):
        self.epg = epg

class DatabaseSchemaException(sqlite3.DatabaseError):
    pass

class Database(object):
    SOURCE_DB = 'source.db'
    if PY3:
        config = configparser.RawConfigParser()
    else:
        config = ConfigParser.RawConfigParser()
    try:
        config.read(os.path.join(Skin.getSkinPath(), 'settings.ini'))
        ini_chan = config.getint("Skin", "CHANNELS_PER_PAGE")
        CHANNELS_PER_PAGE = ini_chan
    except:
        CHANNELS_PER_PAGE = 10

    def __init__(self):
        self.conn = None
        self.eventQueue = []
        self.event = threading.Event()

        self.eventResults = dict()
        self.source = instantiateSource()
        self.updateInProgress = False
        self.updateFailed = False
        self.skipUpdateRetries = False
        self.settingsChanged = None
        self.channelList = list()
        self.channelListAll = list()
        self.servicePlaylist = dict()
        self.cacheList = dict()
        self.category = None

        if PY3:
            try:
                self.profilePath  = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
            except:
                self.profilePath  = xbmcvfs.translatePath(ADDON.getAddonInfo('profile')).decode('utf-8')
        else:
            try:
                self.profilePath  = xbmc.translatePath(ADDON.getAddonInfo('profile'))
            except:
                self.profilePath  = xbmc.translatePath(ADDON.getAddonInfo('profile')).decode('utf-8')

        if not os.path.exists(self.profilePath):
            os.makedirs(self.profilePath)
        self.databasePath = os.path.join(self.profilePath, Database.SOURCE_DB)
        self.ChannelsWithStream = ADDON.getSetting('OnlyChannelsWithStream')
        self.epgBasedOnLastModDate = ADDON.getSetting('UpdateEPGOnModifiedDate')
        self.lock = threading.Lock()
        self.services_updated = False
        self.number_of_service_priorites = NUMBER_OF_SERVICE_PRIORITIES
        self.close_callback = None
        self.unlockDbTimer = None

        threading.Thread(name='Database Event Loop', target = self.eventLoop).start()

    def eventLoop(self):
        deb('Database.eventLoop() >>>>>>>>>> starting...')
        while True:
            self.event.wait()
            self.event.clear()
            event = self.eventQueue.pop(0)
            command = event[0]
            callback = event[1]

            deb('Database.eventLoop() >>>>>>>>>> processing command: {}'.format(command.__name__ ))
            try:
                result = command(*event[2:])
                self.eventResults[command.__name__] = result
                if callback:
                    if self._initialize == command:
                        self.close_callback = callback
                        threading.Thread(name='Database callback', target=callback, args=[result]).start()
                    else:
                        threading.Thread(name='Database callback', target=callback).start()
                if self._close == command:
                    del self.eventQueue[:]
                    break

            except Exception as ex:
                deb('Database.eventLoop() >>>>>>>>>> exception: {}!'.format(getExceptionString() ))
                if self.close_callback:
                    self.close_callback(False)

        deb('Database.eventLoop() >>>>>>>>>> exiting...')

    def _invokeAndBlockForResult(self, method, *args):
        self.lock.acquire()
        event = [method, None]
        event.extend(args)
        self.eventQueue.append(event)
        self.event.set()
        while method.__name__ not in self.eventResults:
            time.sleep(0.03)
        result = self.eventResults.get(method.__name__)
        del self.eventResults[method.__name__]
        self.lock.release()
        return result

    def initialize(self, callback, cancel_requested_callback=None):
        self.eventQueue.append([self._initialize, callback, cancel_requested_callback])
        self.event.set()

    def _initialize(self, cancel_requested_callback):
        deb('_initialize')
        sqlite3.register_adapter(datetime, self.adapt_datetime)
        sqlite3.register_converter(str('timestamp'), self.convert_datetime)

        self.alreadyTriedUnlinking = False
        while True:
            if cancel_requested_callback is not None and cancel_requested_callback():
                break

            try:
                self.unlockDbTimer = threading.Timer(120, self.delayedUnlockDb)
                self.unlockDbTimer.start()
                time.sleep(uniform(0, 0.2))
                self.conn = sqlite3.connect(self.databasePath, detect_types=sqlite3.PARSE_DECLTYPES, cached_statements=2000)
                self.conn.execute("PRAGMA foreign_keys = ON");
                self.conn.execute("PRAGMA locking_mode = EXCLUSIVE");
                self.conn.execute("PRAGMA encoding = 'UTF-8'");
                self.conn.execute("PRAGMA temp_store = 2");
                self.conn.execute("PRAGMA cache_size = -32000");
                if GET_PRAGMA_MODE:
                    self.conn.execute("PRAGMA journal_mode = WAL");
                    self.conn.execute("PRAGMA temp_store = MEMORY");
                    self.conn.execute("PRAGMA synchronous = NORMAL");
                self.conn.row_factory = sqlite3.Row

                # create and drop dummy table to check if database is locked
                c = self.conn.cursor()
                c.execute('CREATE TABLE IF NOT EXISTS database_lock_check(id TEXT PRIMARY KEY)')
                c.execute('DROP TABLE database_lock_check')

                c.execute('pragma integrity_check')
                for row in c:
                    deb('Database is {}'.format(row[str('integrity_check')]))

                c.close()

                self._createTables()
                self.settingsChanged = self._wasSettingsChanged(ADDON)
                break

            except RestartRequired:
                strings2.M_TVGUIDE_CLOSING = True
                xbmcgui.Dialog().ok(strings(30978), strings(30979))
                return False

            except sqlite3.OperationalError:
                #if cancel_requested_callback is None or strings2.M_TVGUIDE_CLOSING:
                deb('[{}] Database is locked, bailing out...'.format(ADDON_ID))
                    #break
                #else: # ignore 'database is locked'
                    #deb('[{}] Database is locked, retrying...'.format(ADDON_ID))
                xbmcgui.Dialog().notification(strings(57051), strings(57052), time=8000, sound=True)
                return False

            except sqlite3.DatabaseError:
                self.conn = None
                if self.alreadyTriedUnlinking:
                    deb('[{}] Database is broken and unlink() failed'.format(ADDON_ID))
                    break
                else:
                    try:
                        os.unlink(self.databasePath)
                    except OSError:
                        pass
                    self.alreadyTriedUnlinking = True
                    xbmcgui.Dialog().ok(ADDON.getAddonInfo('name'), strings(DATABASE_SCHEMA_ERROR_1) + '\n' + strings(DATABASE_SCHEMA_ERROR_2) + ' ' + strings(DATABASE_SCHEMA_ERROR_3))

        return self.conn is not None

    def delayedUnlockDb(self):
        try:
            self.eventQueue.append([self.unlockDb, None])
            self.event.set()
        except:
            pass

    def unlockDb(self):
        try:
            if self.conn:
                deb('Unlocking DB')
                self.conn.execute("PRAGMA locking_mode = NORMAL");

                c = self.conn.cursor()
                c.execute('CREATE TABLE IF NOT EXISTS database_lock_check(id TEXT PRIMARY KEY)')
                c.execute('DROP TABLE database_lock_check')
                self.conn.commit()
                c.close()
        except:
            pass

    def close(self, callback=None):
        self.close_callback = None
        if self.unlockDbTimer and self.unlockDbTimer.is_alive():
            self.unlockDbTimer.cancel()
        self.source.close()
        self.eventQueue.append([self._close, callback])
        self.event.set()

    def _close(self):
        try:
            # rollback any non-commit'ed changes to avoid database lock
            if self.conn:
                self.conn.execute("PRAGMA analysis_limit = 400");
                self.conn.execute("PRAGMA optimize");
                self.conn.rollback()
        except sqlite3.OperationalError:
            pass # no transaction is active
        if self.conn:
            self.conn.close()

    def _wasSettingsChanged(self, addon):
        settingsChanged = False
        noRows = True
        count = 0
        c = self.conn.cursor()
        c.execute('SELECT * FROM settings')
        for row in c:
            noRows = False
            key = row[str('key')]
            if SETTINGS_TO_CHECK.count(key):
                count += 1
                setting = addon.getSetting(key)
                if row[str('value')] != setting:
                    deb('Settings changed for key: {}, value id DB: {}, in settings.xml: {}'.format(key, row[str('value')], setting) )
                    settingsChanged = True
        if count != len(SETTINGS_TO_CHECK):
            deb('Settings changed - number of keys is different')
            settingsChanged = True
        if settingsChanged or noRows:
            for key in SETTINGS_TO_CHECK:
                value = addon.getSetting(key)
                c.execute('INSERT OR IGNORE INTO settings(key, value) VALUES (?, ?)', [key, value])
                if not c.rowcount:
                    c.execute('UPDATE settings SET value=? WHERE key=?', [value, key])

            try:
                c.execute('UPDATE UPDATES SET epg_size=? WHERE source=?', [0, self.source.KEY])
            except:
                pass

            self.conn.commit()
        c.close()
        deb('Settings changed: {}'.format(str(settingsChanged) ))
        return settingsChanged

    def _isCacheExpired(self, date, initializing, startup, force):
        try:
            if force:
                return True

            if startup:
                return False

            if GET_EPG_INTERVAL == 1 and initializing:
                return True

            if self.settingsChanged:
                return True

            # check if channel data is up-to-date in database
            try:
                c = self.conn.cursor()
                c.execute('SELECT channels_updated FROM sources WHERE id=?', [self.source.KEY])
                row = c.fetchone()
                if not row:
                    return True
                channelsLastUpdated = row[str('channels_updated')]
                c.close()
            except TypeError:
                return True

            # check if program data is up-to-date in database
            c = self.conn.cursor()

            if self.epgBasedOnLastModDate == 'false':
                dateStr = date.strftime('%Y-%m-%d')
                c.execute('SELECT programs_updated FROM updates WHERE source=? AND date=?', [self.source.KEY, dateStr])
            else:
                c.execute('SELECT programs_updated FROM updates WHERE source=?', [self.source.KEY])

            row = c.fetchone()
            if row:
                programsLastUpdated = row[str('programs_updated')]
            else:
                programsLastUpdated = None

            c.execute('SELECT epg_size FROM updates WHERE source=?', [self.source.KEY])
            row = c.fetchone()
            epgSize = 0
            if row:
                epgSize = row[str('epg_size')]
                ADDON.setSetting('epg_size', str(epgSize))
            c.close()

            set_time = 'auto'

            if programsLastUpdated is not None:
                interval = GET_EPG_INTERVAL

                if interval == 0:
                    set_time = 'auto'
                elif interval == 1:
                    set_time = 0
                elif interval == 2:
                    set_time = 43200
                elif interval == 3:
                    set_time = 86400
                elif interval == 4:
                    set_time = 172800
                elif interval == 5:
                    set_time = 604800
                elif interval == 6:
                    set_time = 1209600

                if set_time != 'auto':
                    try:
                        epg_interval = datetime.timestamp(datetime.now()) - set_time
                    except:
                        epg_interval = time.mktime(datetime.now().timetuple()) - set_time

                    try:
                        last_update = datetime.timestamp(programsLastUpdated)
                    except:
                        last_update = time.mktime(programsLastUpdated.timetuple())

                    if int(epg_interval) > int(last_update):
                        self.source.isUpdated(channelsLastUpdated, programsLastUpdated, epgSize)
                    else:
                        return False

            return self.source.isUpdated(channelsLastUpdated, programsLastUpdated, epgSize)
        except:
            self.updateFailed = True
            return

    def cachePlaylist(self, serviceHandler):
        playlist_cache = os.path.join(PROFILE_PATH, 'playlist_cache.list')
        serviceName = serviceHandler.serviceName

        n = datetime.now()
        d = timedelta(days=int(ADDON.getSetting('{playlist}_refr_days'.format(playlist=serviceName))))

        if PY3:
            tnow = datetime.timestamp(n)
        else:
            from time import time
            tnow = str(time()).split('.')[0]

        tdel = d.total_seconds()

        path = os.path.join(PROFILE_PATH, 'playlists')
        filepath = os.path.join(PROFILE_PATH, 'playlists', '{playlist}.m3u'.format(playlist=serviceName))

        try:
            filename = os.path.basename(filepath)
            timestamp = str(os.path.getmtime(filepath)).split('.')[0]
        except:
            timestamp = tnow

        if not os.path.exists(path):
            os.makedirs(path)

        url_setting = ADDON.getSetting('{playlist}_url'.format(playlist=serviceName))

        urlpath = os.path.join(PROFILE_PATH, 'playlists', '{playlist}.url'.format(playlist=serviceName))
        if os.path.exists(urlpath):
            if PY3:
                with open(urlpath, 'r', encoding='utf-8') as f:
                    url = [line.strip() for line in f][0]
            else:
                with codecs.open(urlpath, 'r', encoding='utf-8') as f:
                    url = [line.strip() for line in f][0]

        else:
            url = url_setting

        cachedate = int(timestamp) + int(tdel)

        if int(tnow) >= int(cachedate) or (not os.path.exists(filepath) or os.stat(filepath).st_size <= 0 or url != url_setting):
            deb('[UPD] Cache playlist: Write, expiration date: {}'.format(datetime.fromtimestamp(int(cachedate))))
            cache = False

        else:
            refr = ADDON.getSetting('{playlist}_refr'.format(playlist=serviceName))
            src = ADDON.getSetting('{playlist}_source'.format(playlist=serviceName))

            if refr == 'true' and src == '0':
                deb('[UPD] Cache playlist: Read')
                cache = True
            else:
                cache = False

        if not cache:
            if PY3:
                if os.path.exists(playlist_cache):
                    with open(playlist_cache, 'r', encoding='utf-8') as r:
                        services = r.read().splitlines()

                    with open(playlist_cache, 'w', encoding='utf-8') as f:
                        for service in services:
                            if service != serviceName:
                                f.write(service+'\n')
            else:
                if os.path.exists(playlist_cache):
                    with codecs.open(playlist_cache, 'r', encoding='utf-8') as r:
                        services = r.read().splitlines()

                    with codecs.open(playlist_cache, 'w', encoding='utf-8') as f:
                        for service in services:
                            if service != serviceName:
                                f.write(service+'\n')
        else:
            if (os.path.exists(filepath) or os.stat(filepath).st_size > 0 or url == url_setting):
                if PY3:
                    try:
                        with open(playlist_cache, 'r', encoding='utf-8') as r:
                            services = r.read().splitlines()
                    except:
                        services = []

                    with open(playlist_cache, 'a', encoding='utf-8') as f:
                        if serviceName not in services:
                            f.write(serviceName+'\n')

                else:
                    try:
                        with codecs.open(playlist_cache, 'r', encoding='utf-8') as r:
                            services = r.read().splitlines()
                    except:
                        services = []

                    with codecs.open(playlist_cache, 'a', encoding='utf-8') as f:
                        if serviceName not in services:
                            f.write(serviceName+'\n')

        return cache

    def updateChannelAndProgramListCaches(self, callback, date = datetime.now(), progress_callback = None, initializing=False, startup=False, force=False, clearExistingProgramList = True):
        self.eventQueue.append([self._updateChannelAndProgramListCaches, callback, date, progress_callback, initializing, startup, force, clearExistingProgramList])
        self.event.set()

    def _updateChannelAndProgramListCaches(self, date, progress_callback, initializing, startup, force, clearExistingProgramList):
        deb('_updateChannelAndProgramListCache')
        import sys

        # todo workaround service.py 'forgets' the adapter and convert set in _initialize.. wtf?!
        sqlite3.register_adapter(datetime, self.adapt_datetime)
        sqlite3.register_converter(str('timestamp'), self.convert_datetime)

        # Start service threads
        updateServices = self.services_updated == False and UPDATE_CID
        if updateServices:
            deb('[UPD] Starting updating STRM')

            playlist_cache = os.path.join(PROFILE_PATH, 'playlist_cache.list')

            serviceList = list()
            services = list()

            for serviceName in playService.LIST:
                serviceHandler = playService.LIST[serviceName]
                services.append(serviceHandler)
                cache = False

                if serviceHandler.serviceEnabled == 'true':
                    serviceList.append(serviceHandler)
                    if 'playlist_' in serviceName:
                        cache = self.cachePlaylist(serviceHandler)
                        if GET_DATABASE_CLEARED:
                            cache = False
                        self.cacheList.update({serviceHandler: {'cache': cache}})

                if (not cache and not 'playlist_' in serviceName) or serviceHandler.serviceEnabled == 'false':
                    self.removePredefinedCategoriesDb(serviceName)

            if not self.cacheList:
                self.deleteAllCustomStreams()
                if os.path.exists(playlist_cache):
                    os.remove(playlist_cache)

                for num in range(1, 6):
                    filepath = os.path.join(PROFILE_PATH, 'playlists', 'playlist_{playlist}.m3u'.format(playlist=num))
                    urlpath = os.path.join(PROFILE_PATH, 'playlists', 'playlist_{playlist}.url'.format(playlist=num))
                    cachepath = os.path.join(PROFILE_PATH, 'playlists', 'playlist_{playlist}.cache'.format(playlist=num))

                    if os.path.exists(filepath):
                        os.remove(filepath)
                    if os.path.exists(urlpath):
                        os.remove(urlpath)
                    if os.path.exists(cachepath):
                        os.remove(cachepath)
            else:
                for s in services:
                    if s not in serviceList:
                        self.deleteCustomStreams(s.serviceName, s.serviceRegex)
                        if 'playlist_' in s.serviceName:
                            filepath = os.path.join(PROFILE_PATH, 'playlists', '{playlist}.m3u'.format(playlist=s.serviceName))
                            urlpath = os.path.join(PROFILE_PATH, 'playlists', '{playlist}.url'.format(playlist=s.serviceName))
                            cachepath = os.path.join(PROFILE_PATH, 'playlists', '{playlist}.cache'.format(playlist=s.serviceName))

                            if os.path.exists(filepath):
                                os.remove(filepath)
                            if os.path.exists(urlpath):
                                os.remove(urlpath)
                            if os.path.exists(cachepath):
                                os.remove(cachepath)

                            if PY3:
                                if os.path.exists(playlist_cache):
                                    with open(playlist_cache, 'r', encoding='utf-8') as r:
                                        r_services = r.read().splitlines()

                                    with open(playlist_cache, 'w', encoding='utf-8') as f:
                                        for service in r_services:
                                            if service != s.serviceName:
                                                f.write(service+'\n')
                            else:
                                if os.path.exists(playlist_cache):
                                    with codecs.open(playlist_cache, 'r', encoding='utf-8') as r:
                                        r_services = r.read().splitlines()

                                    with codecs.open(playlist_cache, 'w', encoding='utf-8') as f:
                                        for service in r_services:
                                            if service != s.serviceName:
                                                f.write(service+'\n')

        cacheExpired = self._isCacheExpired(date, initializing, startup, force)
        ADDON.setSetting('database_cleared', 'false')

        if cacheExpired and not self.skipUpdateRetries:
            deb('_isCacheExpired')
            self.updateInProgress = True
            self.updateFailed = False
            dateStr = date.strftime('%Y-%m-%d')
            self._removeOldRecordings()
            self._removeOldNotifications()
            c = self.conn.cursor()
            dbChannelsUpdated = False

            try:
                deb('[{}] Updating caches...'.format(ADDON_ID))

                profilePath = self.profilePath

                if progress_callback:
                    progress_callback(0)

                imported = 0
                nrOfFailures = 0

                startTime = datetime.now()
                for item in self.source.getDataFromExternal(date, progress_callback):
                    imported += 1

                    xbmcvfs.delete(os.path.join(profilePath, 'custom_channels.list'))

                    channelList = []

                    if not xbmcvfs.exists(os.path.join(profilePath, 'basemap_extra.xml')):
                        try:
                            shutil.copyfile(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'basemap_extra.xml'), os.path.join(profilePath, 'basemap_extra.xml'))
                        except:
                            pass

                    p = re.compile(r'\s<channel id="(.*?)"', re.DOTALL)
                    with open(os.path.join(profilePath, 'basemap_extra.xml'), 'rb') as f:
                        if PY3:
                            base = str(f.read(), 'utf-8')
                        else:
                            base = f.read().decode('utf-8')

                        channList = p.findall(base)
                        intList = range(len(channList))

                        for chann in intList:
                            ch = Channel(channList[chann], channList[chann])
                            channelList.append(ch)

                    # Clear program list only when there is at lease one valid row available
                    if not dbChannelsUpdated:
                        dbChannelsUpdated = True
                        if self.settingsChanged:
                            c.execute('DELETE FROM channels WHERE source=?', [self.source.KEY])
                            c.execute('DELETE FROM programs WHERE source=?', [self.source.KEY])
                            c.execute('DELETE FROM updates WHERE source=?', [self.source.KEY])
                            for channel in channelList:
                                c.execute('INSERT OR IGNORE INTO channels(id, title, logo, titles, stream_url, visible, weight, source) VALUES(?, ?, ?, ?, ?, ?, (CASE ? WHEN -1 THEN (SELECT COALESCE(MAX(weight)+1, 0) FROM channels WHERE source=?) ELSE ? END), ?)', [channel.id, channel.title, channel.logo, channel.titles, channel.streamUrl, channel.visible, channel.weight, self.source.KEY, channel.weight, self.source.KEY])
                                if not c.rowcount:
                                    c.execute('UPDATE channels SET title=?, logo=?, titles=?, stream_url=?, visible=?, weight=(CASE ? WHEN -1 THEN weight ELSE ? END) WHERE id=? AND source=?', [channel.title, channel.logo, channel.titles, channel.streamUrl, channel.visible, channel.weight, channel.weight, channel.id, self.source.KEY])

                        self.settingsChanged = False # only want to update once due to changed settings

                        if clearExistingProgramList:
                            c.execute("DELETE FROM updates WHERE source=?", [self.source.KEY]) # cascades and deletes associated programs records
                        else:
                            c.execute("DELETE FROM updates WHERE source=? AND date=?", [self.source.KEY, dateStr]) # cascades and deletes associated programs records

                        # programs updated
                        c.execute("UPDATE sources SET channels_updated=? WHERE id=?", [0, self.source.KEY])
                        c.execute("INSERT INTO updates(source, date, programs_updated, epg_size) VALUES(?, ?, ?, ?)", [self.source.KEY, dateStr, 0, 0])

                        self.conn.commit()
                        updatesId = c.lastrowid

                    if imported % 10000 == 0:
                        try:
                            self.conn.commit()
                        except:
                            xbmcgui.Dialog().ok(strings(LOAD_ERROR_TITLE), strings(EPG_FORMAT_ERROR))
                            strings2.M_TVGUIDE_CLOSING = True
                            return False

                    if isinstance(item, Channel):
                        c.execute('INSERT OR IGNORE INTO channels(id, title, logo, titles, stream_url, visible, weight, source) VALUES(?, ?, ?, ?, ?, ?, (CASE ? WHEN -1 THEN (SELECT COALESCE(MAX(weight)+1, 0) FROM channels WHERE source=?) ELSE ? END), ?)', [item.id, item.title, item.logo, item.titles, item.streamUrl, item.visible, item.weight, self.source.KEY, item.weight, self.source.KEY])
                        if not c.rowcount:
                            c.execute('UPDATE channels SET title=?, logo=?, titles=?, stream_url=?, visible=(CASE ? WHEN -1 THEN visible ELSE ? END), weight=(CASE ? WHEN -1 THEN weight ELSE ? END) WHERE id=? AND source=?',
                                [item.title, item.logo, item.titles, item.streamUrl, item.weight, item.visible, item.weight, item.weight, item.id, self.source.KEY])

                    elif isinstance(item, Program):
                        try:
                            c.execute('INSERT OR REPLACE INTO programs(channel, title, start_date, end_date, description, productionDate, director, actor, episode, rating, image_large, image_small, categoryA, categoryB, source, updates_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                [item.channel, item.title, item.startDate, item.endDate, item.description, item.productionDate, item.director, item.actor, item.episode, item.rating, item.imageLarge, item.imageSmall, item.categoryA, item.categoryB, self.source.KEY, updatesId])

                        except (sqlite3.InterfaceError) as ex:
                            nrOfFailures += 1
                            imported -= 1
                            if nrOfFailures <= 10:
                                deb('_updateChannelAndProgramListCache ERROR while inserting program to DB for {} time, faulty row will follow, exception: {}'.format(nrOfFailures, getExceptionString()))
                                try:
                                    if PY3:
                                        deb('Row: {}'.format(str(item)))
                                    else:
                                        deb('Row: {}'.format(unicode(item)))
                                except:
                                    deb('Unable to print row...')

                        except (sqlite3.OperationalError) as ex:
                            xbmcgui.Dialog().ok(ADDON.getAddonInfo('name'), strings(DATABASE_SCHEMA_ERROR_1) + '\n' + strings(DATABASE_SCHEMA_ERROR_2) + ' ' + strings(DATABASE_SCHEMA_ERROR_3))
                            c.close()

                # channels updated
                if imported > 0:
                    c.execute("UPDATE sources SET channels_updated=? WHERE id=?", [self.source.getNewUpdateTime(), self.source.KEY])
                    c.execute("UPDATE updates SET date=?, programs_updated=?, epg_size=? WHERE source=?", [dateStr, self.source.getNewUpdateTime(), self.source.getEpgSize(), self.source.KEY])
                self.conn.commit()
                deb('_updateChannelAndProgramListCaches parsing EPG and database update took {} seconds, nr of imports: {}, failures: {}'.format((datetime.now() - startTime).seconds, imported, nrOfFailures))
                self.channelList = None
                if imported == 0:
                    self.updateFailed = True

            except SourceUpdateCanceledException:
                # force source update on next load
                deb('_updateChannelAndProgramListCaches SourceUpdateCanceledException!')
                c.execute('UPDATE sources SET channels_updated=? WHERE id=?', [0, self.source.KEY])
                c.execute("DELETE FROM updates WHERE source=?", [self.source.KEY]) # cascades and deletes associated programs records
                self.conn.commit()
                self.updateFailed = True

            except SourceFaultyEPGException:
                deb('SourceFaultyEPGException unable to load main EPG, trying to continue despite of that')
                self.skipUpdateRetries = True
                if GET_SOURCE == '0':
                    xbmcgui.Dialog().ok(strings(LOAD_ERROR_TITLE), strings(LOAD_ERROR_LINE1) + '\n' + ADDON.getSetting('xmltv_file').strip() + '\n' + strings(LOAD_ERROR_LINE2))
                else:
                    xbmcgui.Dialog().ok(strings(LOAD_ERROR_TITLE), strings(LOAD_ERROR_LINE1) + '\n' + ADDON.getSetting('m-TVGuide').strip() + '\n' + strings(LOAD_ERROR_LINE2))

            except Exception:
                import traceback as tb
                import sys
                (etype, value, traceback) = sys.exc_info()
                tb.print_exception(etype, value, traceback)
                try:
                    self.conn.rollback()
                except sqlite3.OperationalError:
                    pass # no transaction is active
                try:
                    # invalidate cached data
                    c.execute('UPDATE sources SET channels_updated=? WHERE id=?', [0, self.source.KEY])
                    self.conn.commit()
                except sqlite3.OperationalError:
                    pass # database is locked
                self.updateFailed = True
            finally:
                self.updateInProgress = False
                c.close()

        # END self._isCacheExpired(date):

        # zabezpieczenie: is invoked again by XBMC after a video addon exits after being invoked by XBMC.RunPlugin(..)
        deb('[UPD] AutoUpdateCid={} : services_updated={} : self.updateFailed={}'.format(str(UPDATE_CID), self.services_updated, self.updateFailed))
        # jezeli nie udalo sie pobranie epg lub juz aktualizowalismy CIDy lub w opcjach nie mamy zaznaczonej automatycznej aktualizacji
        if self.updateFailed or not updateServices:
            return cacheExpired #to wychodzimy - nie robimy aktualizacji

        epgChannels = self.epgChannels()

        # Waiting for all services
        deb('[UPD] Waiting for loading STRM')
        for priority in reversed(list(range(self.number_of_service_priorites))):
            for service in serviceList:
                if strings2.M_TVGUIDE_CLOSING:
                    break

                if priority == service.servicePriority:
                    cached_service = [v['cache'] for k,v in self.cacheList.items() if k == service]
                    if cached_service:
                        cache = cached_service[0]
                    else:
                        cache = False

                    service.startLoadingChannelList(automap=epgChannels, cache=cache)

                    if progress_callback:
                        if not cache:
                            progress_callback(100, "{}: {}".format(strings(59915), service.getDisplayName()) )
                        else:
                            progress_callback(100, "{}: {}".format(strings(59915), strings(69072)) )
                            time.sleep(0.5)

                    if not cache:
                        service.waitUntilDone()
                        self.storeCustomStreams(service, priority, service.serviceName, service.serviceRegex)

        serviceList = []
        self.printStreamsWithoutChannelEPG()

        self.services_updated = True
        self.channelList = None
        deb('[UPD] Update finished')
        return cacheExpired

    def deleteAllCustomStreams(self):
        try:
            c = self.conn.cursor()
            deb('[UPD] Clearing all custom streams')
            c.execute('DELETE FROM custom_stream_url WHERE stream_url like "service=%"')
            self.conn.commit()
            c.close()
            self.channelList = None

        except Exception as ex:
            deb('[UPD] Error deleteAllCustomStreams exception: {}'.format(getExceptionString()))

    def deleteCustomStreams(self, streamSource, serviceStreamRegex):
        try:
            c = self.conn.cursor()
            deb('[UPD] Clearing list of {} stream urls like {}'.format(streamSource, serviceStreamRegex))
            c.execute("DELETE FROM custom_stream_url WHERE stream_url like ?", [serviceStreamRegex])
            self.conn.commit()
            c.close()
            self.channelList = None

        except Exception as ex:
            deb('[UPD] Error deleting streams: {}'.format(getExceptionString()))


    def epgChannels(self):
        result = dict()

        with self.conn as conn:
            cur = conn.execute('SELECT id, titles FROM channels')

            for x in cur:
                if CH_DISP_NAME:
                    try:
                        result.update({x[0].upper(): x[1].upper()})
                    except:
                        result.update({x[0].upper(): ''})
                else:
                    result.update({x[0].upper(): ''})

        return result.items()

    def storeCustomStreams(self, streams, priority, streamSource, serviceStreamRegex):
        try:
            self.deleteCustomStreams(streamSource, serviceStreamRegex)
            #deb('-------------------------------------------------------------------------------------')
            #deb('[UPD] Updating database')
            #deb('-------------------------------------------------------------------------------------')
            #deb('[UPD]     %-40s %-40s %-35s' % ('-TITLE-', '-ORIG NAME-', '-SERVICE-'))
            categories = []

            nrOfChannelsUpdated = 0
            c = self.conn.cursor()

            for x in streams.automap:
                if x.strm is not None and x.strm != '':
                    #deb('[UPD]     %-40s %-40s %-35s ' % (x.channelid, x.channelid, x.strm))
                    try:
                        channelid = None
                        backup = False

                        for predefined in PREDEFINED_CATEGORIES:
                            channel_regex = re.compile(r'.*({})$'.format(predefined))
                            if PY3:
                                cat = channel_regex.fullmatch(x.channelid)
                            else:
                                cat = channel_regex.match(x.channelid)

                            if cat:
                                if predefined not in categories:
                                    categories.append(predefined)

                        backup_regex = re.compile(r'\w+\d+')
                        if PY3:
                            channel_match = backup_regex.fullmatch(x.channelid)
                        else:
                            channel_match = backup_regex.match(x.channelid)

                        if channel_match and CH_DISP_NAME:
                            channelid = re.sub(r"([0-9]+(\.[0-9]+)?)",r" \1", x.channelid).strip()
                            backup = True

                            if PY3:
                                c.execute("INSERT OR REPLACE INTO custom_stream_url(channel, stream_url, priority) VALUES(?, ?, ?)", [channelid, x.strm + '_BACKUP', priority])
                            else:
                                c.execute("INSERT OR REPLACE INTO custom_stream_url(channel, stream_url, priority) VALUES(?, ?, ?)", [channelid.encode('utf-8').decode('utf-8'), x.strm + '_BACKUP', priority])

                        if PY3:
                            c.execute("INSERT OR IGNORE INTO custom_stream_url(channel, stream_url, priority) VALUES(?, ?, ?)", [x.channelid, x.strm, priority])
                        else:
                            c.execute("INSERT OR REPLACE INTO custom_stream_url(channel, stream_url, priority) VALUES(?, ?, ?)", [x.channelid.encode('utf-8').decode('utf-8'), x.strm, priority])

                        if backup:
                            nrOfChannelsUpdated += 2
                        else:
                            nrOfChannelsUpdated += 1

                    except Exception as ex:
                        deb('[UPD] Error updating stream: {}'.format(getExceptionString()))

            # Categories
            for cat in categories:
                c.execute("INSERT OR REPLACE INTO categories(category, source) VALUES(?, ?)", [cat, streamSource])

            self.conn.commit()
            c.close()

        except Exception as ex:
            deb('[UPD] Error updating streams: {}'.format(getExceptionString()))

            self.conn.commit()
            c.close()

        except Exception as ex:
            deb('[UPD] Error updating streams: {}'.format(getExceptionString()))

    def printStreamsWithoutChannelEPG(self):
        try:
            c = self.conn.cursor()
            c.execute("SELECT custom.channel, custom.stream_url FROM custom_stream_url as custom LEFT JOIN channels as chann ON UPPER(custom.channel) = UPPER(chann.id) WHERE chann.id IS NULL")

            if c.rowcount:
                deb('\n\n')
                deb('List of streams having stream URL assigned but no EPG is available - fix it!')
                deb('-------------------------------------------------------------------------------------')
                deb('[UPD]     %-40s %-35s' % ( '-TITLE-', '-SERVICE-'))
                #cur = self.conn.cursor()
                for row in c:
                    deb('[UPD]     %-40s %-35s' % (unidecodeStr(row[str('channel')]), row[str('stream_url')]))
                    #cur.execute('INSERT OR IGNORE INTO channels(id, title, logo, stream_url, visible, weight, source) VALUES(?, ?, ?, ?, ?, (CASE ? WHEN -1 THEN (SELECT COALESCE(MAX(weight)+1, 0) FROM channels WHERE source=?) ELSE ? END), ?)', [row['channel'], row['channel'], '', '', 1, -1, 'm-TVGuide', -1, 'm-TVGuide'])
                #self.conn.commit()
                deb('End of streams without EPG!')
                deb('-------------------------------------------------------------------------------------------')
                deb('\n\n')
            c.close()

        except Exception as ex:
            deb('printStreamsWithoutChannelEPG Error: {}'.format(getExceptionString()))

    def reloadServices(self):
        if strings2.M_TVGUIDE_CLOSING:
            return
        self._invokeAndBlockForResult(self._reloadServices)

    def _reloadServices(self, cache=False):
        serviceList = list()
        cacheList = list()

        epgChannels = self.epgChannels()

        serviceLib.baseServiceUpdater.baseMapContent = None
        for serviceName in playService.LIST:
            serviceHandler = playService.LIST[serviceName]
            cached_service = [v['cache'] for k,v in self.cacheList.items() if k == serviceHandler]
            if cached_service:
                cache = cached_service[0]
                if cache:
                    cacheList.append(serviceName)

            if serviceHandler.serviceEnabled == 'true':
                serviceHandler.resetService()
                serviceHandler.startLoadingChannelList(automap=epgChannels, cache=cache)
                serviceList.append(serviceHandler)

        deb('[UPD] Starting updating STRM')
        for priority in reversed(list(range(self.number_of_service_priorites))):
            for service in serviceList:
                if priority == service.servicePriority:
                    service.waitUntilDone()
                    if service.serviceName not in cacheList:
                        self.storeCustomStreams(service, priority, service.serviceName, service.serviceRegex)

    def setCategory(self, category):
        try:
            deb('setCategory - setting category to: {}'.format(category))
        except:
            deb('setCategory - setting category to: {}'.format(category.decode('utf-8')))

        if self.category != category:
            self.category = category

        self.channelList = None

    def getEPGView(self, channelStart, date = datetime.now(), progress_callback = None, initializing = False, startup = False, force = False, clearExistingProgramList = True):
        result = self._invokeAndBlockForResult(self._getEPGView, channelStart, date, progress_callback, initializing, startup, force, clearExistingProgramList)
        if self.updateFailed:
            raise SourceException('No channels or programs imported')
        return result

    def _getEPGView(self, channelStart, date, progress_callback, initializing, startup, force, clearExistingProgramList):
        deb('_getEPGView')
        if strings2.M_TVGUIDE_CLOSING:
            self.updateFailed = True
            return

        cacheExpired = self._updateChannelAndProgramListCaches(date, progress_callback, initializing, startup, force, clearExistingProgramList)
        if strings2.M_TVGUIDE_CLOSING:
            self.updateFailed = True
            return

        channels = self._getChannelList(onlyVisible = True)

        try:
            if channelStart < 0:
                modulo = len(channels) % Database.CHANNELS_PER_PAGE
                if modulo > 0:
                    channelStart = len(channels) - modulo
                else:
                    channelStart = len(channels) - Database.CHANNELS_PER_PAGE
            elif channelStart > len(channels) - 1:
                channelStart = 0

            channelEnd = channelStart + Database.CHANNELS_PER_PAGE
            channelsOnPage = channels[channelStart : channelEnd]

            programs = self._getProgramList(channelsOnPage, date)

            return [channelStart, channelsOnPage, programs, cacheExpired]

        except Exception as ex:
            deb('getEPGView Exception: {}'.format(ex))
            self.updateFailed = True
            return

    def getCurrentChannelIdx(self, currentChannel):
        channels = self.getChannelList()
        try:
            idx = channels.index(currentChannel)
        except:
            return 0
        return idx

    def getNumberOfChannels(self):
        channels = self.getChannelList()
        return len(channels)

    def getNextChannel(self, currentChannel):
        channels = self.getChannelList()
        idx = channels.index(currentChannel)
        idx += 1
        if idx > len(channels) - 1:
            idx = 0
        return channels[idx]

    def getPreviousChannel(self, currentChannel):
        channels = self.getChannelList()
        idx = channels.index(currentChannel)
        idx -= 1
        if idx < 0:
            idx = len(channels) - 1
        return channels[idx]

    def lastChannel(self, idx, start, end, played):
        self._invokeAndBlockForResult(self._lastChannel, idx, start, end, played)

    def _lastChannel(self, idx, start, end, played):
        c = self.conn.cursor()
        c.execute("DELETE FROM lastplayed")
        try:
            c.execute("INSERT INTO lastplayed(idx, start_date, end_date, played_date) VALUES(?, ?, ?, ?)", [idx, start, end, played])
        except:
            now = datetime.now()
            if PY3:
                start = datetime.timestamp(now)
            else:
                from time import mktime
                now = datetime.now()
                start = str(int(time.mktime(now.timetuple())))
            c.execute("INSERT INTO lastplayed(idx, start_date, end_date, played_date) VALUES(?, ?, ?, ?)", [idx, start, end, played])
        self.conn.commit()
        c.close()

    def getLastChannel(self):
        return self._invokeAndBlockForResult(self._getLastChannel)

    def _getLastChannel(self):
        from time import mktime
        c = self.conn.cursor()

        now = datetime.now()

        c.execute("SELECT idx, start_date, end_date, played_date FROM lastplayed")
        row = c.fetchone()

        try:
            idx = row[str('idx')]
        except:
            idx = 0

        try:
            start = row[str('start_date')]
        except:
            if PY3:
                start = str(datetime.timestamp(now))
            else:
                start = str(int(time.mktime(now.timetuple())))
        try:
            end = row[str('end_date')]
        except:
            if PY3:
                end = str(datetime.timestamp(now))
            else:
                 end = str(int(time.mktime(now.timetuple())))
        try:
            played = row[str('played_date')]
        except:
            if PY3:
                played = str(datetime.timestamp(now))
            else:
                played = str(int(time.mktime(now.timetuple())))
        c.close()

        return idx, start, end, played

    def getPredefinedCategoriesDb(self):
        result = self._invokeAndBlockForResult(self._getPredefinedCategoriesDb)
        return result

    def _getPredefinedCategoriesDb(self):
        categories = list()

        try:
            c = self.conn.cursor()
            c.execute("SELECT * FROM categories")
            for row in c:
                category = row[str('category')]
                categories.append(category)

            categories = list(dict.fromkeys(categories))
            self.conn.commit()
            c.close()

        except Exception as ex:
            deb('_getPredefinedCategories Error: {}'.format(ex))

        return categories

    def removePredefinedCategoriesDb(self, serviceName):
        c = self.conn.cursor()
        c.execute("DELETE FROM categories WHERE source=?", [serviceName])
        self.conn.commit()
        c.close()

    def addChannel(self, channel):
        self._invokeAndBlockForResult(self._addChannel, channel)

    def _addChannel(self, channel):
        if channel is not None:
            c = self.conn.cursor()
            c.execute('INSERT OR IGNORE INTO channels(id, title, logo, titles, stream_url, visible, weight, source) VALUES(?, ?, ?, ?, ?, ?, (CASE ? WHEN -1 THEN (SELECT COALESCE(MAX(weight)+1, 0) FROM channels WHERE source=?) ELSE ? END), ?)', [channel.id, channel.title, channel.logo, channel.titles, channel.streamUrl, channel.visible, channel.weight, self.source.KEY, channel.weight, self.source.KEY])
            if not c.rowcount:
                c.execute('UPDATE channels SET title=?, logo=?, titles=?, stream_url=?, visible=?, weight=(CASE ? WHEN -1 THEN weight ELSE ? END) WHERE id=? AND source=?', [channel.title, channel.logo, channel.titles, channel.streamUrl, channel.visible, channel.weight, channel.weight, channel.id, self.source.KEY])
            self.conn.commit()
            c.close()

    def removeChannel(self, channelList):
        self._invokeAndBlockForResult(self._removeChannel, channelList)

    def _removeChannel(self, channelList):
        try:
            if channelList is not None:
                for chann in reversed(channelList):
                    channel = Channel(chann, chann)
                    c = self.conn.cursor()
                    c.execute('DELETE FROM channels WHERE id LIKE ? AND title LIKE ?', [channel.id, channel.title])
                    self.conn.commit()
                    c.close()
        except:
            pass

    def saveChannelList(self, callback, channelList):
        self.eventQueue.append([self._saveChannelList, callback, channelList])
        self.event.set()

    def _saveChannelList(self, channelList):
        c = self.conn.cursor()
        for idx, channel in enumerate(channelList):
            c.execute('INSERT OR IGNORE INTO channels(id, title, logo, titles, stream_url, visible, weight, source) VALUES(?, ?, ?, ?, ?, ?, (CASE ? WHEN -1 THEN (SELECT COALESCE(MAX(weight)+1, 0) FROM channels WHERE source=?) ELSE ? END), ?)', [channel.id, channel.title, channel.logo, channel.titles, channel.streamUrl, channel.visible, channel.weight, self.source.KEY, channel.weight, self.source.KEY])
            if not c.rowcount:
                c.execute('UPDATE channels SET title=?, logo=?, titles=?, stream_url=?, visible=?, weight=(CASE ? WHEN -1 THEN weight ELSE ? END) WHERE id=? AND source=?', [channel.title, channel.logo, channel.titles, channel.streamUrl, channel.visible, channel.weight, channel.weight, channel.id, self.source.KEY])
        c.execute("UPDATE sources SET channels_updated=? WHERE id=?", [self.source.getNewUpdateTime(), self.source.KEY])
        self.conn.commit()
        self.channelList = None

    def getChannelList(self, onlyVisible = True, customCategory=None, excludeCurrentCategory = False):
        result = self._invokeAndBlockForResult(self._getChannelList, onlyVisible, customCategory, excludeCurrentCategory)
        return result

    def _getChannelList(self, onlyVisible, customCategory=None, excludeCurrentCategory = False):
        deb('_getChannelList')
        try:
            if not self.channelList or not onlyVisible or excludeCurrentCategory or customCategory:

                if customCategory:
                    category = customCategory
                else:
                    try:
                        category = self.category.decode('utf-8')
                    except:
                        category = self.category

                c = self.conn.cursor()
                channelList = list()

                if self.ChannelsWithStream == 'true':
                    if onlyVisible:
                        c.execute('SELECT DISTINCT chann.id, chann.title, chann.logo, chann.stream_url, chann.source, chann.visible, chann.weight, chann.titles FROM channels AS chann INNER JOIN custom_stream_url AS custom ON UPPER(chann.id) = UPPER(custom.channel) WHERE source=? AND visible=? ORDER BY weight', [self.source.KEY, True])
                    else:
                        c.execute('SELECT DISTINCT chann.id, chann.title, chann.logo, chann.stream_url, chann.source, chann.visible, chann.weight, chann.titles FROM channels AS chann INNER JOIN custom_stream_url AS custom ON UPPER(chann.id) = UPPER(custom.channel) WHERE source=? ORDER BY weight', [self.source.KEY])
                else:
                    if onlyVisible:
                        c.execute('SELECT * FROM channels WHERE source=? AND visible=? ORDER BY weight', [self.source.KEY, True])
                    else:
                        c.execute('SELECT * FROM channels WHERE source=? ORDER BY weight', [self.source.KEY])
                for row in c:
                    channel = Channel(row[str('id')], row[str('title')], row[str('logo')], row[str('titles')], row[str('stream_url')], row[str('visible')], row[str('weight')])
                    channelList.append(channel)
                c.close()

                NONE = "0"
                SORT = "1"
                CATEGORIES = "2"
                newCList = []

                cats = False

                if list(self.getAllCategories()):
                    cats = True
                    f = xbmcvfs.File('special://profile/addon_data/script.mtvguide/categories.ini','rb')
                    lines = f.read().splitlines()
                    f.close()
                    filter = []
                    seen = set()
                    for line in lines:
                        if PY3:
                            if "=" not in line:
                                continue
                        else:
                            if b"=" not in line:
                                continue

                        if PY3:
                            name,cat = line.split('=')
                        else:
                            name,cat = line.split(b'=')
                        if cat == self.category:
                            if name not in seen:
                                filter.append(name)
                            seen.add(name)

                if GET_CHANNEL_FILTER == SORT:
                    channelList = sorted(channelList, key=lambda channel: channel.title.lower())

                elif GET_CHANNEL_FILTER == CATEGORIES:
                    for filter_name in filter:
                        for channel in channelList:
                            if channel.title == filter_name:
                                newCList.append(channel)

                    if newCList:
                        channelList = newCList

                if category:
                    channelList = self.getCategoryChannelList(category, channelList, excludeCurrentCategory)

                if onlyVisible and excludeCurrentCategory == False and customCategory is None:
                    self.channelList = channelList
            else:
                channelList = self.channelList

            return channelList

        except Exception as ex:
            deb('getChannelList Exception: {}'.format(ex))
            if self.channelList:
                channelList = self.channelList
            else:
                channelList = list()
            return channelList

    def getAllChannelList(self, onlyVisible = True):
        result = self._invokeAndBlockForResult(self._getAllChannelList, onlyVisible)
        return result

    def _getAllChannelList(self, onlyVisible):
        if not self.channelListAll:# or not onlyVisible:

            c = self.conn.cursor()
            channelList = list()

            if onlyVisible:
                c.execute('SELECT * FROM channels WHERE source=? AND visible=? ORDER BY weight', [self.source.KEY, True])
            else:
                c.execute('SELECT * FROM channels WHERE source=? ORDER BY weight', [self.source.KEY])
            for row in c:
                channel = Channel(row[str('id')], row[str('title')],row[str('logo')], row[str('titles')], row[str('stream_url')], row[str('visible')], row[str('weight')])
                channelList.append(channel)
            c.close()

        else:
            channelList = self.channelListAll
        return channelList

    def addCategory(self, category):
        try:
            categories = []

            for k, v in EPG_DICT.items():
                if k.upper() == category:
                    categories.append(k.upper())

                elif '.' + k.lower() == category:
                    categories.append(k.upper())

                elif v['alpha-3'] == category:
                    categories.append(k.upper())

                elif v['language'] == category:
                    categories.append(k.upper())

                elif v['native'] == category:
                    categories.append(k.upper())

                else:
                    categories.append(category)

            categories = list(dict.fromkeys(categories))
            return categories

        except Exception as ex:
            deb('addCategory error: {}'.format(ex))

    def getCategoryChannelList(self, category, channelList, excludeCurrentCategory):
        try:
            newChannelList = []

            newList = [strings(30995) + ': {}'.format(cat) for cat in PREDEFINED_CATEGORIES]

            if category in newList:
                predefined_category_re = re.compile(strings(30995) + r': ([^\s]*)', re.IGNORECASE)
                r = predefined_category_re.search(category)
                category = r.group(1) if r else ''
                categories = self.addCategory(category)

                deb('Using predefined category: {}'.format(category))
                predefined = '|'.join(categories)

                channel_regex = re.compile(r'.*({})$'.format(predefined))
                newChannelList = [channel for channel in channelList[:] if channel_regex.search(channel.id)]
                if not newChannelList:
                    channelList = []

            else:
                category = category.replace(strings(30995), 'TV Group')

                channelsInCategory = self.getChannelsInCategory(category)
                deb('Using custom category: {}'.format(category))

                if len(channelsInCategory) > 0:
                    newChannelList = [channel for channel in channelList[:] if channel.title in channelsInCategory]

            if len(newChannelList) > 0 and not excludeCurrentCategory:
                channelList = newChannelList

        except Exception as ex:
            deb('getCategoryChannelList error: {}'.format(ex))

        return channelList

    def getCategoryMap(self):
        categoryMap = list()
        try:
            f = xbmcvfs.File('special://profile/addon_data/script.mtvguide/categories.ini','rb')
            lines = f.read().splitlines()
            f.close()

            for line in lines:
                try:
                    name, category = line.split('=')
                except:
                    name, category = line.decode('utf-8').split('=')
                categoryMap.append((name, category))
        except:
            deb('getCategoryMap Error: {}'.format(getExceptionString()))

        return categoryMap

    def saveCategoryMap(self, categories, custom=False):
        self.channelList = None
        if custom:
            try:
                newList = list()
                for channel, cat in categories:
                    line = "{}={}".format(channel, cat)
                    newList.append(line)

                f = xbmcvfs.File('special://profile/addon_data/script.mtvguide/categories.ini','wb')
                f.write(bytearray('\n'.join(newList), 'utf-8'))
                f.close()
            except:
                deb('custom saveCategoryMap Error: {}'.format(getExceptionString()))
        else:
            try:
                f = xbmcvfs.File('special://profile/addon_data/script.mtvguide/categories.ini','wb')
                for cat in categories:
                    for channel in categories[cat]:
                        try:
                            f.write(bytearray("{}={}\n".format(channel, cat), 'utf-8'))
                        except:
                            f.write(bytearray("{}={}\n".format(channel, cat.decode('utf-8')), 'utf-8'))
                f.close()
            except:
                deb('saveCategoryMap Error: {}'.format(getExceptionString()))

    def getChannelsInCategory(self, category):
        channelList = set()
        for channel, cat in self.getCategoryMap():
            if cat == category:
                channelList.add(channel)
        return channelList

    def getAllCategories(self):
        from collections import OrderedDict
        categoryList = list()
        for _, cat in self.getCategoryMap():
            categoryList.append(cat)
        categoryList = OrderedDict((k, None) for k in categoryList)
        return categoryList

    def programSearch(self, search):
        return self._invokeAndBlockForResult(self._programSearch, search)

    def _programSearch(self, search):
        programList = []
        now = datetime.now()
        pre_days = int(ADDON.getSetting('listing_pre_days'))
        days = int(ADDON.getSetting('listing_days'))
        startTime = now - timedelta(days=pre_days)
        endTime = now + timedelta(days=days)
        c = self.conn.cursor()
        channelList = self._getChannelList(True)
        if PY3:
            search = '%%{}%%'.format(search)
        else:
            search = '%%{}%%'.format(search.decode('utf-8'))

        for channel in channelList:

            if ADDON.getSetting('program_search_plot') == 'true':
                try: c.execute('SELECT * FROM programs WHERE channel=? AND source=? AND start_date>=? AND end_date<=? AND (title LIKE ? OR description LIKE ?) OR channel=? AND source=? AND start_date<=? AND end_date>=? AND (title LIKE ? OR description LIKE ?)',
                          [channel.id, self.source.KEY, startTime, endTime, search, search, channel.id, self.source.KEY, now, now, search, search])
                except: return
            else:
                try: c.execute('SELECT * FROM programs WHERE channel=? AND source=? AND start_date>=? AND end_date<=? AND title LIKE ? OR channel=? AND source=? AND start_date<=? AND end_date>=? AND title LIKE ?',
                          [channel.id, self.source.KEY, startTime, endTime, search, channel.id, self.source.KEY, now, now, search])
                except: return
            for row in c:
                program = Program(channel, row[str('title')], row[str('start_date')], row[str('end_date')], row[str('description')], row[str('productionDate')], row[str('director')], row[str('actor')], row[str('episode')], row[str('rating')], row[str('image_large')], row[str('image_small')], row[str('categoryA')], row[str('categoryB')])
                programList.append(program)
        c.close()
        return programList

    def descriptionSearch(self, search):
        return self._invokeAndBlockForResult(self._descriptionSearch, search)

    def _descriptionSearch(self, search):
        programList = []
        now = datetime.now()
        pre_days = int(ADDON.getSetting('listing_pre_days'))
        days = int(ADDON.getSetting('listing_days'))
        startTime = now - timedelta(days=pre_days)
        endTime = now + timedelta(days=days)
        c = self.conn.cursor()
        channelList = self._getChannelList(True)
        if PY3:
            search = '%%{}%%'.format(search)
        else:
            search = '%%{}%%'.format(search.decode('utf-8'))

        for channel in channelList:

            try: c.execute('SELECT * FROM programs WHERE channel=? AND source=? AND description LIKE ? AND start_date>=? AND end_date<=? OR channel=? AND source=? AND description LIKE ? AND start_date<=? AND end_date>=?',
                      [channel.id, self.source.KEY, search, startTime, endTime, channel.id, self.source.KEY, search, now, now])
            except: return
            for row in c:
                program = Program(channel, row[str('title')], row[str('start_date')], row[str('end_date')], row[str('description')], row[str('productionDate')], row[str('director')], row[str('actor')], row[str('episode')], row[str('rating')], row[str('image_large')], row[str('image_small')], row[str('categoryA')], row[str('categoryB')])
                programList.append(program)
        c.close()
        return programList

    def programCategorySearch(self, search):
        return self._invokeAndBlockForResult(self._programCategorySearch, search)

    def _programCategorySearch(self, search):
        programList = []
        now = datetime.now()
        pre_days = int(ADDON.getSetting('listing_pre_days'))
        days = int(ADDON.getSetting('listing_days'))
        startTime = now - timedelta(days=pre_days)
        endTime = now + timedelta(days=days)
        c = self.conn.cursor()
        channelList = self._getChannelList(True)
        if PY3:
            search = '%%{}%%'.format(search)
        else:
            search = '%%{}%%'.format(search.decode('utf-8'))

        for channel in channelList:

            try: c.execute('SELECT * FROM programs WHERE channel=? AND source=? AND (categoryA LIKE ? OR categoryB LIKE ?) AND start_date>=? AND end_date<=? OR channel=? AND source=? AND (categoryA LIKE ? OR categoryB LIKE ?) AND start_date<=? AND end_date>=?',
                      [channel.id, self.source.KEY, search, search, startTime, endTime, channel.id, self.source.KEY, search, search, now, now])
            except: return
            for row in c:
                program = Program(channel, row[str('title')], row[str('start_date')], row[str('end_date')], row[str('description')], row[str('productionDate')], row[str('director')], row[str('actor')], row[str('episode')], row[str('rating')], row[str('image_large')], row[str('image_small')], row[str('categoryA')], row[str('categoryB')])
                programList.append(program)
        c.close()
        return programList

    def getChannelListing(self, channel):
        return self._invokeAndBlockForResult(self._getChannelListing, channel)

    def _getChannelListing(self, channel):
        now = datetime.now()
        days = int(ADDON.getSetting('listing_days'))
        endTime = now + timedelta(days=days)
        programList = []
        c = self.conn.cursor()

        try: c.execute('SELECT * FROM programs WHERE channel=? AND end_date>? AND start_date<?',
                  [channel.id, now, endTime])
        except: return
        for row in c:
            program = Program(channel, row[str('title')], row[str('start_date')], row[str('end_date')], row[str('description')], row[str('productionDate')], row[str('director')], row[str('actor')], row[str('episode')], row[str('rating')], row[str('image_large')], row[str('image_small')], row[str('categoryA')], row[str('categoryB')])
            programList.append(program)
        c.close()

        return programList

    def channelSearch(self, search):
        return self._invokeAndBlockForResult(self._channelSearch, search)

    def _channelSearch(self, search):
        programList = []
        now = datetime.now()
        c = self.conn.cursor()
        channels = self._getChannelList(True)
        channelIds = [cc.id for cc in channels]
        channelMap = dict()
        ids = []
        for cc in channels:
            if cc.id:
                channelMap[cc.id] = cc
                search = search.replace(' ','.*')
                if re.search(search,cc.title,flags=re.I):
                    ids.append(cc.id)
        if not ids:
            return
        ids_string = '\',\''.join(ids)
        c.execute('SELECT * FROM programs WHERE channel IN (\'' + ids_string + '\') AND source=?',
                  [self.source.KEY])
        for row in c:
            program = Program(channelMap[row[str('channel')]], title=row[str('title')], startDate=row[str('start_date')], endDate=row[str('end_date')],
                  description=row[str('description')], episode=row[str('episode')], rating=row[str('rating')], imageLarge=row[str('image_large')], imageSmall=row[str('image_small')], categoryA=row[str('categoryA')], categoryB=row[str('categoryB')])
            programList.append(program)
        c.close()
        return programList

    def getNowList(self, channel):
        return self._invokeAndBlockForResult(self._getNowList, channel)

    def _getNowList(self, channel):
        programList = []
        now = datetime.now()
        channels = self._getChannelList(True)
        channelIds = [c.id for c in channels]
        channelMap = dict()
        for cc in channels:
            if cc.id:
                channelMap[cc.id] = cc

        c = self.conn.cursor()
        c.execute('SELECT DISTINCT p.*' + 'FROM programs p, channels c WHERE p.channel IN (\'' + ('\',\''.join(channelIds)) + '\') AND p.channel=c.id AND p.source=? AND p.end_date >= ? AND p.start_date <= ?' + 'ORDER BY c.weight', [self.source.KEY, now, now])

        for row in c:
            notification_scheduled = ''
            recording_scheduled = ''
            program = Program(channelMap[row[str('channel')]], title=row[str('title')], startDate=row[str('start_date')], endDate=row[str('end_date')],
                  description=row[str('description')], episode=row[str('episode')], rating=row[str('rating')], imageLarge=row[str('image_large')], imageSmall=row[str('image_small')], categoryA=row[str('categoryA')], categoryB=row[str('categoryB')],
                  notificationScheduled=str(notification_scheduled), recordingScheduled=str(recording_scheduled))
            programList.append(program)
        c.close()
        return programList

    def getNextList(self, channel):
        return self._invokeAndBlockForResult(self._getNextList, channel)

    def _getNextList(self, channel):
        programList = []
        now = datetime.now()
        c = self.conn.cursor()
        channelList = self._getChannelList(True)
        for channel in channelList:
            try: c.execute('SELECT * FROM programs WHERE channel=? AND source=? AND start_date >= ? AND end_date >= ?', [channel.id, self.source.KEY,now,now])
            except: return
            row = c.fetchone()
            if row:
                program = Program(channel, row[str('title')], row[str('start_date')], row[str('end_date')], row[str('description')], row[str('productionDate')], row[str('director')], row[str('actor')], row[str('episode')], row[str('rating')], row[str('image_large')], row[str('image_small')], row[str('categoryA')], row[str('categoryB')])
                programList.append(program)
        c.close()
        return programList

    def getCurrentProgram(self, channel):
        return self._invokeAndBlockForResult(self._getCurrentProgram, channel)

    def _getCurrentProgram(self, channel):
        sqlite3.register_adapter(datetime, self.adapt_datetime)
        sqlite3.register_converter(str('timestamp'), self.convert_datetime)

        program = None

        if channel is None:
            return None

        try:
            now = datetime.now() + timedelta(minutes=int(ADDON.getSetting('timebar_adjust')))
        except:
            now = datetime.now()

        c = self.conn.cursor()
        c.execute('SELECT * FROM programs WHERE channel=? AND source=? AND start_date <= ? AND end_date >= ?', [channel.id, self.source.KEY, now, now])
        row = c.fetchone()
        if row:
            program = Program(channel, row[str('title')], row[str('start_date')], row[str('end_date')], row[str('description')], row[str('productionDate')], row[str('director')], row[str('actor')], row[str('episode')], row[str('rating')], row[str('image_large')], row[str('image_small')], row[str('categoryA')], row[str('categoryB')])
        else:
            try:
                title = channel.title
            except:
                title = ''

            try:
                start = channel.start_date
            except:
                start = datetime.now().replace(microsecond=0)

            try:
                end = channel.end_date
            except:
                end = datetime.now().replace(microsecond=0)

            try:
                desc = channel.description
            except:
                desc = ''

            try:
                date = channel.productionDate
            except:
                date = ''

            try:
                director = channel.director
            except:
                director = ''

            try:
                actor = channel.actor
            except:
                actor = ''

            try:
                episode = channel.episode
            except:
                episode = ''

            try:
                rating = channel.rating
            except:
                rating = ''

            try:
                imageLarge = channel.image_large
            except:
                imageLarge = 'tvguide-logo-epg.png'

            try:
                imageSmall = channel.image_small
            except:
                imageSmall = 'tvguide-logo-epg.png'

            try:
                categoryA = channel.categoryA
            except:
                categoryA = ''

            try:
                categoryB = channel.categoryB
            except:
                categoryB = ''

            program = Program(channel, title, start, end, desc, date, director, actor, episode, rating, imageLarge, imageSmall, categoryA, categoryB)
        c.close()

        return program

    def getNextProgram(self, program):
        return self._invokeAndBlockForResult(self._getNextProgram, program)

    def _getNextProgram(self, program):
        nextProgram = None
        c = self.conn.cursor()
        c.execute('SELECT * FROM programs WHERE channel=? AND source=? AND start_date >= ? ORDER BY start_date ASC LIMIT 1', [program.channel.id, self.source.KEY, program.endDate])
        row = c.fetchone()
        if row:
            nextProgram = Program(program.channel, row[str('title')], row[str('start_date')], row[str('end_date')], row[str('description')], row[str('productionDate')], row[str('director')], row[str('actor')], row[str('episode')], row[str('rating')], row[str('image_large')], row[str('image_small')], row[str('categoryA')], row[str('categoryB')])
        c.close()
        return nextProgram

    def getPreviousProgram(self, program):
        return self._invokeAndBlockForResult(self._getPreviousProgram, program)

    def _getPreviousProgram(self, program):
        previousProgram = None
        c = self.conn.cursor()
        c.execute('SELECT * FROM programs WHERE channel=? AND source=? AND end_date <= ? ORDER BY start_date DESC LIMIT 1', [program.channel.id, self.source.KEY, program.startDate])
        row = c.fetchone()
        if row:
            previousProgram = Program(program.channel, row[str('title')], row[str('start_date')], row[str('end_date')], row[str('description')], row[str('productionDate')], row[str('director')], row[str('actor')], row[str('episode')], row[str('rating')], row[str('image_large')], row[str('image_small')], row[str('categoryA')], row[str('categoryB')])
        c.close()
        return previousProgram

    def getPrograms(self, channel, _program, startTime, endTime):
        return self._invokeAndBlockForResult(self._getPrograms, channel, _program, startTime, endTime)

    def _getPrograms(self, channel, _program, startTime, endTime):
        result = None

        c = self.conn.cursor()
        c.execute('SELECT * FROM programs WHERE channel = ? AND source = ?  AND ( (end_date > ?) AND (start_date < ? ) )', [channel.id, self.source.KEY, startTime, endTime])
        for row in c:
            program = Program(channel, row[str('title')], row[str('start_date')], row[str('end_date')], row[str('description')], row[str('productionDate')], row[str('director')], row[str('actor')], row[str('episode')], row[str('rating')], row[str('image_large')], row[str('image_small')], row[str('categoryA')], row[str('categoryB')])
            if program.title == _program.title:
                result = program

        c.close()
        return result

    def getProgramStartingAt(self, channel, startTime, endTime):
        return self._invokeAndBlockForResult(self._getProgramStartingAt, channel, startTime, endTime)

    def _getProgramStartingAt(self, channel, startTime, endTime):
        program = None
        c = self.conn.cursor()
        if endTime:
            c.execute('SELECT * FROM programs WHERE channel=? AND source=? AND ( (end_date > ?) AND (start_date < ? ) )', [channel.id, self.source.KEY, startTime, endTime])
        else:
            c.execute('SELECT * FROM programs WHERE channel=? AND source=? AND start_date <= ? AND end_date >= ?', [channel.id, self.source.KEY, startTime, startTime])
        row = c.fetchone()
        if row:
            program = Program(channel, row[str('title')], row[str('start_date')], row[str('end_date')], row[str('description')], row[str('productionDate')], row[str('director')], row[str('actor')], row[str('episode')], row[str('rating')], row[str('image_large')], row[str('image_small')], row[str('categoryA')], row[str('categoryB')])

        c.close()
        return program

    def _getProgramList(self, channels, startTime):
        deb('_getProgramList')
        programList = list()
        try:
            """
            @param channels:
            @type channels: list of source.Channel
            @param startTime:
            @type startTime: datetime
            @return:
            """
            endTime = startTime + timedelta(hours=2)
            channelsWithoutProg = list(channels)

            channelMap = dict()
            for c in channels:
                if c.id:
                    channelMap[c.id] = c
            if not channels:
                return []

            c = self.conn.cursor()

            if startTime == '' or startTime is None:
                startTime = datetime.now().replace(microsecond=0)

            if endTime == '' or endTime is None:
                endTime = datetime.now().replace(microsecond=0)

            c.execute('SELECT p.*, (SELECT 1 FROM notifications n WHERE n.channel=p.channel AND n.program_title=p.title AND n.source=p.source AND (n.start_date IS NULL OR n.start_date = p.start_date)) AS notification_scheduled , (SELECT 1 FROM recordings r WHERE r.channel=p.channel AND r.program_title=p.title AND r.start_date=p.start_date AND r.source=p.source) AS recording_scheduled FROM programs p WHERE p.channel IN (\'' + ('\',\''.join(channelMap.keys())) + '\') AND p.source=? AND p.end_date > ? AND p.start_date < ?', [self.source.KEY, startTime, endTime])

            for row in c:
                program = Program(channelMap[row[str('channel')]], row[str('title')], row[str('start_date')], row[str('end_date')], row[str('description')], row[str('productionDate')], row[str('director')], row[str('actor')], row[str('episode')], row[str('rating')], row[str('image_large')], row[str('image_small')], row[str('categoryA')], row[str('categoryB')], row[str('notification_scheduled')], row[str('recording_scheduled')])
                programList.append(program)
                try:
                    channelsWithoutProg.remove(channelMap[row[str('channel')]])
                except ValueError:
                    pass

            for channel in channelsWithoutProg:
                try:
                    title = channel.title
                except:
                    title = ''

                try:
                    start = channel.start_date
                except:
                    start = startTime

                try:
                    end = channel.end_date
                except:
                    end = endTime

                try:
                    desc = channel.description
                except:
                    desc = ''

                try:
                    date = channel.productionDate
                except:
                    date = ''

                try:
                    director = channel.director
                except:
                    director = ''

                try:
                    actor = channel.actor
                except:
                    actor = ''

                try:
                    episode = channel.episode
                except:
                    episode = ''

                try:
                    rating = channel.rating
                except:
                    rating = ''

                try:
                    imageLarge = channel.image_large
                except:
                    imageLarge = 'tvguide-logo-epg.png'

                try:
                    imageSmall = channel.image_small
                except:
                    imageSmall = 'tvguide-logo-epg.png'

                try:
                    categoryA = channel.categoryA
                except:
                    categoryA = ''

                try:
                    categoryB = channel.categoryB
                except:
                    categoryB = ''

                program = Program(channel, title, start, end, desc, date, director, actor, episode, rating, imageLarge, imageSmall, categoryA, categoryB)
                programList.append(program)
            c.close()
        except Exception as ex:
            deb('_getProgramList Exception: {}'.format(getExceptionString()))
            xbmcgui.Dialog().ok(ADDON.getAddonInfo('name'), strings(DATABASE_SCHEMA_ERROR_1) + '\n' + strings(DATABASE_SCHEMA_ERROR_2) + ' ' + strings(DATABASE_SCHEMA_ERROR_3))
        return programList

    def _isProgramListCacheExpired(self, date = datetime.now()):
        deb('_isProgramListCacheExpired')
        # check if data is up-to-date in database
        dateStr = date.strftime('%Y-%m-%d')
        c = self.conn.cursor()
        c.execute('SELECT programs_updated FROM updates WHERE source=? AND date=?', [self.source.KEY, dateStr])
        row = c.fetchone()
        today = datetime.now()
        expired = row is None or row[str('programs_updated')].day != today.day
        c.close()
        return expired

    def setCustomStreamUrl(self, channel, stream_url):
        if stream_url is not None:
            self._invokeAndBlockForResult(self._setCustomStreamUrl, channel, stream_url)
        # no result, but block until operation is done

    def _setCustomStreamUrl(self, channel, stream_url):
        deb('_setCustomStreamUrl')
        if stream_url is not None:
            c = self.conn.cursor()
            c.execute("DELETE FROM custom_stream_url WHERE channel like ?", [channel.id])
            c.execute("INSERT INTO custom_stream_url(channel, stream_url, priority) VALUES(?, ?, ?)", [channel.id, stream_url, 12]) #.decode('utf-8', 'ignore')])
            self.conn.commit()
            c.close()
            self.channelList = None

    def getCustomChannel(self, cid, service):
        return self._invokeAndBlockForResult(self._getCustomChannel, cid, service)

    def _getCustomChannel(self, cid, service):
        deb('_getCustomStreamUrl')

        stream_url = 'service={0}&cid={1}'.format(service, cid)

        c = self.conn.cursor()
        c.execute("SELECT stream_url FROM custom_stream_url WHERE strm like ? limit 1", [stream_url])
        channel = c.fetchone()
        c.close()

        return channel

    def getCustomStreamUrl(self, channel):
        return self._invokeAndBlockForResult(self._getCustomStreamUrl, channel)

    def _getCustomStreamUrl(self, channel):
        deb('_getCustomStreamUrl')
        c = self.conn.cursor()
        c.execute("SELECT stream_url FROM custom_stream_url WHERE channel like ? limit 1", [channel.id])
        stream_url = c.fetchone()
        c.close()

        if stream_url:
            deb('stream url is {}'.format(stream_url[0]))
            return stream_url[0]
        else:
            return None

    def getCustomStreamUrlList(self, channel):
        return self._invokeAndBlockForResult(self._getCustomStreamUrlList, channel)

    def _getCustomStreamUrlList(self, channel):
        deb('_getCustomStreamUrlList')
        result = list()
        c = self.conn.cursor()
        c.execute("SELECT stream_url, priority FROM custom_stream_url WHERE channel like ? OR channel like ?", [channel.id, channel.title])
        for row in c:
            url = row[str('stream_url')]
            priority = row[str('priority')]
            result.append([url, priority])
        c.close()
        return result

    def getAllStreamUrlList(self):
        return self._invokeAndBlockForResult(self._getAllStreamUrlList)

    def _getAllStreamUrlList(self):
        deb('_getAllStreamUrlList')
        result = list()
        c = self.conn.cursor()
        c.execute("SELECT channel, stream_url FROM custom_stream_url")
        for row in c:
            url = row[str('channel')]
            cid = row[str('stream_url')]
            result.append(url+', '+cid.upper())
        c.close()
        return result

    def getAllCatchupUrlList(self, channels):
        return self._invokeAndBlockForResult(self._getAllCatchupUrlList, channels)

    def _getAllCatchupUrlList(self, channels):
        deb('_getAllCatchupUrlList')
        result = dict()

        channelList = list()

        for chann in channels:
            channelList.append(chann.id.upper())
            channelList.append(chann.title.upper())

        c = self.conn.cursor()
        c.execute("SELECT channel, stream_url FROM custom_stream_url")

        for row in c:
            if row[str('channel')].upper() in channelList:

                url = row[str('channel')]
                cid = row[str('stream_url')]

                if url in result:
                    result[url].append(cid)
                else:
                    result[url]=[cid]

        c.close()

        return result

    def deleteCustomStreamUrl(self, channel):
        self.eventQueue.append([self._deleteCustomStreamUrl, None, channel])
        self.event.set()

    def _deleteCustomStreamUrl(self, channel):
        deb('_deleteCustomStreamUrl')
        c = self.conn.cursor()
        c.execute("DELETE FROM custom_stream_url WHERE channel like ?", [channel.id])
        self.conn.commit()
        c.close()
        self.channelList = None

    def getStreamUrl(self, channel):
        deb('getStreamUrl')
        customStreamUrl = self.getCustomStreamUrl(channel)
        if customStreamUrl:
            customStreamUrl = customStreamUrl.encode('utf-8', 'ignore')
            return customStreamUrl
        elif channel.isPlayable():
            streamUrl = channel.streamUrl.encode('utf-8', 'ignore')
            return streamUrl
        return None

    def getStreamUrlList(self, channel):
        deb('getStreamUrlList')
        customStreamUrlList = self.getCustomStreamUrlList(channel)
        if len(customStreamUrlList) > 0:
            for url in customStreamUrlList:
                deb('getStreamUrlList channel: %-30s, stream: %-30s' % (channel.id, url[0]))

        elif channel.isPlayable():
            streamUrl = channel.streamUrl
            customStreamUrlList.append(streamUrl)
        return customStreamUrlList

    def adapt_datetime(self, ts):
        try:
            adapt_datetime = time.mktime(ts.timetuple())
        except:
            ts = datetime.now()
            adapt_datetime = time.mktime(ts.timetuple())

        return adapt_datetime

    def convert_datetime(self, ts):
        try:
            return datetime.fromtimestamp(float(ts))
        except ValueError:
            return None

    def _createTables(self):
        c = self.conn.cursor()

        try:
            c.execute('SELECT major, minor, patch FROM version')
            (major, minor, patch) = c.fetchone()
            version = [major, minor, patch]
        except sqlite3.OperationalError:
            version = [0, 0, 0]

        try:
            if version < [1, 3, 0]:
                c.execute('CREATE TABLE IF NOT EXISTS custom_stream_url(channel TEXT, stream_url TEXT)')
                c.execute('CREATE TABLE version (major INTEGER, minor INTEGER, patch INTEGER)')
                c.execute('INSERT INTO version(major, minor, patch) VALUES(1, 3, 0)')

                # For caching data
                c.execute('CREATE TABLE sources(id TEXT PRIMARY KEY, channels_updated TIMESTAMP)')
                c.execute('CREATE TABLE updates(id INTEGER PRIMARY KEY, source TEXT, date TEXT, programs_updated TIMESTAMP)')
                c.execute('CREATE TABLE channels(id TEXT, title TEXT, logo TEXT, stream_url TEXT, source TEXT, visible BOOLEAN, weight INTEGER, PRIMARY KEY (id, source), FOREIGN KEY(source) REFERENCES sources(id) ON DELETE CASCADE)')
                c.execute('CREATE TABLE programs(channel TEXT, title TEXT, start_date TIMESTAMP, end_date TIMESTAMP, description TEXT, productionDate TEXT, director TEXT, actor TEXT, episode TEXT, image_large TEXT, image_small TEXT, categoryA TEXT, categoryB TEXT, source TEXT, updates_id INTEGER, FOREIGN KEY(channel, source) REFERENCES channels(id, source) ON DELETE CASCADE, FOREIGN KEY(updates_id) REFERENCES updates(id) ON DELETE CASCADE)')
                c.execute('CREATE INDEX program_list_idx ON programs(source, channel, start_date, end_date)')
                c.execute('CREATE INDEX start_date_idx ON programs(start_date)')
                c.execute('CREATE INDEX end_date_idx ON programs(end_date)')

                # For active setting
                c.execute('CREATE TABLE settings(key TEXT PRIMARY KEY, value TEXT)')

                # For notifications
                c.execute("CREATE TABLE notifications(channel TEXT, program_title TEXT, source TEXT, FOREIGN KEY(channel, source) REFERENCES channels(id, source) ON DELETE CASCADE)")
                self.conn.commit()

            if version < [1, 3, 1]:
                # Recreate tables with FOREIGN KEYS as DEFERRABLE INITIALLY DEFERRED
                c.execute('UPDATE version SET major=1, minor=3, patch=1')
                c.execute('DROP TABLE channels')
                c.execute('DROP TABLE programs')
                c.execute('CREATE TABLE channels(id TEXT, title TEXT, logo TEXT, stream_url TEXT, source TEXT, visible BOOLEAN, weight INTEGER, PRIMARY KEY (id, source), FOREIGN KEY(source) REFERENCES sources(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED)')
                c.execute('CREATE TABLE programs(channel TEXT, title TEXT, start_date TIMESTAMP, end_date TIMESTAMP, description TEXT, productionDate TEXT, director TEXT, actor TEXT, episode TEXT, image_large TEXT, image_small TEXT, categoryA TEXT, categoryB TEXT, source TEXT, updates_id INTEGER, FOREIGN KEY(channel, source) REFERENCES channels(id, source) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED, FOREIGN KEY(updates_id) REFERENCES updates(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED)')
                c.execute('CREATE INDEX program_list_idx ON programs(source, channel, start_date, end_date)')
                c.execute('CREATE INDEX start_date_idx ON programs(start_date)')
                c.execute('CREATE INDEX end_date_idx ON programs(end_date)')
                self.conn.commit()

            if version < [3, 0, 0]:
                # Nowe tabele na nowa wersje :P
                c.execute('CREATE TABLE IF NOT EXISTS version (major INTEGER, minor INTEGER, patch INTEGER)')
                c.execute('UPDATE version SET major=3, minor=0, patch=0')
                c.execute('DROP TABLE custom_stream_url')
                c.execute('DROP TABLE sources')
                c.execute('DROP TABLE updates')
                c.execute('DROP TABLE settings')
                c.execute('DROP TABLE notifications')
                c.execute('DROP TABLE programs')
                c.execute('DROP TABLE channels')
                c.execute('CREATE TABLE IF NOT EXISTS custom_stream_url(channel TEXT COLLATE NOCASE, stream_url TEXT)')
                c.execute('CREATE TABLE IF NOT EXISTS sources(id TEXT PRIMARY KEY, channels_updated TIMESTAMP)')
                c.execute('CREATE TABLE IF NOT EXISTS updates(id INTEGER PRIMARY KEY, source TEXT, date TEXT, programs_updated TIMESTAMP)')
                c.execute('CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT)')
                c.execute("CREATE TABLE IF NOT EXISTS notifications(channel TEXT, program_title TEXT, source TEXT, FOREIGN KEY(channel, source) REFERENCES channels(id, source) ON DELETE CASCADE)")
                c.execute('CREATE TABLE IF NOT EXISTS channels(id TEXT, title TEXT, logo TEXT, stream_url TEXT, source TEXT, visible BOOLEAN, weight INTEGER, PRIMARY KEY (id, source), FOREIGN KEY(source) REFERENCES sources(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED)')
                c.execute('CREATE TABLE IF NOT EXISTS programs(channel TEXT, title TEXT, start_date TIMESTAMP, end_date TIMESTAMP, description TEXT, productionDate TEXT, director TEXT, actor TEXT, episode TEXT, image_large TEXT, image_small TEXT, categoryA TEXT, categoryB TEXT, source TEXT, updates_id INTEGER, FOREIGN KEY(channel, source) REFERENCES channels(id, source) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED, FOREIGN KEY(updates_id) REFERENCES updates(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED)')
                c.execute('CREATE INDEX program_list_idx ON programs(source, channel, start_date, end_date)')
                c.execute('CREATE INDEX start_date_idx ON programs(start_date)')
                c.execute('CREATE INDEX end_date_idx ON programs(end_date)')
                self.conn.commit()

            if version < [3, 1, 0]:
                c.execute("SELECT * FROM custom_stream_url")
                channelList = list()
                for row in c:
                    channel = [row[str('channel')], row[str('stream_url')]]
                    channelList.append(channel)

                c.execute('UPDATE version SET major=3, minor=1, patch=0')
                c.execute('DROP TABLE custom_stream_url')
                c.execute('CREATE TABLE IF NOT EXISTS custom_stream_url(channel TEXT COLLATE NOCASE, stream_url TEXT)')

                for channel in channelList:
                    c.execute("INSERT INTO custom_stream_url(channel, stream_url) VALUES(?, ?)", [channel[0], channel[1]])

                self.conn.commit()

            if version < [6, 1, 0]:
                c.execute("CREATE TABLE IF NOT EXISTS recordings(channel TEXT, program_title TEXT, start_date TIMESTAMP, end_date TIMESTAMP, source TEXT, FOREIGN KEY(channel, source) REFERENCES channels(id, source) ON DELETE CASCADE)")
                c.execute('UPDATE version SET major=6, minor=1, patch=0')
                self.conn.commit()

            if version < [6, 1, 1]:
                c.execute('ALTER TABLE updates ADD COLUMN epg_size INTEGER DEFAULT 0')
                c.execute('UPDATE version SET major=6, minor=1, patch=1')
                self.conn.commit()

            if version < [6, 1, 5]:
                c.execute('ALTER TABLE notifications ADD COLUMN start_date TIMESTAMP DEFAULT NULL')
                c.execute('UPDATE version SET major=6, minor=1, patch=5')
                self.conn.commit()


            if version < [6, 2, 3]:
                deb('DATABASE UPLIFT TO VERSION 6.2.3')
                channelList = list()
                notificationList = list()

                c.execute("SELECT * FROM channels ORDER BY VISIBLE DESC, WEIGHT ASC")
                for row in c:
                    channelList.append(row)

                c.execute("SELECT * FROM notifications")
                for row in c:
                    notificationList.append(row)

                c.execute('DELETE FROM channels')
                c.execute('DELETE FROM programs')
                c.execute('DELETE FROM notifications')
                c.execute('DELETE FROM recordings')
                c.execute('DELETE FROM updates')
                self.conn.commit()

                for channel in channelList:
                    c.execute("INSERT OR IGNORE INTO channels(id, title, logo, stream_url, source, visible, weight) VALUES(?, ?, ?, ?, ?, ?, ?)", [channel['id'].upper(), channel['title'], channel['logo'], channel['stream_url'], channel['source'], channel['visible'], channel['weight'] ])

                for notification in notificationList:
                    c.execute("INSERT OR IGNORE INTO notifications(channel, program_title, source, start_date) VALUES(?, ?, ?, ?)", [ notification['channel'].upper(), notification['program_title'], notification['source'], notification['start_date'] ])

                c.execute('CREATE TABLE IF NOT EXISTS rss_messages(last_message TIMESTAMP)')
                c.execute('UPDATE version SET major=6, minor=2, patch=3')

                self.conn.commit()

            if version < [6, 6, 5]:
                ADDON.setSetting(id="ffmpeg_format", value=('mpegts'))
                c.execute('UPDATE version SET major=6, minor=6, patch=5')
                self.conn.commit()

            if version < [6, 6, 9]:
                #its version 6.6.8...
                ADDON.setSetting(id="XXX_EPG", value=(""))
                ADDON.setSetting(id="showAdultChannels", value=(strings(30720)))
                c.execute('UPDATE version SET major=6, minor=6, patch=9')
                self.conn.commit()

            if version < [6, 6, 9]:
                #its version 6.6.8...
                ADDON.setSetting(id="VOD_EPG", value=(""))
                ADDON.setSetting(id="showVodChannels", value=(strings(30720)))
                c.execute('UPDATE version SET major=6, minor=6, patch=9')
                self.conn.commit()

            if version < [6, 7, 1]:
                c.execute('DELETE FROM programs')
                c.execute('DELETE FROM updates')
                c.execute('UPDATE version SET major=6, minor=7, patch=1')
                self.conn.commit()
                try:
                    c.execute('VACUUM')
                except:
                    deb('Error - unable to vacuum database!')
                self.conn.commit()

            if version < [6, 7, 2]:
                ADDON.setSetting(id="ffmpeg_format", value=("mpegts"))
                ADDON.setSetting(id="ffmpeg_dis_cop_un", value=("false"))
                if PY3:
                    xbmcRootDir = xbmcvfs.translatePath('special://xbmc')
                else:
                    xbmcRootDir = xbmc.translatePath('special://xbmc')
                if os.path.isdir('/data/dalvik-cache') or os.path.isdir('/sdcard/Android') or os.path.isdir('/storage/emulated/0/Android') or '/data/data' in xbmcRootDir or '/data/user/0/' in xbmcRootDir or '/cache/apk/assets/' in xbmcRootDir:
                    deb('Detected Android system, disabling Video animation!')
                    ADDON.setSetting(id="start_video_minimalized", value=("false"))

                c.execute('UPDATE version SET major=6, minor=7, patch=2')
                self.conn.commit()

            if version < [6, 7, 3]:
                neededRestart = False
                if ADDON.getSetting('playlist_source') != '':
                    deb('setting playlist_1_source')
                    ADDON.setSetting(id="playlist_1_source", value=(ADDON.getSetting('playlist_source')))
                    ADDON.setSetting(id="playlist_source", value=(''))
                    ADDON.setSetting(id="playlist_enabled", value=(''))
                    neededRestart = True

                if ADDON.getSetting('playlist_url') != '':
                    deb('setting playlist_1_url')
                    ADDON.setSetting(id="playlist_1_url", value=(ADDON.getSetting('playlist_url')))
                    ADDON.setSetting(id="playlist_url", value=(''))
                    neededRestart = True

                if ADDON.getSetting('playlist_file') != '':
                    deb('setting playlist_1_file')
                    ADDON.setSetting(id="playlist_1_file", value=(ADDON.getSetting('playlist_file')))
                    ADDON.setSetting(id="playlist_file", value=(''))
                    neededRestart = True

                if ADDON.getSetting('playlist_high_prio_hd') != '':
                    deb('setting playlist_1_high_prio_hd')
                    ADDON.setSetting(id="playlist_1_high_prio_hd", value=(ADDON.getSetting('playlist_high_prio_hd')))
                    ADDON.setSetting(id="playlist_high_prio_hd", value=(''))
                    neededRestart = True

                if ADDON.getSetting('playlist_stop_when_starting') != '':
                    deb('setting playlist_1_stop_when_starting')
                    ADDON.setSetting(id="playlist_1_stop_when_starting", value=(ADDON.getSetting('playlist_stop_when_starting')))
                    ADDON.setSetting(id="playlist_stop_when_starting", value=(''))
                    neededRestart = True

                if ADDON.getSetting('priority_playlist') != '':
                    deb('setting playlist_1_priority')
                    ADDON.setSetting(id="playlist_1_priority", value=(ADDON.getSetting('priority_playlist')))
                    ADDON.setSetting(id="priority_playlist", value=(''))
                    neededRestart = True

                if ADDON.getSetting('priority_playlist2') != '':
                    deb('setting playlist_2_priority')
                    ADDON.setSetting(id="playlist_2_priority", value=(ADDON.getSetting('priority_playlist2')))
                    ADDON.setSetting(id="priority_playlist2", value=(''))
                    neededRestart = True

                if ADDON.getSetting('priority_playlist3') != '':
                    deb('setting playlist_3_priority')
                    ADDON.setSetting(id="playlist_3_priority", value=(ADDON.getSetting('priority_playlist3')))
                    ADDON.setSetting(id="priority_playlist3", value=(''))
                    neededRestart = True

                if ADDON.getSetting('playlist_3_enabled') == 'true':
                    ADDON.setSetting(id="nr_of_playlists", value=('3'))
                    neededRestart = True
                elif ADDON.getSetting('playlist_2_enabled') == 'true':
                    ADDON.setSetting(id="nr_of_playlists", value=('2'))
                    neededRestart = True
                elif ADDON.getSetting('playlist_1_enabled') == 'true':
                    ADDON.setSetting(id="nr_of_playlists", value=('1'))
                    neededRestart = True

                if int(ADDON.getSetting('max_wait_for_playback')) < 8:
                    ADDON.setSetting(id="max_wait_for_playback", value=('8'))
                    neededRestart = True

                c.execute('ALTER TABLE recordings ADD COLUMN start_offset INTEGER DEFAULT 0')
                c.execute('ALTER TABLE recordings ADD COLUMN end_offset INTEGER DEFAULT 0')

                c.execute('UPDATE version SET major=6, minor=7, patch=3')
                self.conn.commit()

            if version < [6, 7, 4]:
                c.execute('ALTER TABLE channels ADD COLUMN titles TEXT')
                c.execute('UPDATE version SET major=6, minor=7, patch=4')
                neededRestart = False

                self.conn.commit()

                if neededRestart:
                    deb('Required m-TVGuide restart')
                    raise RestartRequired()

            if version < [6, 7, 5]:
                c.execute('ALTER TABLE programs ADD COLUMN rating TEXT DEFAULT NULL')
                c.execute('UPDATE version SET major=6, minor=7, patch=5')
                neededRestart = False

                self.conn.commit()

                if neededRestart:
                    deb('Required m-TVGuide restart')
                    raise RestartRequired()

            if version < [6, 7, 6]:
                c.execute('ALTER TABLE custom_stream_url ADD COLUMN priority INTEGER DEFAULT 0')
                c.execute('UPDATE version SET major=6, minor=7, patch=6')
                neededRestart = False

                self.conn.commit()

                if neededRestart:
                    deb('Required m-TVGuide restart')
                    raise RestartRequired()

            if version < [6, 7, 7]:
                c.execute('CREATE TABLE IF NOT EXISTS categories(category TEXT PRIMARY KEY)')
                c.execute('ALTER TABLE categories ADD COLUMN source TEXT COLLATE NOCASE')
                c.execute('UPDATE version SET major=6, minor=7, patch=7')
                neededRestart = False

                self.conn.commit()

                if neededRestart:
                    deb('Required m-TVGuide restart')
                    raise RestartRequired()

            # make sure we have a record in sources for this Source
            c.execute('CREATE TABLE IF NOT EXISTS lastplayed(idx INTEGER, start_date TEXT, end_date TEXT, played_date TEXT)')
            c.execute("INSERT OR IGNORE INTO sources(id, channels_updated) VALUES(?, ?)", [self.source.KEY, 0])

            self.conn.commit()
            c.close()

        except sqlite3.OperationalError as ex:
            raise DatabaseSchemaException(ex)

    def updateRssDate(self, date):
        self._invokeAndBlockForResult(self._updateRssDate, date)

    def _updateRssDate(self, date):
        c = self.conn.cursor()
        c.execute("DELETE FROM rss_messages")
        try:
            c.execute("INSERT INTO rss_messages(last_message) VALUES(?)", [date])
        except:
            now = datetime.now()
            if PY3:
                date = datetime.timestamp(now)
            else:
                from time import time
                date = str(time()).split('.')[0]
            c.execute("INSERT INTO rss_messages(last_message) VALUES(?)", [date])
        self.conn.commit()
        c.close()

    def getLastRssDate(self):
        return self._invokeAndBlockForResult(self._getLastRssDate)

    def _getLastRssDate(self):
        c = self.conn.cursor()
        try:
            c.execute("SELECT last_message FROM rss_messages")
            row = c.fetchone()
        except:
            c.execute("DELETE FROM rss_messages")
            row = None
        if row:
            date = row[str('last_message')]
        else:
            date = None
        c.close()
        return date

    def addNotification(self, program, onlyOnce = False):
        self._invokeAndBlockForResult(self._addNotification, program, onlyOnce)
        # no result, but block until operation is done

    def _addNotification(self, program, onlyOnce = False):
        """
        @type program: source.program
        """
        if onlyOnce:
            programStartDate = program.startDate
        else:
            programStartDate = None
        c = self.conn.cursor()
        c.execute("INSERT INTO notifications(channel, program_title, source, start_date) VALUES(?, ?, ?, ?)", [program.channel.id, program.title, self.source.KEY, programStartDate])
        self.conn.commit()
        c.close()

    def removeNotification(self, program):
        self._invokeAndBlockForResult(self._removeNotification, program)
        # no result, but block until operation is done

    def _removeNotification(self, program):
        """
        @type program: source.program
        """
        c = self.conn.cursor()
        c.execute("DELETE FROM notifications WHERE channel=? AND program_title=? AND source=?", [program.channel.id, program.title, self.source.KEY])
        self.conn.commit()
        c.close()

    def _removeOldNotifications(self):
        debug('_removeOldNotifications')
        c = self.conn.cursor()
        c.execute("DELETE FROM notifications WHERE start_date IS NOT NULL AND start_date <= ? AND source=?", [datetime.now() - timedelta(days=1), self.source.KEY])
        self.conn.commit()
        c.close()

    def getFullNotifications(self, daysLimit = 2):
        return self._invokeAndBlockForResult(self._getFullNotifications, daysLimit)

    def _getFullNotifications(self, daysLimit):
        start = datetime.now()
        end = start + timedelta(days=daysLimit)
        programList = list()       
        c = self.conn.cursor()
        #once
        c.execute("SELECT DISTINCT c.id, c.title as channel_title,c.logo,c.stream_url,c.visible,c.weight, p.* FROM programs p, channels c, notifications a WHERE c.id = p.channel AND p.title = a.program_title AND p.start_date = p.start_date")
        for row in c:
            channel = Channel(row[str("id")], row[str("channel_title")], row[str("logo")], row[str("stream_url")], row[str("visible")], row[str("weight")])
            program = Program(channel, row[str('title')], row[str('start_date')], row[str('end_date')], row[str('description')], row[str('productionDate')], row[str('director')], row[str('actor')], row[str('episode')], row[str('rating')], row[str('image_large')], row[str('image_small')], row[str('categoryA')], row[str('categoryB')], notificationScheduled=True)
            programList.append(program)
        #always
        c.execute("SELECT DISTINCT c.id, c.title as channel_title,c.logo,c.stream_url,c.visible,c.weight, p.* FROM programs p, channels c, notifications a WHERE c.id = p.channel AND p.title = a.program_title AND p.start_date >= ? AND p.end_date <= ?", [start,end])
        #c.execute("SELECT DISTINCT c.id, c.title as channel_title,c.logo,c.stream_url,c.visible,c.weight, p.* FROM programs p, channels c, notifications a WHERE c.id = p.channel AND a.type = 1 AND p.title = a.program_title")
        for row in c:
            channel = Channel(row[str("id")], row[str("channel_title")], row[str("logo")], row[str("stream_url")], row[str("visible")], row[str("weight")])
            program = Program(channel, row[str('title')], row[str('start_date')], row[str('end_date')], row[str('description')], row[str('productionDate')], row[str('director')], row[str('actor')], row[str('episode')], row[str('rating')], row[str('image_large')], row[str('image_small')], row[str('categoryA')], row[str('categoryB')], notificationScheduled=True)
            programList.append(program)
        c.close()
        return programList

    def getNotifications(self, daysLimit = 2):
        return self._invokeAndBlockForResult(self._getNotifications, daysLimit)

    def _getNotifications(self, daysLimit):
        try:
            debug('_getNotifications')
            start = datetime.now()
            end = start + timedelta(days = daysLimit)
            c = self.conn.cursor()
            c.execute("SELECT DISTINCT c.title, p.title, p.start_date FROM notifications n, channels c, programs p WHERE n.channel = c.id AND p.channel = c.id AND n.program_title = p.title AND n.source=? AND p.start_date >= ? AND p.end_date <= ? AND (n.start_date IS NULL OR n.start_date = p.start_date)", [self.source.KEY, start, end])
            programs = c.fetchall()
            c.close()
            return programs
        except:
            self.updateFailed = True
            return

    def isNotificationRequiredForProgram(self, program):
        return self._invokeAndBlockForResult(self._isNotificationRequiredForProgram, program)

    def _isNotificationRequiredForProgram(self, program):
        """
        @type program: source.program
        """
        c = self.conn.cursor()
        c.execute("SELECT 1 FROM notifications WHERE channel=? AND program_title=? AND source=? AND (start_date IS NULL OR start_date=?)", [program.channel.id, program.title, self.source.KEY, program.startDate])
        result = c.fetchone()
        c.close()
        return result

    def clearAllNotifications(self):
        self._invokeAndBlockForResult(self._clearAllNotifications)
        # no result, but block until operation is done

    def _clearAllNotifications(self):
        c = self.conn.cursor()
        c.execute('DELETE FROM notifications')
        self.conn.commit()
        c.close()

    def addRecording(self, program, start_offset, end_offset):
        self._invokeAndBlockForResult(self._addRecording, program, start_offset, end_offset)

    def _addRecording(self, program, start_offset, end_offset):
        c = self.conn.cursor()
        c.execute("INSERT INTO recordings(channel, program_title, start_date, end_date, source, start_offset, end_offset) VALUES(?, ?, ?, ?, ?, ?, ?)", [program.channel.id, program.title, program.startDate, program.endDate, self.source.KEY, start_offset, end_offset])
        self.conn.commit()
        c.close()

    def removeRecording(self, program):
        self._invokeAndBlockForResult(self._removeRecording, program)

    def _removeRecording(self, program):
        c = self.conn.cursor()
        c.execute("DELETE FROM recordings WHERE channel=? AND program_title=? AND start_date=? AND source=?", [program.channel.id, program.title, program.startDate, self.source.KEY])
        self.conn.commit()
        c.close()

    def _removeOldRecordings(self):
        debug('_removeOldRecordings')
        c = self.conn.cursor()
        c.execute("DELETE FROM recordings WHERE end_date <= ? AND source=?", [datetime.now() - timedelta(days=1), self.source.KEY])
        self.conn.commit()
        c.close()

    def removeAllRecordings(self):
        self._invokeAndBlockForResult(self._removeAllRecordings)

    def _removeAllRecordings(self):
        debug('_removeAllRecordings')
        c = self.conn.cursor()
        c.execute('DELETE FROM recordings')
        self.conn.commit()
        c.close()

    def getFullRecordings(self, daysLimit = 2):
        return self._invokeAndBlockForResult(self._getFullRecordings, daysLimit)

    def _getFullRecordings(self, daysLimit):
        start = datetime.now()
        end = start + timedelta(days=daysLimit)
        programList = list()
        c = self.conn.cursor()
        #once
        c.execute("SELECT DISTINCT c.id, c.title as channel_title,c.logo,c.stream_url,c.visible,c.weight, p.* FROM programs p, channels c, recordings a WHERE c.id = p.channel AND p.title = a.program_title AND p.start_date = p.start_date")
        for row in c:
            channel = Channel(row[str("id")], row[str("channel_title")], row[str("logo")], row[str("stream_url")], row[str("visible")], row[str("weight")])
            program = Program(channel, row[str('title')], row[str('start_date')], row[str('end_date')], row[str('description')], row[str('productionDate')], row[str('director')], row[str('actor')], row[str('episode')], row[str('rating')], row[str('image_large')], row[str('image_small')], row[str('categoryA')], row[str('categoryB')], recordingScheduled=True)
            programList.append(program)
        #always
        c.execute("SELECT DISTINCT c.id, c.title as channel_title,c.logo,c.stream_url,c.visible,c.weight, p.* FROM programs p, channels c, recordings a WHERE c.id = p.channel AND p.title = a.program_title AND p.start_date >= ? AND p.end_date <= ?", [start,end])
        #c.execute("SELECT DISTINCT c.id, c.title as channel_title,c.logo,c.stream_url,c.visible,c.weight, p.* FROM programs p, channels c, notifications a WHERE c.id = p.channel AND a.type = 1 AND p.title = a.program_title")
        for row in c:
            channel = Channel(row[str("id")], row[str("channel_title")], row[str("logo")], row[str("stream_url")], row[str("visible")], row[str("weight")])
            program = Program(channel, row[str('title')], row[str('start_date')], row[str('end_date')], row[str('description')], row[str('productionDate')], row[str('director')], row[str('actor')], row[str('episode')], row[str('rating')], row[str('image_large')], row[str('image_small')], row[str('categoryA')], row[str('categoryB')], recordingScheduled=True)
            programList.append(program)
        c.close()
        return programList

    def getRecordings(self):
        return self._invokeAndBlockForResult(self._getRecordings)

    def _getRecordings(self):
        c = self.conn.cursor()
        c.execute("SELECT channel, program_title, start_date, end_date, start_offset, end_offset FROM recordings WHERE source=?", [self.source.KEY])
        programs = c.fetchall()
        c.close()
        return programs

    def getDbEPGSize(self):
        return self._invokeAndBlockForResult(self._getDbEPGSize)

    def _getDbEPGSize(self):
        c = self.conn.cursor()
        c.execute('SELECT * FROM updates WHERE source=?', [self.source.KEY])
        for row in c:
            size = row[str('epg_size')]
            updated = row[str('programs_updated')]
        c.close()
        return size, updated

    def clearDB(self):
        self._invokeAndBlockForResult(self._clearDB)

    def _clearDB(self):
        try:
            shutil.copyfile(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'basemap_extra.xml'), os.path.join(self.profilePath, 'basemap_extra.xml'))
        except:
            pass

        cache = os.path.join(self.profilePath, 'playlists')
        if os.path.exists(cache):
            try:
                shutil.rmtree(cache)
            except:
                pass

        c = self.conn.cursor()
        c.execute('DELETE FROM channels')
        c.execute('DELETE FROM programs')
        c.execute('DELETE FROM notifications')
        c.execute('DELETE FROM recordings')
        c.execute('DELETE FROM updates')
        c.execute('DELETE FROM sources')
        c.execute('DELETE FROM lastplayed')
        c.execute('UPDATE settings SET value=0 WHERE rowid=1')
        self.conn.commit()
        c.close()

    def deleteAllStreams(self):
        self._invokeAndBlockForResult(self._deleteAllStreams)

    def _deleteAllStreams(self):
        cache = os.path.join(self.profilePath, 'playlists')
        if os.path.exists(cache):
            try:
                shutil.rmtree(cache)
            except:
                pass

        c = self.conn.cursor()
        c.execute('DELETE FROM custom_stream_url')
        self.conn.commit()
        c.close()
        self.channelList = None

    def deleteDbFile(self):
        self._invokeAndBlockForResult(self._deleteDbFile)

    def _deleteDbFile(self):
        try:
            os.remove(self.databasePath)
            os.remove(self.databasePath + '-journal')
            os.remove(os.path.join(self.profilePath, 'skin_fonts.ini'))
        except:
            pass

        try:
            shutil.copyfile(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'basemap_extra.xml'), os.path.join(self.profilePath, 'basemap_extra.xml'))
        except:
            pass

        cache = os.path.join(self.profilePath, 'playlists')
        if os.path.exists(cache):
            try:
                shutil.rmtree(cache)
            except:
                pass

        if os.path.isfile (self.databasePath) == False:
            deb('_deleteDbFile successfully deleted database file')
        else:
            deb('_deleteDbFile failed to delete database file')

class Source(object):
    def getDataFromExternal(self, date, progress_callback = None):
        """
        Retrieve data from external as a list or iterable. Data may contain both Channel and Program objects.
        The source may choose to ignore the date parameter and return all data available.
        @param date: the date to retrieve the data for
        @param progress_callback:
        @return:
        """
        return None

    def getNewUpdateTime(self):
        return datetime.now()

    def isUpdated(self, channelsLastUpdated, programsLastUpdated, epgSize):
        today = datetime.now()
        if channelsLastUpdated is None or channelsLastUpdated.day != today.day or channelsLastUpdated.year != today.year:
            return True
        if programsLastUpdated is None or programsLastUpdated.day != today.day or programsLastUpdated.year != today.year:
            return True
        return False

    def getEpgSize(self):
        return 0

    def close(self):
        pass

    def _downloadUrl(self, url):
        from os.path import basename
        try:
            remoteFilename = ''
            deb("[EPG] Downloading epg: {}".format(url))
            start = datetime.now()
            failCounter = 0

            while True:
                try:
                    u = None

                    filename = ''
                    contentType = ''

                    headers = {
                        'User-Agent': UA,
                        'Keep-Alive': 'timeout=20',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Connection': 'Keep-Alive',
                    }

                    try:
                        http = urllib3.PoolManager()
                        u = http.request('GET', url, headers=headers, timeout=20)
                        content = u.data

                    except:
                        u = requests.get(url, headers=headers, verify=False, timeout=20)
                        content = u.content

                    content_type = u.headers.get('Content-Type', '')
                    c_disposition = u.headers.get('Content-Disposition', '')

                    filename_regex = re.compile(r'filename="(.+?)"')

                    r = filename_regex.search(c_disposition)
                    filename = r.group(1) if r else url

                    break

                except Exception as ex:
                    failCounter+=1
                    deb('_downloadUrl Error downloading url: {}, Exception: {}, failcounter: {}'.format(url, str(ex), failCounter))
                    if strings2.M_TVGUIDE_CLOSING:
                        raise SourceUpdateCanceledException()
                    if failCounter > 3:
                        raise
                    time.sleep(1)
            try:
                remoteFilename = u.headers['Content-Disposition'].split('filename=')[-1].replace('"','').replace(';','').strip()
            except:
                pass

            if url.lower().endswith('.xz') or remoteFilename.lower().endswith('.xz') or '.xz' in filename or 'xz' in content_type:
                tnow = datetime.now()
                deb("[EPG] Type: .xz, Unpacking epg: {} [{} sek.]".format(url, str((tnow-start).seconds)))
                try:
                    import lzma
                except ImportError:
                    xbmcgui.Dialog().ok(strings(57051), strings(70140).format('.xz'))
                memfile = io.BytesIO(content)
                unziped = lzma.LZMAFile(filename=memfile)
                content = unziped.read()
                unziped.close()
                memfile.close()

            elif url.lower().endswith('.gz') or remoteFilename.lower().endswith('.gz') or '.gz' in filename or 'application/x-gzip' in content_type:
                tnow = datetime.now()
                deb("[EPG] Type: .gz, Unpacking epg: {} [{} sek.]".format(url, str((tnow-start).seconds)))
                import gzip
                memfile = io.BytesIO(content)
                unziped = gzip.GzipFile(fileobj=memfile)
                content = unziped.read()
                unziped.close()
                memfile.close()

            elif url.lower().endswith('.zip') or remoteFilename.lower().endswith('.zip') or '.zip' in filename:
                tnow = datetime.now()
                deb("[EPG] Type: .zip, Unpacking epg: {} [{} sek.]".format(url, str((tnow-start).seconds)))
                memfile = io.BytesIO(content)
                unziped = zipfile.ZipFile(memfile)
                content = unziped.read(unziped.namelist()[0])
                unziped.close()
                memfile.close()

            elif url.lower().endswith('.bz2') or remoteFilename.lower().endswith('.bz2') or '.bz2' in filename:
                tnow = datetime.now()
                deb("[EPG] Type: .bz2, Unpacking epg: {} [{} sek.]".format(url, str((tnow-start).seconds)))
                import bz2
                memfile = io.BytesIO(content)
                memfile.seek(0)
                unziped = bz2.decompress(memfile.read())
                content = unziped
                memfile.close()

            u.close()
            tnow = datetime.now()
            deb("[EPG] Downloading done [{} sek.]".format(str((tnow-start).seconds)))


            if not b'<channel' in content:
                deb('Detected not valid EPG XML, url: {}'.format(url))
                try:
                    deb('Faulty EPG content: {}'.format(str(content[:15000])))
                except:
                    deb('Faulty EPG content: {}'.format(str(content[:15000]).decode('utf-8')))

                #not a valid EPG XML
                deb("Error downloading EPG: {}\n\nDetails:\n{}".format(url, getExceptionString()))
                raise SourceFaultyEPGException(url)

            return content

        except SourceUpdateCanceledException as cancelException:
            raise cancelException

        except Exception as ex:
            tnow = datetime.now()
            deb("[EPG] Downloading error [{} sek.]".format(str((tnow-start).seconds)))
            raise Exception ('Error in _downloadUrl: \n{}'.format(getExceptionString()))

class XMLTVSource(Source):
    KEY = '0'
    def __init__(self, addon):
        self.logoFolder = addon.getSetting('xmltv_logo_folder')
        self.xmltvFile = addon.getSetting('xmltv_file')

        if not self.xmltvFile or not xbmcvfs.exists(self.xmltvFile):
            raise SourceNotConfiguredException()

    def getDataFromExternal(self, date, progress_callback = None):
        start = datetime.now()

        filename = self.xmltvFile

        zone, autozone, local = getTimeZone()

        if self.xmltvFile.lower().endswith('.xml'):
            f = FileWrapper(filename)
            context = ElementTree.iterparse(f, events=("start", "end"))
            return parseXMLTV(context=context, f=f, size=f.size, progress_callback=progress_callback, zone=zone, autozone=autozone, local=local, logoFolder=self.logoFolder)

        else:
            with open(filename, 'rb') as file:
                if filename.lower().endswith('.xz') or '.xz' in filename:
                    tnow = datetime.now()
                    deb("[EPG] Type: .xz, Unpacking epg: {} [{} sek.]".format(filename, str((tnow-start).seconds)))
                    try:
                        import lzma
                    except ImportError:
                        from backports import lzma
                    memfile = io.BytesIO(file.read())
                    unziped = lzma.LZMAFile(filename=memfile)
                    content = unziped.read()
                    unziped.close()
                    memfile.close()

                elif filename.lower().endswith('.gz') or '.gz' in filename:
                    tnow = datetime.now()
                    deb("[EPG] Type: .gz, Unpacking epg: {} [{} sek.]".format(filename, str((tnow-start).seconds)))
                    import gzip
                    memfile = io.BytesIO(file.read())
                    unziped = gzip.GzipFile(fileobj=memfile)
                    content = unziped.read()
                    unziped.close()
                    memfile.close()

                elif filename.lower().endswith('.zip') or '.zip' in filename:
                    tnow = datetime.now()
                    deb("[EPG] Type: .zip, Unpacking epg: {} [{} sek.]".format(filename, str((tnow-start).seconds)))
                    memfile = io.BytesIO(file.read())
                    unziped = zipfile.ZipFile(memfile)
                    content = unziped.read(unziped.namelist()[0])
                    unziped.close()
                    memfile.close()

                elif filename.lower().endswith('.bz2') or '.bz2' in filename:
                    tnow = datetime.now()
                    deb("[EPG] Type: .bz2, Unpacking epg: {} [{} sek.]".format(filename, str((tnow-start).seconds)))
                    import bz2
                    memfile = io.BytesIO(file.read())
                    memfile.seek(0)
                    unziped = bz2.decompress(memfile.read())
                    content = unziped
                    memfile.close()

                iob = io.BytesIO(content)
                context = ElementTree.iterparse(iob, events=("start", "end"))
                return parseXMLTV(context=context, f=iob, size=len(content), progress_callback=progress_callback, zone=zone, autozone=autozone, local=local, logoFolder=self.logoFolder)

    def isUpdated(self, channelsLastUpdated, programLastUpdate, epgSize):
        if channelsLastUpdated is None or not xbmcvfs.exists(self.xmltvFile):
            return True
        stat = xbmcvfs.Stat(self.xmltvFile)
        fileUpdated = datetime.fromtimestamp(stat.st_mtime())
        return fileUpdated > channelsLastUpdated

class MTVGUIDESource(Source):
    KEY = '1'
    def __init__(self, addon):
        self.MTVGUIDEUrl       = ADDON.getSetting('m-TVGuide').strip()
        self.MTVGUIDEUrl2      = ADDON.getSetting('m-TVGuide2').strip()
        self.MTVGUIDEUrl3      = ADDON.getSetting('m-TVGuide3').strip()

        self.XXX_EPG_Url       = ADDON.getSetting('XXX_EPG').strip()
        if self.XXX_EPG_Url == 'true':
            ADDON.setSetting('XXX_EPG', M_TVGUIDE_SUPPORT + 'freeepg/xxx.xml')
        elif self.XXX_EPG_Url == 'false':
            ADDON.setSetting('XXX_EPG', '')

        self.VOD_EPG_Url       = ADDON.getSetting('VOD_EPG').strip()
        if self.VOD_EPG_Url == 'true':
            ADDON.setSetting('VOD_EPG', M_TVGUIDE_SUPPORT + 'freeepg/vod.xml')
        elif self.VOD_EPG_Url == 'false':
            ADDON.setSetting('VOD_EPG', '')

        self.epgBasedOnLastModDate = ADDON.getSetting('UpdateEPGOnModifiedDate')
        self.logoFolder = ADDON.getSetting('xmltv_logo_folder')
        self.EPGSize    = None
        self.timer      = None

        if PY3:
            try:
                self.profilePath  = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
            except:
                self.profilePath  = xbmcvfs.translatePath(ADDON.getAddonInfo('profile')).decode('utf-8')
        else:
            try:
                self.profilePath  = xbmc.translatePath(ADDON.getAddonInfo('profile'))
            except:
                self.profilePath  = xbmc.translatePath(ADDON.getAddonInfo('profile')).decode('utf-8')

    def check_url(self, url):
        return bool(re.match(
            r"(https?|ftp)://"
            r"(\w+(\-\w+)*\.)?"
            r"((\w+(\-\w+)*)\.(\w+))"
            r"(\.\w+)*"
            r"([\w\-\._\~/]*)*(?<!\.)", url))

    def getDataFromExternal(self, date, progress_callback = None):
        parsedData = {}

        errorList = []

        mainEpgs = [self.MTVGUIDEUrl2, self.MTVGUIDEUrl3] + EPG_LIST
        extraEpgs = [self.XXX_EPG_Url, self.VOD_EPG_Url]

        if self.check_url(self.MTVGUIDEUrl):
            if not strings2.M_TVGUIDE_CLOSING:
                parsedData.update({self.MTVGUIDEUrl:{'date': date}})
        else:
            raise SourceFaultyEPGException(self.MTVGUIDEUrl)

        try:
            if CUSTOM_PARSER:
                for epg in mainEpgs:
                    if self.check_url(epg) and not strings2.M_TVGUIDE_CLOSING:
                        parsedData.update({epg:{'date': date}})
                    else:
                        errorList.append(epg)

                for epg in extraEpgs:
                    if self.check_url(epg) and epg != 'false' and not strings2.M_TVGUIDE_CLOSING:
                        parsedData.update({epg:{'date': date}})
                    else:
                        if epg != 'false':
                            errorList.append(epg)

                data = self._getDataFromExternal(data=parsedData, progress_callback=progress_callback)

            else:
                data = self._getDataFromExternal(date=date, progress_callback=progress_callback, url=self.MTVGUIDEUrl)

                for epg in mainEpgs:
                    if self.check_url(epg) and not strings2.M_TVGUIDE_CLOSING:
                        parsedData_etree = self._getDataFromExternal(date=date, progress_callback=progress_callback, url=epg)
                        data = chain(data, parsedData_etree)
                    else:
                        errorList.append(epg)

                for epg in extraEpgs:
                    if self.check_url(epg) and epg != 'false' and not strings2.M_TVGUIDE_CLOSING:
                        parsedData_etree = self._getDataFromExternal(date=date, progress_callback=progress_callback, url=epg)
                        data = chain(data, parsedData_etree)
                    else:
                        if epg != 'false':
                            errorList.append(epg)

            errorList = filter(lambda x: len(x) > 0, errorList)

            error_str = ', '.join(errorList)
            if error_str.strip() != '':
                raise SourceFaultyEPGException(error_str)

        except SourceFaultyEPGException as ex:
            deb("Failed to download custom EPG but addon should start!, EPG: {}".format(ex.epg))

            adultEPG = M_TVGUIDE_SUPPORT + 'freeepg/xxx.xml'
            vodEPG = M_TVGUIDE_SUPPORT + 'freeepg/vod.xml'

            epgTitle = strings(LOAD_ERROR_LINE1) + '\n' + ex.epg + '\n' + strings(LOAD_NOT_CRITICAL_ERROR)
            if ex.epg == adultEPG:
                res = requests.get(adultEPG, timeout=5)
                status = res.status_code
                title = 'Adult XXX EPG'

                epgTitle = strings(30170).format(title, status)

            elif ex.epg == vodEPG:
                res = requests.get(vodEPG, timeout=5)
                status = res.status_code
                title = 'VOD EPG'

                epgTitle = strings(30170).format(title, status)

            xbmcgui.Dialog().ok(strings(LOAD_ERROR_TITLE), epgTitle)

            parsedDataEx = {}

            if self.check_url(self.MTVGUIDEUrl):
                if not strings2.M_TVGUIDE_CLOSING:
                    parsedDataEx.update({self.MTVGUIDEUrl:{'date': date}})
                    data = self._getDataFromExternal(data=parsedDataEx, progress_callback=progress_callback)
            else:
                raise SourceFaultyEPGException(self.MTVGUIDEUrl)

        return data

    def _getDataFromExternal(self, date=None, url=None, data=None, progress_callback=None):
        xml = b''

        if data:
            for url, v in data.items():
                date = v['date']

                try:
                    xml += bytearray(self._downloadUrl(url))

                except SourceUpdateCanceledException as cancelException:
                    raise cancelException

                except Exception as ex:
                    deb("Error downloading EPG: {}\n\nDetails:\n{}".format(url, getExceptionString()))
                    raise SourceFaultyEPGException(url)

        else:
            try:
                xml = self._downloadUrl(url)

            except SourceUpdateCanceledException as cancelException:
                    raise cancelException

            except Exception as ex:
                deb("Error downloading EPG: {}\n\nDetails:\n{}".format(url, getExceptionString()))
                raise SourceFaultyEPGException(url)

        if strings2.M_TVGUIDE_CLOSING:
            raise SourceUpdateCanceledException()

        zone, autozone, local = getTimeZone()

        try:        
            if CUSTOM_PARSER:
                return customParseXMLTV(xml=xml.decode('utf-8'), progress_callback=progress_callback, zone=zone, autozone=autozone, local=local, logoFolder=self.logoFolder)

            else:
                iob = io.BytesIO(xml)

                context = ElementTree.iterparse(iob, events=("start", "end"))
                return parseXMLTV(context=context, f=iob, size=len(xml), progress_callback=progress_callback, zone=zone, autozone=autozone, local=local, logoFolder=self.logoFolder)

        except SourceUpdateCanceledException as cancelException:
            raise cancelException

        except Exception as ex:
            deb("Error downloading EPG: {}\n\nDetails:\n{}".format(url, getExceptionString()))
            raise SourceFaultyEPGException(url)

    def isUpdated(self, channelsLastUpdated, programLastUpdate, epgSizeInDB):
        if self.epgBasedOnLastModDate == 'false':
            return super(MTVGUIDESource, self).isUpdated(channelsLastUpdated, programLastUpdate, epgSizeInDB)
        if channelsLastUpdated is None or programLastUpdate is None or epgSizeInDB == 0:
            return True
        epgSize = self.getEpgSize(epgSizeInDB)
        if epgSize == '' or epgSize is None:
            epgSize = 0

        if int(epgSize) != int(epgSizeInDB):
            debug('[UPD] isUpdated detected new EPG! size in DB is: {}, on server: {}'.format(epgSizeInDB, epgSize))
            return True
        return False

    def getEpgSize(self, defaultSize = 0, forceCheck = False):
        if not self.check_url(self.MTVGUIDEUrl):
            return 0
        if self.epgBasedOnLastModDate == 'false':
            return 0
        if self.EPGSize is not None and forceCheck == False:
            return self.EPGSize
        epgRecheckTimeout = 900
        failedCounter = 0
        while failedCounter < 3:
            try:
                headers = {'User-Agent': UA,
                            'Keep-Alive': 'timeout=20',
                            'ContentType': 'application/x-www-form-urlencoded',
                            'Connection': 'Keep-Alive',
                            }

                response = requests.get(self.MTVGUIDEUrl, headers=headers, verify=False, timeout=10)

                try:
                    new_size = int(response.headers['Content-Length'].strip())
                    deb('[UPD] getEpgSize Content-Length: {}'.format(new_size))
                except:
                    new_size = 0

                if new_size <= 0:
                    data = response.content
                    new_size = len(data)
                    deb('[UPD] getEpgSize Content: {}'.format(new_size))

                #if new_size < 10000:
                    #raise Exception('getEpgSize too smal EPG size received: {}'.format(new_size))

                self.EPGSize = new_size
                break
            except Exception as ex:
                deb('[UPD] getEpgSize exception {} failedCounter {}'.format(str(ex), failedCounter))
                failedCounter = failedCounter + 1
                time.sleep(0.1)

        if self.EPGSize == 0:
            self.EPGSize = defaultSize
            epgRecheckTimeout = 600 #recheck in 10 min
        #This will force checking for updates every 1h
        self.timer = threading.Timer(epgRecheckTimeout, self.resetEpgSize)
        self.timer.start()
        return self.EPGSize

    def resetEpgSize(self):
        debug('[UPD] resetEpgSize')
        self.EPGSize = self.getEpgSize(self.EPGSize, forceCheck=True)

    def close(self):
        if self.timer and self.timer.is_alive():
            self.timer.cancel()

def catList(category_count):
    cleanup_regex = re.compile(r'[!"”#$%&’()*+,-.\/:;<>?@\[\]^_`{|}~]|ADDON.*|^\s', re.IGNORECASE)

    categoriesList = []

    for c in sorted(category_count):
        if c is not None or c != '':
            s = "{}={}\n".format(c, category_count[c])
            s = cleanup_regex.sub('', s)
            s = re.sub(r'(^|\s)(\S)', lambda m: m.group(1) + m.group(2).upper(), s)

            if s.strip() != '':
                categoriesList.append(s.strip())

    if PY3:
        file_name = os.path.join(PROFILE_PATH, 'category_count.list')
        with open(file_name, 'w+', encoding='utf-8') as f:
            for line in categoriesList:
                f.write('{}\n'.format(line))
    else:
        file_name = os.path.join(PROFILE_PATH, 'category_count.list')
        with codecs.open(file_name, 'w+', encoding='utf-8') as f:
            for line in categoriesList:
                f.write('{}\n'.format(line))

def getTimeZone():
    ZONE = ADDON.getSetting('time_zone')

    ADJUST_LOCAL_TIME = ADDON.getSetting('adjust_local_time')
    if ADJUST_LOCAL_TIME == 'true':
        LOCAL_TIME = True
    else:
        LOCAL_TIME = False

    ZONE_CONFIG = ADDON.getSetting('auto_time_zone')
    if ZONE_CONFIG == 'true':
        TIME_ZONE_AUTO = True
    else:
        TIME_ZONE_AUTO = False

    return ZONE, TIME_ZONE_AUTO, LOCAL_TIME

def prepareTimeZone(zone, autozone, local):
    """
    Prepare timezone data to avoid do it in every loop step.

    `zone`     - EPG timezone, used if not `autozone`
    `autozone` - parse timezone from EPG if true
    `local`    – force local timezone for UTC, used if not `autozone`
    """

    if autozone:
        if local:
            # adjust for summertime
            if PY3:
                local = datetime.now(timezone.utc).astimezone().utcoffset()
            else:
                local = datetime.now() - datetime.utcnow()
        else:
            local = None
        zone = None

    elif zone:
        if zone == '00:00':
            zone = timedelta(hours=0)
        else:
            zone = timedelta(minutes=int(zone[:3]) * 60 + int(zone[-2:]))

    return zone, autozone, local


def parseTvDate(dateString, zone, autozone, local):
    """
    Parse date-time. Options must be prepared by prepareTimeZone().
    `zone`     - EPG timezone, used if not `autozone`
    `autozone` - parse timezone from EPG if true
    `local`    – local timezone to force for UTC, used if `autozone`
    """
    dateString, _, zoneString = dateString.partition(' ')

    offset = None
    if zoneString:
        offset = timedelta(minutes=int(zoneString[:3]) * 60 + int(zoneString[-2:]))
    elif local and autozone:
        offset = local - timedelta(hours=1)

    dt = datetime(*(int(dateString[i:i+2 if i else i+4]) for i in (0, 4, 6, 8, 10, 12)))
    if zone:
        offset = zone
    elif local and offset == parseTvDate.utc:
        offset = local
    if offset:
        dt += offset  # apply timezone offset
    return dt


parseTvDate.utc = timedelta()


def customParseXMLTV(xml, progress_callback, zone, autozone, local, logoFolder):
    def retimezone(text, regex, group=1, default=''):
        try:
            return parseTvDate(regex.search(text).group(group), *tzargs)
        except Exception as ex:
            deb('TimeZone Exception: {}'.format(ex))
            return default

    def progress(result):
        elements_parsed[0] += 1
        if elements_parsed[0] % 500 == 0:
            if strings2.M_TVGUIDE_CLOSING:
                raise SourceUpdateCanceledException()
            if progress_callback:
                if not progress_callback((elements_parsed[0] / float(totalElement)) * 100.0):
                    raise SourceUpdateCanceledException()
        return result

    def process_prog(program, category=None):
        r = programChannelRe.search(program)
        channel = r.group(1).upper() if r else ''

        r = programTitleRe.search(program)
        title = r.group(1) if r else ''

        categories = programCategory.findall(program)
        if category is not None:
            categories.insert(0, category)

        category_count.update(categories)
        categoryA, categoryB = (categories + ['', ''])[:2]

        start = retimezone(program, programStartRe)
        stop = retimezone(program, programStopRe)

        r = programDesc.search(program)
        desc = r.group(1) if r else ''

        r = programProdDate.search(program)
        live = r and r.group(1) or ''
        date = r and r.group(2) or ''

        r = programDirector.search(program)
        director = r.group(1) if r else ''

        r = programActor.search(program)
        actor = r.group(1) if r else ''

        r = programIcon.search(program)
        icon = r.group(1) if r else None

        r = programEpisode.search(program)
        episode = r.group(1) if r else ''
        if episode != '':
            r = progEpisodeNumRe.search(episode)
            episode = r.group(1) if r else ''

        r = programRating.search(program)
        rating = r.group(1) if r else ''

        program = None
        return Program(channel=channel, title=title, startDate=start, endDate=stop, description=desc,
                       productionDate=date, director=director, actor=actor, episode=episode, rating=rating,
                       imageLarge=live, imageSmall=icon, categoryA=categoryA, categoryB=categoryB)

    deb("[EPG] Parsing EPG by custom parser")
    startTime = datetime.now()
    tzargs = prepareTimeZone(zone, autozone, local)

    #regex for channel
    channelRe        = re.compile(r'(<channel.*?</channel>)',                re.DOTALL)
    channelIdRe      = re.compile(r'<channel\s*id="(.*?)">',                 re.DOTALL)
    channelTitleRe   = re.compile(r'<(?:display-)?name.*?>(.*?)</(?:display-)?name>',  re.DOTALL)
    channelIconRe    = re.compile(r'<icon\s*src="(.*?)"',                    re.DOTALL)

    #regex for program
    programPattern   = r'(?P<program_outer><(?:programme|prog).*?</(?:programme|prog>)>)'
    mainNodeRe       = re.compile(r'<category[^>]*?(:?category="(?P<category>[^"]*)")?.*?>(?P<category_inner>.*?)</category>|%s' % programPattern, re.DOTALL)
    programRe        = re.compile(programPattern,                            re.DOTALL)
    programChannelRe = re.compile(r'channel="(.*?)"',                        re.DOTALL)
    programTitleRe   = re.compile(r'<title.*?>(.*?)</title>',                re.DOTALL)
    programStartRe   = re.compile(r'start="(.*?)"',                          re.DOTALL)
    programStopRe    = re.compile(r'stop="(.*?)"',                           re.DOTALL)
    programDesc      = re.compile(r'<desc.*?>(.*?)</desc>',                  re.DOTALL)
    programIcon      = re.compile(r'<icon\s*src="(.*?)"',                    re.DOTALL)
    programCategory  = re.compile(r'<category.*?>(.*?)</category>',          re.DOTALL)
    programProdDate  = re.compile(r'<date.*?>(?:(live)|(.*?))</date>',       re.DOTALL)
    programDirector  = re.compile(r'<director.*?>(.*?)</director>',          re.DOTALL)
    programActor     = re.compile(r'<actor.*?>(.*?)</actor>',                re.DOTALL)
    programEpisode   = re.compile(r'<episode-num.*?>(.*?)</episode-num>',    re.DOTALL)
    programRating    = re.compile(r'<rating.*?>\s*<value>(.*?)<\/value>\s*<\/rating>', re.DOTALL | re.MULTILINE)
    programLive      = re.compile(r'<date.*?>(live)</date>',                 re.DOTALL)
    progEpisodeNumRe = re.compile(r'([*S|E]((S)?(\d{1,3})?\s*((E)?\d{1,5}(\/\d{1,5})?)))')

    #replace &amp; with & and Carriage Return (CR) in xml
    xml = xml.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('\r', '')

    channels = channelRe.findall(xml)
    if len(channels) == 0:
        deb('Error, no channels in EPG!')
        deb('Part of faulty EPG content without channels: {}'.format(str(xml[:15000])))
        raise SourceFaultyEPGException('')

    titles = None

    for channel in channels:
        r = channelIdRe.search(channel)
        id = r.group(1).upper() if r else ''

        r = channelTitleRe.search(channel)
        title = r.group(1) if r else ''
        if title == '':
            title = id

        if CH_DISP_NAME:
            titleList = channelTitleRe.findall(channel)
            titles = ', '.join([elem.upper() for elem in titleList])
            if titles == '':
                titles = title

        logo = None

        if logoFolder:
            logoFile = os.path.join(logoFolder, title.replace(' ', '_').lower() + '.png')
            if xbmcvfs.exists(logoFile):
                logo = logoFile

        if not logo:
            r = channelIconRe.search(channel)
            logo = r.group(1) if r else None

        channel = None
        yield Channel(id, title, logo, titles)

    if strings2.M_TVGUIDE_CLOSING:
        raise SourceUpdateCanceledException()

    del channels[:]
    elements_parsed = [0]
    category_count = Counter()
    programs = []  # (program_outer, category_name)
    for node in mainNodeRe.finditer(xml):
        category_inner = node.group('category_inner')
        if category_inner is not None:
            for subnode in programRe.finditer(category_inner):
                programs.append((subnode.group('program_outer'), node.group('category')))
        program_outer = node.group('program_outer')
        if program_outer is not None:
            programs.append((program_outer, None))

    del xml
    totalElement = len(programs)
    for program, category in programs:
        yield progress(process_prog(program, category=category))

    tnow = datetime.now()
    deb("[EPG] Parsing EPG by custom parser is done [{} sek.]".format(str((tnow-startTime).seconds)))

    thread = threading.Thread(name='catList', target=catList, args=[category_count])
    thread.start()


def parseXMLTV(context, f, size, progress_callback, zone, autozone, local, logoFolder):
    def progress(result):
        elements_parsed[0] += 1
        if elements_parsed[0] % 500 == 0:
            if strings2.M_TVGUIDE_CLOSING:
                raise SourceUpdateCanceledException()
            if progress_callback:
                if not progress_callback(100.0 / size * f.tell()):
                    raise SourceUpdateCanceledException()
        return result

    def process_prog(elem, category=None):
        channel = elem.get("channel", "").upper()
        description = elem.findtext("desc")
        date = elem.findtext("date")
        director = elem.findtext("director")
        actor = elem.findtext("actor")
        episode = elem.findtext("episode-num")
        iconElement = elem.findtext("sub-title")
        categories = [node.text for node in elem.findall("category")]
        if category is not None:
            categories.insert(0, category)
        category_count.update(categories)
        categoryA, categoryB = (categories + ['', ''])[:2]

        value = ''
        rating = elem.findtext("rating")
        if rating is not None:
            for ele in elem:
                get_value = ele.findtext("value")
                if get_value is not None:
                    value = get_value

        live = ''
        if date == 'live':
            live = date

        progEpisodeNumRe = re.compile(r'([*S|E]((S)?(\d{1,3})?\s*((E)?\d{1,5}(\/\d{1,5})?)))')

        if episode:
            r = progEpisodeNumRe.search(episode)
            episode = r.group(1) if r else ''

        icon = None

        if iconElement is not None:
            icon = iconElement
        else:
            iconElementEx = elem.find("icon")
            if iconElementEx is not None:
                icon = iconElementEx.get("src")

        if not description:
            description = strings(NO_DESCRIPTION)

        try:
            start = parseTvDate(elem.get('start'), *tzargs)
        except Exception as ex:
            deb('TimeZone Exception: {}'.format(ex))
            start = ''

        try:
            stop = parseTvDate(elem.get('stop'), *tzargs)
        except Exception as ex:
            deb('TimeZone Exception: {}'.format(ex))
            stop = ''

        return Program(channel, elem.findtext('title'), start, stop, description, productionDate=date,
                       director=director, actor=actor, episode=episode, rating=value, imageLarge=live, imageSmall=icon,
                       categoryA=categoryA, categoryB=categoryB)

    deb("[EPG] Parsing EPG")
    start = datetime.now()
    tzargs = prepareTimeZone(zone, autozone, local)

    if PY3:
        event, root = next(context)
    else:
        event, root = context.next()
    elements_parsed = [0]
    category_count = Counter()

    titles = None

    for event, elem in context:
        if event == "end":
            if elem.tag in ("programme", "prog"):
                # single <programme/>
                yield progress(process_prog(elem))
            elif elem.tag == "category":
                category = elem.get('category')
                for node in elem:
                    if elem.tag in ("programme", "prog"):
                        # <programme/> in <category/>
                        yield progress(process_prog(elem, category))
            elif elem.tag == "channel":
                id = elem.get("id").upper()

                if CH_DISP_NAME:
                    titleList = chain(elem.findall("display-name"), elem.findall("name"))
                    titles = ', '.join([x.text.upper() for x in titleList])

                title = elem.findtext("name") or elem.findtext("display-name") or ''

                if title == "":
                    title = id

                logo = None

                if logoFolder:
                    logoFile = os.path.join(logoFolder, title.replace(' ', '_').lower() + '.png')
                    if xbmcvfs.exists(logoFile):
                        logo = logoFile

                if not logo:
                    iconElement = elem.find("icon")
                    if iconElement is not None:
                        logo = iconElement.get("src")

                yield progress(Channel(id, title, logo, titles))

        root.clear()
    f.close()

    del context

    tnow = datetime.now()
    deb("[EPG] Parsing EPG is done [{} sek.]".format(str((tnow-start).seconds)))

    thread = threading.Thread(name='catList', target = catList, args=[category_count])
    thread.start()

class FileWrapper(object):
    def __init__(self, filename):
        self.vfsfile = xbmcvfs.File(filename, 'rb')
        self.size = self.vfsfile.size()
        self.bytesRead = 0
    def close(self):
        self.vfsfile.close()
    def read(self, bytes):
        self.bytesRead += bytes
        if PY3:
            return self.vfsfile.read()
        else:
            return self.vfsfile.read(bytes)
    def tell(self):
        return self.bytesRead

def instantiateSource():
    SOURCES = {
    '0' : XMLTVSource,
    '1' : MTVGUIDESource
    }

    try:
        activeSource = SOURCES[GET_SOURCE]
    except KeyError:
        activeSource = SOURCES['1']
    return activeSource(ADDON)

class RssFeed(object):
    def __init__(self, url, last_message, update_date_call):
        self.dateFormat = '%d.%m.%Y_%H:%M:%S'
        deb('RssFeed __init__ url: {}, File format: \"{} MESSAGE\"'.format(url, self.dateFormat) )
        self.updateInterval = 1200 # check every 20m
        self.rssUrl = url
        self.closing = False
        self.lastPrintedMessageInDB = last_message
        self.updateDbCall = update_date_call
        self.downloader = serviceLib.ShowList(deb)
        self.timer = threading.Timer(0, self.checkForUpdates)
        self.timer.start()

    def checkForUpdates(self):
        debug('RssFeed checkForUpdates')

        UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36 Edg/98.0.1108.50'
        customHeaders = {
            'User-Agent' : UA, 
            'Connection' : 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        for url in self.rssUrl:
            if 'mods-kodi.pl' in url:
                rssData = self.downloader.getJsonFromExtendedAPI(url, customHeaders=customHeaders)
            else:
                rssData = self.downloader.getJsonFromExtendedAPI(url)

            try:
                rssData = rssData.decode('utf-8')
            except:
                pass

            if rssData is not None:
                for line in reversed(rssData.split('\n')):
                    strippedLine = line.strip()
                    if len(strippedLine) == 0:
                        continue
                    try:
                        #strippedLine = strippedLine.decode('iso-8859-2')
                        message = re.search(".*?([_.0-9:]*)(.*)", strippedLine)
                        dateStr = message.group(1).strip()
                        messageStr = message.group(2).strip()
                        t = time.strptime(dateStr, self.dateFormat)
                        messageDate = datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)

                        if (not self.lastPrintedMessageInDB or messageDate > self.lastPrintedMessageInDB) and len(messageStr) > 0 and messageDate < datetime.now() + timedelta(days=1):
                            deb('RssFeed News: {}'.format(messageStr))
                            xbmcgui.Dialog().ok(strings(RSS_MESSAGE), "\n" + messageStr )
                            self.lastPrintedMessageInDB = messageDate
                            self.updateDbCall(self.lastPrintedMessageInDB)
                    except Exception as ex:
                        deb('RssFeed checkForUpdates Error: {}'.format(getExceptionString()))

        if not self.closing:
            self.timer = threading.Timer(self.updateInterval, self.checkForUpdates)
            self.timer.start()

    def close(self):
        self.closing = True
        self.timer.cancel()