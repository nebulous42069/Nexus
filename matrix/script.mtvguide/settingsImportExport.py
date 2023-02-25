#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   GNU General Public License

#   m-TVGuide KODI Addon
#   Copyright (C) 2021 Mariusz89B
#   Copyright (C) 2021 mbebe
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

if PY3:
    import urllib.request, urllib.parse, urllib.error,  http.client
else:
    import urllib, urllib2, httplib

import os, stat, io, zipfile, datetime, shutil, platform, re
import xbmc, xbmcgui, xbmcvfs
from strings import *
from groups import *

compressionType = zipfile.ZIP_STORED
try:
    compressionType = zipfile.ZIP_DEFLATED
except:
    pass

#import gzip
import collections

dbFileName          = 'source.db'
settingsFileName    = 'settings.xml'
categoriesFileName  = 'categories.ini'
WINDOWS_OS_NAME     = 'Windows'
ANDROID_OS_NAME     = 'Android'
MAC_OS_NAME         = 'MacOS'
COREELEC_OS_NAME    = 'CoreELEC / LibreELEC'
LINUX_OS_NAME       = 'Linux'
OSMC_OS_NAME        = 'OSMC'
OTHER_OS_NAME       = 'Other'

recordAppWindows    = M_TVGUIDE_SUPPORT + 'record_apps/recording_windows.zip'
recordAppAndroid    = M_TVGUIDE_SUPPORT + 'record_apps/recording_android.zip'
recordAppMacOS      = M_TVGUIDE_SUPPORT + 'record_apps/recording_macos.zip'

adultEPG            = M_TVGUIDE_SUPPORT + 'freeepg/xxx.xml'
vodEPG              = M_TVGUIDE_SUPPORT + 'freeepg/vod.xml'

CC_DICT = ccDict()

class SettingsImp:
    def __init__(self):
        try:
            try:
                self.profilePath  = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
            except:
                self.profilePath  = xbmcvfs.translatePath(ADDON.getAddonInfo('profile')).decode('utf-8')
        except:
            try:
                self.profilePath  = xbmc.translatePath(ADDON.getAddonInfo('profile'))
            except:
                self.profilePath  = xbmc.translatePath(ADDON.getAddonInfo('profile')).decode('utf-8')

        try:
            self.command = sys.argv[1]
        except:
            self.command = None
        if self.command is None or self.command == '':
            return
        deb('SettingsImp __init__ command %s' % self.command)
        if self.command == 'Import':
            self.importSettings()
        elif self.command == 'Export':
            self.exportSettings()
        elif self.command == 'ImportRecordApp':
            try:
                recordApp = sys.argv[2]
            except:
                recordApp = None
            self.importRecordApp(recordApp)
        elif self.command == 'DownloadRecordAppFromModsKodi':
            self.downloadRecordApp()
        elif self.command == 'Adult':
            self.adultPicker()
        elif self.command == 'Vod':
            self.vodPicker()
        elif self.command == 'CountryUrl':
            self.countryUrlPicker()
        elif self.command == 'CountryFile':
            self.countryFilePicker()

    def exportSettings(self):
        success = False
        try:
            dirname = xbmcgui.Dialog().browseSingle(type=3, heading=strings(58001), shares='files')
        except:
            dirname = xbmcgui.Dialog().browseSingle(type=3, heading=strings(58001).encode('utf-8'), shares='files')
        filename = 'm-TVGuide_backup_' + str(datetime.datetime.now().strftime('%Y-%m-%d')) + '.zip'
        if dirname is not None and dirname != '':
            if not os.path.isdir(self.profilePath):
                try:
                    xbmcgui.Dialog().ok(strings(58002),'\n' + strings(58004))
                except:
                    xbmcgui.Dialog().ok(strings(58002).encode('utf-8'),'\n' + strings(58004).encode('utf-8'))
                return success

            deb('SettingsImp exportSettings to file {}'.format(os.path.join(dirname, filename)))
            try:
                with zipfile.ZipFile(os.path.join(dirname, filename), mode='w', compression=compressionType) as zf:
                    for fileN in [ dbFileName, settingsFileName, categoriesFileName ]:
                        if os.path.isfile(os.path.join(self.profilePath, fileN)):
                            zf.write(os.path.join(self.profilePath, fileN), fileN)
                            success = True

            except:
                deb('Exporting to ZIP failed with error: {} \n trying to copy files'.format(getExceptionString()))
                success = False
                try:
                    os.remove(os.path.join(dirname, filename))
                except:
                    pass
                dest_dir = os.path.join(dirname, filename).replace('.zip', '')
                if not os.path.isdir(dest_dir):
                    if PY3:
                        os.makedirs(dest_dir, exist_ok=True)
                    else:
                        os.makedirs(dest_dir)
                for fileN in [ dbFileName, settingsFileName ]:
                    if os.path.isfile(os.path.join(self.profilePath, fileN)):
                        shutil.copy2(os.path.join(self.profilePath, fileN), dest_dir)
                        success = True
                deb('Settings exported as separate files')

            if success:
                try:
                    xbmcgui.Dialog().ok(strings(58002),'\n' + strings(58005))
                except:
                    xbmcgui.Dialog().ok(strings(58002).encode('utf-8'),'\n' + strings(58005).encode('utf-8'))
            else:
                try:
                    xbmcgui.Dialog().ok(strings(58002),'\n' + strings(58006))
                except:
                    xbmcgui.Dialog().ok(strings(58002).encode('utf-8'),'\n' + strings(58006).encode('utf-8'))
        return success

    def importSettings(self):
        success = False
        try:
            filename = xbmcgui.Dialog().browseSingle(type=1, heading=strings(58007), shares='files', mask='.zip|settings.xml|source.db')
        except:
            filename = xbmcgui.Dialog().browseSingle(type=1, heading=strings(58007).encode('utf-8'), shares='files', mask='.zip|settings.xml|source.db')

        if filename is not None and filename != '':
            deb('SettingsImp importSettings file {}'.format(filename))
            if not os.path.isdir(self.profilePath):
                if PY3:
                    os.makedirs(self.profilePath, exist_ok=True)
                else:
                    os.makedirs(self.profilePath)
            if filename[-4:] == '.zip':
                try:
                    zf = zipfile.ZipFile(filename)
                    for fileN in [ dbFileName, settingsFileName, categoriesFileName ]:
                        try:
                            zf.extract(fileN, self.profilePath)
                            success = True
                        except Exception as ex:
                            deb('SettingsImp importSettings: Error got exception {} while reading archive {}'.format(getExceptionString(), filename))
                except Exception as ex:
                    deb('importSettings Exception: {}'.format(ex))
                    ### Force import
                    #try:
                        #for fileN in [ dbFileName, settingsFileName, categoriesFileName ]:
                            #with gzip.open(filename, 'r') as f_in, open(os.path.join(self.profilePath, fileN), 'wb') as f_out:
                                #shutil.copyfileobj(f_in, f_out)
                            #success = True
                    #except Exception as ex:
                        #deb('SettingsImp importSettings: Error got exception %s while reading archive %s' % (getExceptionString(), filename))

            else:
                deb('Importing settings as single files!')
                for fileN in [ dbFileName, settingsFileName, categoriesFileName ]:
                    try:
                        source_file = os.path.join(os.path.dirname(filename), fileN)
                        deb('Trying to copy file: {} to {}'.format(source_file, self.profilePath))
                        shutil.copy2(source_file, self.profilePath)
                        success = True
                    except:
                        deb('Failed to copy file')

            if success:
                try:
                    xbmcgui.Dialog().ok(strings(58003),'\n' + strings(58008) + '.')
                except:
                    xbmcgui.Dialog().ok(strings(58003).encode('utf-8'),'\n' + strings(58008).encode('utf-8') + '.')
            else:
                try:
                    xbmcgui.Dialog().ok(strings(58003),'\n' + strings(58009) + '.' + '\n' + strings(58010) + '.')
                except:
                    xbmcgui.Dialog().ok(strings(58003).encode('utf-8'),'\n' + strings(58009).encode('utf-8') + '.' + '\n' + strings(58010).encode('utf-8') + '.')
        return success

    def importRecordApp(self, filename):
        try:
            binaryFinalPath = None
            if PY3:
                xbmcRootDir = xbmcvfs.translatePath('special://xbmc')
            else:
                xbmcRootDir = xbmc.translatePath('special://xbmc')
            if filename is None:
                try:
                    filename = xbmcgui.Dialog().browseSingle(type=1, heading=strings(69012), shares='files')
                except:
                    filename = xbmcgui.Dialog().browseSingle(type=1, heading=strings(69012).encode('utf-8'), shares='files')
            if filename == '':
                deb('importRecordApp no file selected for import!')
                return
            binaryFilename = os.path.basename(filename)
            deb('RecordAppImporter filepath: {}, filename: {}, xbmcRootDir: {}'.format(filename, binaryFilename, xbmcRootDir))

            if xbmc.getCondVisibility('system.platform.android'):
                deb('RecordAppImporter detected Android!')

                recordDirName = 'recapp-' + os.name
                recordAppDir = os.path.join(xbmcRootDir.replace('cache/apk/assets/', ''), recordDirName)
                recordAppLibDir = os.path.join(recordAppDir, 'lib')

                deb('RecordAppImporter recordAppDir: {}, recordAppLibDir: {}'.format(recordAppDir, recordAppLibDir))

                if 'ffmpeg' in binaryFilename or 'rtmpdump' in binaryFilename or 'avconv' in binaryFilename:
                    # main
                    try:
                        if PY3:
                            os.makedirs(recordAppDir, exist_ok=True)
                        else:
                            os.makedirs(recordAppDir)
                    except:
                        deb('RecordAppImporter exception: {}'.format(getExceptionString()))

                    # lib
                    try:
                        if PY3:
                            os.makedirs(recordAppLibDir, exist_ok=True)
                        else:
                            os.makedirs(recordAppLibDir)
                    except:
                        deb('RecordAppImporter exception: {}'.format(getExceptionString()))

                    # copy file to root
                    deb('RecordAppImporter copying files')
                    try:
                        shutil.copy2(filename, recordAppDir)
                    except:
                        deb('RecordAppImporter exception: {}'.format(getExceptionString()))

                    fileLib = os.path.join(os.path.dirname(filename), 'lib')
                    if os.path.isdir(fileLib):
                        for filen in os.listdir(fileLib):
                            deb('importRecordApp copy file from lib: {}'.format(filen))
                            try:
                                shutil.copy2(os.path.join(fileLib, filen), recordAppLibDir)
                            except:
                                deb('RecordAppImporter exception: {}'.format(getExceptionString()))

                    binaryFinalPath = os.path.join(recordAppDir, binaryFilename)
            else:
                #other than android
                deb('RecordAppImporter not Android!')
                if 'ffmpeg' in binaryFilename or 'rtmpdump' in binaryFilename or 'avconv' in binaryFilename:
                    binaryFinalPath = filename

            if binaryFinalPath is not None:
                deb('binaryFinalPath: {}'.format(binaryFinalPath))
                if os.path.isfile(binaryFinalPath):
                    try:
                        st = os.stat(binaryFinalPath)
                        os.chmod(binaryFinalPath, stat.S_ISVTX | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
                    except:
                        deb('Unable to set exec permissions to file {}'.format(binaryFinalPath))

                    if 'ffmpeg' in binaryFilename or 'avconv' in binaryFilename:
                        deb('importRecordApp setting ffmpeg app to: {}'.format(binaryFinalPath))
                        ADDON.setSetting(id='ffmpegExe', value=str(binaryFinalPath))
                        try:
                            xbmcgui.Dialog().ok(strings(69012),'\n' + 'FFMPEG ' + strings(69013))
                        except:
                            xbmcgui.Dialog().ok(strings(69012).encode('utf-8'),'\n' + 'FFMPEG ' + strings(69013).encode('utf-8'))

                    if 'rtmpdump' in binaryFilename:
                        deb('importRecordApp setting rtmpdump app to: {}'.format(binaryFinalPath))
                        ADDON.setSetting(id='rtmpdumpExe', value=str(binaryFinalPath))
                        try:
                            xbmcgui.Dialog().ok(strings(69012),'\n' + 'RTMPDUMP ' + strings(69013))
                        except:
                            xbmcgui.Dialog().ok(strings(69012).encode('utf-8'),'\n' + 'RTMPDUMP ' + strings(69013).encode('utf-8'))
                else:
                    deb('importRecordApp error destination file: {} does not exist'.format(binaryFinalPath))

        except Exception as ex:
            deb('RecordAppImporter Error: {}'.format(getExceptionString()))
            raise

    def downloadRecordApp(self):
        recordApp = None
        rtmpdumpExe = None
        ffmpegExe = None
        failedToDownload = False
        failedToFindBinary = False

        if platform.system() == WINDOWS_OS_NAME: # WINDOWS_OS_NAME:
            deb('downloadRecordApp detected os = %s, downloading recordApp from %s' % (platform.system(), recordAppWindows))
            recordApp = recordAppWindows
        else:
            deb('downloadRecordApp detected os family = %s, please select your operating system' % platform.system())
            systems = list()
            try:
                systems.append(strings(30204))
            except:
                systems.append(strings(30204).encode('utf-8', 'replace'))
            systems.append(WINDOWS_OS_NAME)
            systems.append(ANDROID_OS_NAME)
            systems.append(MAC_OS_NAME)
            systems.append(COREELEC_OS_NAME)
            systems.append(LINUX_OS_NAME)
            systems.append(OSMC_OS_NAME)
            systems.append(OTHER_OS_NAME)
            ret = xbmcgui.Dialog().select(strings(69023), systems)
            if ret > 0:
                system = systems[ret]
                deb('downloadRecordApp %s was choosen' % system)
                if system == WINDOWS_OS_NAME:
                    recordApp = recordAppWindows
                elif system == MAC_OS_NAME:
                    recordApp = recordAppMacOS
                elif system == ANDROID_OS_NAME:
                    recordApp = recordAppAndroid
                elif system == COREELEC_OS_NAME or system == LINUX_OS_NAME or system == OTHER_OS_NAME or system == OSMC_OS_NAME:
                    possibleAppDirs = ['/bin', '/usr/local/bin', '/usr/bin', '/storage/.kodi/addons/tools.ffmpeg-tools/bin']
                    defaultRtmpdumpExe = 'rtmpdump'
                    defaultFFmpegExe1 = 'ffmpeg'
                    defaultFFmpegExe2 = 'avconv'
                    for path in possibleAppDirs:
                        if os.path.isfile(os.path.join(path, defaultRtmpdumpExe)):
                            rtmpdumpExe = os.path.join(path, defaultRtmpdumpExe)
                        if os.path.isfile(os.path.join(path, defaultFFmpegExe1)):
                            ffmpegExe = os.path.join(path, defaultFFmpegExe1)
                        elif os.path.isfile(os.path.join(path, defaultFFmpegExe2)):
                            ffmpegExe = os.path.join(path, defaultFFmpegExe2)
                        #dopisac do importa obsluge nazwy avconv !!!!!!!!!!!!!
                    if rtmpdumpExe is None and ffmpegExe is None:
                        failedToFindBinary = True
                        #install libav-tools
            else:
                deb('downloadRecordApp Abort was choosen')
                return

        if recordApp is not None:
            try:
                xbmcgui.Dialog().ok(strings(69012),'\n' + strings(69018))
            except:
                xbmcgui.Dialog().ok(strings(69012).encode('utf-8', 'replace'),'\n' + strings(69018).encode('utf-8'))
            try:
                deb('downloadRecordApp downloading app from %s' % recordApp)
                recordAppDir = os.path.join(self.profilePath, 'record_app')
                if os.path.isdir(recordAppDir):
                    shutil.rmtree(recordAppDir)
                if not os.path.isdir(recordAppDir):
                    if PY3:
                        os.makedirs(recordAppDir, exist_ok=True)
                    else:
                        os.makedirs(recordAppDir)

                failCounter = 0
                content = None

                while failCounter < 10:
                    if PY3:
                        try:
                            reqUrl   = urllib.request.Request(recordApp)
                            reqUrl.add_header('authority', 'raw.githubusercontent.com')
                            reqUrl.add_header('upgrade-insecure-requests', '1')
                            reqUrl.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36 Edg/98.0.1108.50')
                            reqUrl.add_header('Keep-Alive', 'timeout=20')
                            reqUrl.add_header('Connection', 'Keep-Alive')
                            u = urllib.request.urlopen(reqUrl, timeout=5)
                            content = u.read()
                            break
                        except http.client.IncompleteRead as ex:
                            failCounter = failCounter + 1
                            deb('downloadRecordApp download exception: %s, failCounter: %d - retrying' % (str(ex), failCounter))
                        except Exception as ex:
                            deb('downloadRecordApp download exception: %s, failCounter: %d - aborting' % (str(ex), failCounter))
                            break
                    else:
                        try:
                            reqUrl   = urllib2.Request(recordApp)
                            reqUrl.add_header('authority', 'raw.githubusercontent.com')
                            reqUrl.add_header('upgrade-insecure-requests', '1')
                            reqUrl.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:19.0) Gecko/20121213 Firefox/19.0')
                            reqUrl.add_header('Keep-Alive', 'timeout=20')
                            reqUrl.add_header('Connection', 'Keep-Alive')
                            u = urllib2.urlopen(reqUrl, timeout=5)
                            content = u.read()
                            break
                        except httplib.IncompleteRead as ex:
                            failCounter = failCounter + 1
                            deb('downloadRecordApp download exception: %s, failCounter: %d - retrying' % (str(ex), failCounter))
                        except Exception as ex:
                            deb('downloadRecordApp download exception: %s, failCounter: %d - aborting' % (str(ex), failCounter))
                            break

                if content == None:
                    deb('downloadRecordApp failed to download record app from %s' % recordApp)
                    failedToDownload = True
                else:
                    memfile = io.BytesIO(content)
                    unziped = zipfile.ZipFile(memfile)
                    unziped.extractall(recordAppDir)
                    for filename in unziped.namelist():
                        if 'ffmpeg' in filename or 'avconv' in filename:
                            ffmpegExe = os.path.join(recordAppDir, filename)
                        elif 'rtmpdump' in filename:
                            rtmpdumpExe = os.path.join(recordAppDir, filename)

            except Exception as ex:
                deb('downloadRecordApp exception: %s!' % getExceptionString() )
                raise

        if PY3:
            settingsImportScript = os.path.join(xbmcvfs.translatePath(ADDON.getAddonInfo('path')), 'settingsImportExport.py')
        else:
            settingsImportScript = os.path.join(xbmc.translatePath(ADDON.getAddonInfo('path')), 'settingsImportExport.py')
        if ffmpegExe is not None:
            sys.argv = [settingsImportScript, 'ImportRecordApp', ffmpegExe]
            exec(compile(open(settingsImportScript, 'rb').read(), settingsImportScript, 'exec'))
        if rtmpdumpExe is not None:
            sys.argv = [settingsImportScript, 'ImportRecordApp', rtmpdumpExe]
            exec(compile(open(settingsImportScript, 'rb').read(), settingsImportScript, 'exec'))

        if ffmpegExe is not None and rtmpdumpExe is None:
            deb('downloadRecordApp found only FFmpeg but no rtmpdump - setting ffmpeg as only app')
            ADDON.setSetting(id='use_only_ffmpeg', value=str('true'))

        if failedToDownload:
            try:
                xbmcgui.Dialog().ok(strings(69012),'\n' + strings(69019))
            except:
                xbmcgui.Dialog().ok(strings(69012).encode('utf-8', 'replace'),'\n' + strings(69019).encode('utf-8'))
        elif failedToFindBinary:
            try:
                xbmcgui.Dialog().ok(strings(69012),'\n' + strings(69021))
            except:
                xbmcgui.Dialog().ok(strings(69012).encode('utf-8', 'replace'),'\n' + strings(69021).encode('utf-8'))
        elif ffmpegExe is None and rtmpdumpExe is None:
            try:
                xbmcgui.Dialog().ok(strings(69012),'\n' + strings(69022))
            except:
                xbmcgui.Dialog().ok(strings(69012).encode('utf-8', 'replace'),'\n' + strings(69022).encode('utf-8'))

    def adultPicker(self):
        deb('starting adultPicker')
        enabling = False

        try:
            options = list()
        except:
            options.append(strings(30008).encode('utf-8', 'replace'))
        options.append(strings(30008))
        if ADDON.getSetting('XXX_EPG') != '':
            #disabling
            try:
                options.append( strings(30719) + ' ' + strings(30747))
            except:
                options.append( strings(30719).encode('utf-8', 'replace') + ' ' + strings(30747).encode('utf-8', 'replace'))
        else:
            #enabling
            try:
                options.append( strings(30722) + ' ' + strings(30747))
            except:
                options.append( strings(30722).encode('utf-8', 'replace') + ' ' + strings(30747).encode('utf-8', 'replace'))
            enabling = True

        ret = xbmcgui.Dialog().select(strings(30715), options)
        if ret > 0:
            deb('Adult - option picked!')
            if not enabling:
                #disable adult
                deb('Adult - disabling!')
                ADDON.setSetting(id='XXX_EPG', value=str(''))
                try:
                    ADDON.setSetting(id='showAdultChannels', value=str(strings(30720)))
                except:
                    ADDON.setSetting(id='showAdultChannels', value=str(strings(30720).encode('utf-8', 'replace')))
            else:
                #enable adult
                deb('Adult - enter password!')
                try:
                    password = xbmcgui.Dialog().input(strings(30723))
                except:
                    password = xbmcgui.Dialog().input(strings(30723).encode('utf-8', 'replace'))
                if password == 'mods':
                    deb('Adult - password correct, enabling!')
                    adult = adultEPG
                    ret = xbmcgui.Dialog().select(strings(30745), [strings(30171), strings(30172)])

                    if ret < 0:
                        return

                    if ret == 0:
                        pass

                    elif ret == 1:
                        label = strings(30747).capitalize()
                        txt = 'https://'

                        kb = xbmc.Keyboard(txt,'')
                        kb.setHeading(strings(59945).format(label))
                        kb.setHiddenInput(False)
                        kb.doModal()
                        c = kb.getText() if kb.isConfirmed() else None
                        if c == '': c = None

                        if c is not None:
                            adult = c

                    ADDON.setSetting(id='XXX_EPG', value=str(adult))
                    try:
                        ADDON.setSetting(id='showAdultChannels', value=str(strings(30721)))
                    except:
                        ADDON.setSetting(id='showAdultChannels', value=str(strings(30721).encode('utf-8', 'replace')))
                else:
                    deb('Adult - password incorrect: %s' % password)
                    try:
                        xbmcgui.Dialog().ok(strings(30715), strings(30724))
                    except:
                        xbmcgui.Dialog().ok(strings(30715).encode('utf-8', 'replace'), strings(30724).encode('utf-8', 'replace'))

        xbmc.executebuiltin('Addon.OpenSettings(%s)' % ADDON_ID)

    def vodPicker(self):
        deb('starting vodPicker')
        enabling = False

        options = list()
        options.append(strings(30008))
        if ADDON.getSetting('VOD_EPG') != '':
            #disabling
            try:
                options.append( strings(30719) + ' ' + strings(30748))
            except:
                options.append( strings(30719).encode('utf-8', 'replace') + ' ' + strings(30748).encode('utf-8', 'replace'))
        else:
            #enabling
            try:
                options.append( strings(30722) + ' ' + strings(30748))
            except:
                options.append( strings(30722).encode('utf-8', 'replace') + ' ' + strings(30748).encode('utf-8', 'replace'))
            enabling = True

        ret = xbmcgui.Dialog().select(strings(30745), options)
        if ret > 0:
            deb('Vod - option picked!')
            if not enabling:
                #disable vod
                deb('Vod - disabling!')
                ADDON.setSetting(id='VOD_EPG', value=str(''))
                try:
                    ADDON.setSetting(id='showVodChannels', value=str(strings(30720)))
                except:
                    ADDON.setSetting(id='showVodChannels', value=str(strings(30720).encode('utf-8', 'replace')))
            else:
                #enable vod
                deb('Vod - enabling!')
                vod = vodEPG
                ret = xbmcgui.Dialog().select(strings(30745), [strings(30171), strings(30172)])

                if ret < 0:
                    return

                if ret == 0:
                    pass

                elif ret == 1:
                    label = strings(30748).capitalize()
                    txt = 'https://'

                    kb = xbmc.Keyboard(txt,'')
                    kb.setHeading(strings(59945).format(label))
                    kb.setHiddenInput(False)
                    kb.doModal()
                    c = kb.getText() if kb.isConfirmed() else None
                    if c == '': c = None

                    if c is not None:
                        vod = c

                ADDON.setSetting(id='VOD_EPG', value=str(vod))
                try:
                    ADDON.setSetting(id='showVodChannels', value=str(strings(30721)))
                except:
                    ADDON.setSetting(id='showVodChannels', value=str(strings(30721).encode('utf-8', 'replace')))

        xbmc.executebuiltin('Addon.OpenSettings(%s)' % ADDON_ID)

    def countryUrlPicker(self, execute=None, options=True):
        deb('starting countryUrlPicker')
        if execute:
            ADDON = execute
        else:
            ADDON_ID = 'script.mtvguide'
            ADDON = xbmcaddon.Addon(id=ADDON_ID)

        enabling = False

        ccListCh = list()
        langListCh = list()

        selectList = list()
        epgList = list()

        continent = xbmcgui.Dialog().select(strings(30725), [xbmc.getLocalizedString(593), strings(30727), strings(30728), strings(30729), strings(30730), strings(30731), strings(30732), '[COLOR red]' + strings(30726) + '[/COLOR]'])

        if continent is None:
            enabling = True
            if options:
                return xbmc.executebuiltin('Addon.OpenSettings(%s)' % ADDON_ID)
            else:
                return False

        elif continent < 0:
            enabling = True
            if options:
                return xbmc.executebuiltin('Addon.OpenSettings(%s)' % ADDON_ID)
            else:
                return False

        elif continent == 0:
            filtered_dict = dict((k, v) for k, v in CC_DICT.items() if int(v['continent']) != 7)
            ADDON.setSetting(id='show_group_channels', value='true')

        elif continent == 7:
            filtered_dict = dict((k, v) for k, v in CC_DICT.items() if int(v['continent']) == 7)
            ADDON.setSetting(id='show_group_channels', value='false')

        else:
            filtered_dict = dict((k, v) for k, v in CC_DICT.items() if int(v['continent']) == continent or (int(v['continent']) == -1 and continent != 6))
            ADDON.setSetting(id='show_group_channels', value='true')

        if sys.version_info[0] < 3:
            filtered_dict = collections.OrderedDict(sorted(filtered_dict.items()))
            orderedDict = collections.OrderedDict(sorted(CC_DICT.items()))

        for cc, value in filtered_dict.items():
            lang = value.get('translated', '')
            if lang == '':
                lang = value['language']

            if lang.isdigit():
                country = strings(int(lang))
            else:
                country = lang

            country_code = ADDON.getSetting(id='country_code_{cc}'.format(cc=cc))

            main_epg = ADDON.getSetting(id='m-TVGuide')
            epg = ADDON.getSetting(id='epg_{cc}'.format(cc=cc))

            if cc == 'all':
                enabled_main_epg = country + ' [COLOR gold][' + main_epg + '][/COLOR]'
                disabled = country + ' [COLOR disabled][' + strings(30720) + '][/COLOR]'
            else:
                enabled_main_epg = '[B]' + cc.upper() + '[/B] - ' + country + ' [COLOR gold][' + main_epg + '][/COLOR]'
                disabled = '[B]' + cc.upper() + '[/B] - ' + country + ' [COLOR disabled][' + strings(30720) + '][/COLOR]'

            enabled_epg = '[B]' + cc.upper() + '[/B] - ' + country + ' [COLOR gold][' + epg + '][/COLOR]'

            if epg and country_code == 'true':
                selectList.append(enabled_epg)
                epgList.append(enabled_epg)
            elif main_epg and (country_code == 'true' or cc == 'all'):
                selectList.append(enabled_main_epg)
                epgList.append(enabled_main_epg)
            else:
                selectList.append(disabled)
                if epg:
                    epgList.append(enabled_epg)
                elif main_epg:
                    epgList.append(enabled_main_epg)
                else:
                    epgList.append(disabled)

        multiselect = xbmcgui.Dialog().multiselect(strings(59943), selectList)

        ccList = list(filtered_dict)
        countrys = list(filtered_dict.values())

        if sys.version_info[0] < 3:
            removeList = list(orderedDict)
        else:
            removeList = list(CC_DICT)

        if multiselect is None:
            enabling = True
            if options:
                return self.countryUrlPicker()
            else:
                return self.countryUrlPicker(options=False)

        elif not multiselect:
            for cc in ccList:
                ADDON.setSetting(id='country_code_{cc}'.format(cc=cc), value='false')

            deb('epg url - disabling!')
            try:
                ADDON.setSetting(id='countryUrlChannels', value=str(strings(30720)))
            except:
                ADDON.setSetting(id='countryUrlChannels', value=str(strings(30720).encode('utf-8', 'replace')))
            if options:
                return xbmc.executebuiltin('Addon.OpenSettings(%s)' % ADDON_ID)
            else:
                return False

        elif len(multiselect) == 1:
            for select in multiselect:
                epg = ADDON.getSetting(id='m-TVGuide')
                if epg:
                    txt = xbmcgui.Dialog().input(strings(59945).format(strings(59941)), defaultt=str(epg))
                else:
                    txt = xbmcgui.Dialog().input(strings(59945).format(strings(59941)), defaultt=str('http://'))

                if txt != '' or txt != 'http://' or txt != 'https://':
                    ADDON.setSetting(id='m-TVGuide', value=str(txt))

                    if ccList[select] != 'all':
                        ADDON.setSetting(id='country_code_{cc}'.format(cc=ccList[select]), value='true')
                        ADDON.setSetting(id='epg_{cc}'.format(cc=ccList[select]), value=str(''))

                    removeList.remove(ccList[select])

                    deb('epg url - enabling!')
                    try:
                        ADDON.setSetting(id='countryUrlChannels', value=str(strings(30721) + ' (' + strings(59919)+')'))
                    except:
                        ADDON.setSetting(id='countryUrlChannels', value=str((strings(30721) + ' (' + strings(59919)+')').encode('utf-8', 'replace'))) 

        elif len(multiselect) > 1:
            for item in multiselect:
                if item in multiselect:
                    langListCh.append(epgList[item])
                    ccListCh.append(ccList[item])

        s = 0

        while len(langListCh) > 0:
            select = xbmcgui.Dialog().select(strings(30101), langListCh)
            if select > -1:
                main_epg = ADDON.getSetting('m-TVGuide')

                heading = re.sub('\s\[COLOR.*', '', langListCh[select])
                try:
                    find = re.findall('.*\s\W\w+\s\w+\W\[(http.*)\]\W\W\w+\W', langListCh[select])
                    epg = find[0] if find else 'https://'
                except:
                    epg = 'https://'

                txt = xbmcgui.Dialog().input(strings(59945).format(heading), defaultt=str(epg))

                if txt != '' or txt != 'http://' or txt != 'https://':
                    if s == 0:
                        ADDON.setSetting(id='m-TVGuide', value=str(txt))
                        ADDON.setSetting(id='epg_{cc}'.format(cc=ccListCh[select]), value=str(''))
                        s += 1

                    elif s > 0:
                        ADDON.setSetting(id='epg_{cc}'.format(cc=ccListCh[select]), value=str(txt))

                    ADDON.setSetting(id='country_code_{cc}'.format(cc=ccListCh[select]), value='true')

                    removeList.remove(ccListCh[select])

                    langListCh.pop(select)
                    ccListCh.pop(select)

                    deb('epg url - enabling!')
                    try:
                        ADDON.setSetting(id='countryUrlChannels', value=str(strings(30721) + ' (' + strings(59919)+')'))
                    except:
                        ADDON.setSetting(id='countryUrlChannels', value=str((strings(30721) + ' (' + strings(59919)+')').encode('utf-8', 'replace'))) 

            else:
                setList = list()
                for cc in ccList:
                    cc = ADDON.getSetting(id='country_code_{cc}'.format(cc=cc))
                    setList.append(cc)

                if 'true' in setList:
                    deb('epg url - enabling!')
                    try:
                        ADDON.setSetting(id='countryUrlChannels', value=str(strings(30721) + ' (' + strings(59919)+')'))
                    except:
                        ADDON.setSetting(id='countryUrlChannels', value=str((strings(30721) + ' (' + strings(59919)+')').encode('utf-8', 'replace'))) 

                else:
                    deb('epg url - disabling!')
                    try:
                        ADDON.setSetting(id='countryUrlChannels', value=str(strings(30720)))
                    except:
                        ADDON.setSetting(id='countryUrlChannels', value=str(strings(30720).encode('utf-8', 'replace')))

                break

        enabling = True
        if options:
            xbmc.executebuiltin('Addon.OpenSettings(%s)' % ADDON_ID)

        for cc in removeList:
            ADDON.setSetting(id='country_code_{cc}'.format(cc=cc), value='false')

        return True

    def countryFilePicker(self, execute=None, options=True):
        deb('starting countryFilePicker')
        if execute:
            ADDON = execute
        else:
            ADDON_ID = 'script.mtvguide'
            ADDON = xbmcaddon.Addon(id=ADDON_ID)

        enabling = False

        ccListCh = list()
        langListCh = list()

        selectList = list()
        epgList = list()

        continent = xbmcgui.Dialog().select(strings(30725), [xbmc.getLocalizedString(593), strings(30727), strings(30728), strings(30729), strings(30730), strings(30731), strings(30732), '[COLOR red]' + strings(30726) + '[/COLOR]'])

        if continent is None:
            enabling = True
            if options:
                return xbmc.executebuiltin('Addon.OpenSettings(%s)' % ADDON_ID)
            else:
                return False

        elif continent < 0:
            enabling = True
            if options:
                return xbmc.executebuiltin('Addon.OpenSettings(%s)' % ADDON_ID)
            else:
                return False

        elif continent == 0:
            filtered_dict = dict((k, v) for k, v in CC_DICT.items() if int(v['continent']) != 7)
            ADDON.setSetting(id='show_group_channels', value='true')

        elif continent == 7:
            filtered_dict = dict((k, v) for k, v in CC_DICT.items() if int(v['continent']) == 7)
            ADDON.setSetting(id='show_group_channels', value='false')

        else:
            filtered_dict = dict((k, v) for k, v in CC_DICT.items() if int(v['continent']) == continent or (int(v['continent']) == -1 and continent != 6))
            ADDON.setSetting(id='show_group_channels', value='true')

        if sys.version_info[0] < 3:
            filtered_dict = collections.OrderedDict(sorted(filtered_dict.items()))

        for cc, value in filtered_dict.items():
            lang = value.get('translated', '')
            if lang == '':
                lang = value['language']

            if lang.isdigit():
                country = strings(int(lang))
            else:
                country = lang

            country_code = ADDON.getSetting(id='country_code_{cc}'.format(cc=cc))

            main_epg = ADDON.getSetting(id='m-TVGuide')
            epg = ADDON.getSetting(id='epg_{cc}'.format(cc=cc))

            if cc == 'all':
                enabled_main_epg = country + ' [COLOR gold][' + strings(30721) + '][/COLOR]'
                disabled = country + ' [COLOR disabled][' + strings(30720) + '][/COLOR]'
            else:
                enabled_main_epg = '[B]' + cc.upper() + '[/B] - ' + country + ' [COLOR gold][' + strings(30721) + '][/COLOR]'
                disabled = '[B]' + cc.upper() + '[/B] - ' + country + ' [COLOR disabled][' + strings(30720) + '][/COLOR]'

            enabled_epg = '[B]' + cc.upper() + '[/B] - ' + country + ' [COLOR gold][' + strings(30721) + '][/COLOR]'

            if epg and country_code == 'true':
                selectList.append(enabled_epg) 
                epgList.append(enabled_epg)
            elif main_epg and (country_code == 'true' or cc == 'all'):
                selectList.append(enabled_main_epg)
                epgList.append(enabled_main_epg) 
            else:
                selectList.append(disabled) 
                if epg:
                    epgList.append(enabled_epg) 
                elif main_epg:
                    epgList.append(enabled_main_epg)
                else:
                    epgList.append(disabled) 

        multiselect = xbmcgui.Dialog().multiselect(strings(59943), selectList)

        ccList = list(filtered_dict)
        countrys = list(filtered_dict.values())

        if multiselect is None:
            enabling = True
            if options:
                return self.countryFilePicker()
            else:
                return self.countryFilePicker(options=False)

        elif not multiselect:
            for cc in ccList:
                ADDON.setSetting(id='country_code_{cc}'.format(cc=cc), value='false')

            deb('epg url - disabling!')
            try:
                ADDON.setSetting(id='countryFileChannels', value=str(strings(30720)))
            except:
                ADDON.setSetting(id='countryFileChannels', value=str(strings(30720).encode('utf-8', 'replace')))
            if options:
                return xbmc.executebuiltin('Addon.OpenSettings(%s)' % ADDON_ID)
            else:
                return False

        elif multiselect:
            for item in ccList:
                ADDON.setSetting(id='country_code_{cc}'.format(cc=item), value='false')

            for item in multiselect:
                if item in multiselect:
                    langListCh.append(epgList[item])
                    ccListCh.append(ccList[item])
                    ADDON.setSetting(id='country_code_{cc}'.format(cc=ccList[item]), value='true')

            fn = xbmcgui.Dialog().browse(1, strings(59942), '')
            ADDON.setSetting('xmltv_file', fn)
            deb('epg file - enabling!')

            if fn != '':
                deb('epg url - enabling!')
                try:
                    ADDON.setSetting(id='countryFileChannels', value=str(strings(30721) + ' (' + strings(59908)+')'))
                except:
                    ADDON.setSetting(id='countryFileChannels', value=str((strings(30721) + ' (' + strings(59908)+')').encode('utf-8', 'replace'))) 

            else:
                deb('epg url - disabling!')
                try:
                    ADDON.setSetting(id='countryFileChannels', value=str(strings(30720)))
                except:
                    ADDON.setSetting(id='countryFileChannels', value=str(strings(30720).encode('utf-8', 'replace')))

        enabling = True

        if options:
            xbmc.executebuiltin('Addon.OpenSettings(%s)' % ADDON_ID)

        return True

settingI = SettingsImp()