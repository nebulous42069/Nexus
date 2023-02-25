#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   GNU General Public License

#   m-TVGuide KODI Addon
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
    import io
else:
    import StringIO

import os, re, shutil, zipfile
import xbmcgui, xbmc, xbmcvfs
from strings import *
from serviceLib import ShowList

try:
    skin_resolution = '1080i'
except:
    skin_resolution = '720p'

class SkinObject:
    def __init__(self, name, url="", version="", minGuideVersion="", icon = "", fanart="", description = ""):
        self.name = name
        self.url = url
        self.version = version
        self.icon = icon
        self.fanart = fanart
        self.description = description
        self.minGuideVersion = minGuideVersion

    def __eq__(self, other):
        return self.name == other.name

class Skin:
    if PY3:
        try:
            PROFILE_PATH  = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
        except:
            PROFILE_PATH  = xbmcvfs.translatePath(ADDON.getAddonInfo('profile')).decode('utf-8')
    else:
        try:
            PROFILE_PATH  = xbmc.translatePath(ADDON.getAddonInfo('profile'))
        except:
            PROFILE_PATH  = xbmc.translatePath(ADDON.getAddonInfo('profile')).decode('utf-8')

    ADDON_EMBEDDED_SKINS    = os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins')

    ADDON_CUSTOM_SKINS_RES  = os.path.join(PROFILE_PATH, 'resources')
    ADDON_CUSTOM_SKINS      = os.path.join(ADDON_CUSTOM_SKINS_RES, 'skins')

    NEW_SKINS_BASE_URL      = 'https://github.com/Mariusz89B/script.mtvguide-support/raw/main/skins/'

    NEW_SKINS_URL           = 'https://raw.githubusercontent.com/Mariusz89B/script.mtvguide-support/main/skins/skinlist.xml'

    CURRENT_SKIN            = ADDON.getSetting('Skin')
    CURRENT_SKIN_DIR        = None
    CURRENT_SKIN_BASE_DIR   = None
    SKIN_XML_REGEX          = 'skin\s*name\s*=\s*"(.+?)"\s*url\s*=\s*"(.+?)"\s*version\s*=\s*"(.+?)"\s*mTVGuideVersion\s*=\s*"(.+?)"\s*icon\s*=\s*"(.*?)"\s*fanart\s*=\s*"(.*?)"\s*description\s*=\s*"(.*?)"'

    @staticmethod
    def getSkinPath():
        if Skin.CURRENT_SKIN_DIR is None:
            if os.path.isdir(os.path.join(Skin.ADDON_CUSTOM_SKINS, Skin.CURRENT_SKIN)):
                Skin.CURRENT_SKIN_DIR = os.path.join(Skin.ADDON_CUSTOM_SKINS, Skin.CURRENT_SKIN)
                Skin.CURRENT_SKIN_BASE_DIR = Skin.PROFILE_PATH
            elif os.path.isdir(os.path.join(Skin.ADDON_EMBEDDED_SKINS, Skin.CURRENT_SKIN)):
                Skin.CURRENT_SKIN_DIR = os.path.join(Skin.ADDON_EMBEDDED_SKINS, Skin.CURRENT_SKIN)
                Skin.CURRENT_SKIN_BASE_DIR = ADDON.getAddonInfo('path')

        return Skin.CURRENT_SKIN_DIR

    @staticmethod
    def getDefaultSkinBaseDir():
        if os.path.isdir(os.path.join(Skin.ADDON_CUSTOM_SKINS, 'skin.default')):
            return Skin.PROFILE_PATH
        else:
            return ADDON.getAddonInfo('path')

    @staticmethod
    def getSkinBasePath():
        if Skin.CURRENT_SKIN_BASE_DIR is None:
            Skin.getSkinPath()
        return Skin.CURRENT_SKIN_BASE_DIR

    @staticmethod
    def fixSkinIfNeeded():
        Skin.createCustomDirIfNeeded()
        if Skin.getSkinPath() is None:
            deb('Skins fixing skin!')
            success = False
            deb('Missing skin: %s' % Skin.getSkinName())
            skins = Skin.getSkinList()
            for skin in skins:
                #deb('Checking skin: %s, guideVersion: %s' % (skin.name, skin.minGuideVersion))
                if skin.name == Skin.getSkinName():
                    deb('Skin found online skin which is missing: %s, starting download!' % skin.name)
                    success = Skin.downloadSkin(skin)
                    xbmcgui.Dialog().notification(strings(30710), strings(30709) + ": " + skin.name, time=7000, sound=False)

            if success == False:
                ADDON.setSetting(id="Skin", value=str('skin.default'))
                xbmcgui.Dialog().ok(strings(LOAD_ERROR_TITLE), strings(SKIN_ERROR_LINE1), strings(SKIN_ERROR_LINE4))
                quit()

    @staticmethod
    def createCustomDirIfNeeded():
        skins = Skin.getSkinList()
        if os.path.isdir(Skin.ADDON_CUSTOM_SKINS) == False:
            deb('Skins creating custom skin dir!')
            if os.path.isdir(Skin.ADDON_CUSTOM_SKINS_RES) == False:
                if os.path.isdir(Skin.PROFILE_PATH) == False:
                    os.makedirs(Skin.PROFILE_PATH)
                os.makedirs(Skin.ADDON_CUSTOM_SKINS_RES)
            os.makedirs(Skin.ADDON_CUSTOM_SKINS)
            try:
                for skin in skins:
                    xpath = os.path.join(Skin.ADDON_CUSTOM_SKINS, 'skin.default')
                    if os.path.exists(xpath) == False:
                        shutil.copytree(os.path.join(Skin.ADDON_EMBEDDED_SKINS, 'skin.default'), os.path.join(Skin.ADDON_CUSTOM_SKINS, 'skin.default'))
            except Exception as ex:
                deb('Skins exception: %s' % getExceptionString())

    @staticmethod
    def selectSkin():
        picker = SkinPicker()

    @staticmethod
    def getCurrentSkinsList():
        Skin.createCustomDirIfNeeded()
        embedded_skins = os.listdir(Skin.ADDON_EMBEDDED_SKINS)
        custom_skins = os.listdir(Skin.ADDON_CUSTOM_SKINS)
        skin_list = list()

        for skin in custom_skins:
            #deb('Skins custom %s' % skin)
            image = os.path.join(Skin.ADDON_CUSTOM_SKINS, skin, 'fanart.jpg')
            if not os.path.isfile(image):
                image = os.path.join(Skin.NEW_SKINS_BASE_URL, skin, 'fanart.jpg')
            icon = os.path.join(Skin.ADDON_CUSTOM_SKINS, skin, 'name.png')
            if not os.path.isfile(icon):
                icon = os.path.join(Skin.NEW_SKINS_BASE_URL, skin, 'name.png')
            skin_list.append(SkinObject(skin, icon=icon, fanart=image))

        for skin in embedded_skins:
            #deb('Skins basic: %s' % skin)
            if skin not in custom_skins:
                image = os.path.join(Skin.ADDON_EMBEDDED_SKINS, skin, 'fanart.jpg')
                if not os.path.isfile(image):
                    image = os.path.join(Skin.NEW_SKINS_BASE_URL, skin, 'fanart.jpg')
                icon = os.path.join(Skin.ADDON_EMBEDDED_SKINS, skin, 'name.png')
                if not os.path.isfile(icon):
                    icon = os.path.join(Skin.NEW_SKINS_BASE_URL, skin, 'name.png')
                skin_list.append(SkinObject(skin, icon=icon, fanart=image))
            else:
                deb('Skipping skin %s since its duplicated' % skin)
        return skin_list

    @staticmethod
    def downloadSkin(skinToDownload):
        Skin.createCustomDirIfNeeded()
        skin_to_download = Skin.NEW_SKINS_BASE_URL + skinToDownload.url
        deb('Downloading skin from: %s' % skin_to_download)
        downloader = ShowList()
        skin_zip = downloader.getJsonFromExtendedAPI(skin_to_download)
        if skin_zip:
            if PY3:
                skin_zip = io.BytesIO(skin_zip)
            else:
                skin_zip = StringIO.StringIO(skin_zip)
            skin_zip = zipfile.ZipFile(skin_zip)
            for name in skin_zip.namelist():
                #deb('Skins extracting file: %s' % name)
                try:
                    skin_zip.extract(name, Skin.ADDON_CUSTOM_SKINS)
                except:
                    deb('Unable to extract file: %s, exception: %s' % (name, getExceptionString()) )

            skin_zip.close()
            return True
        else:
            deb('Failed to download skin')
        return False

    @staticmethod
    def setAddonSkin(skinName):
        ADDON.setSetting(id="Skin", value=skinName)
        deb('Settings skin: %s' % skinName)

    @staticmethod
    def getSkinName():
        return Skin.CURRENT_SKIN

    @staticmethod
    def getSkinList():
        deb('getSkinList')
        skin_list = list()
        matching_skins = list()
        downloader = ShowList()
        xml = downloader.getJsonFromExtendedAPI(Skin.NEW_SKINS_URL)
        if xml:
            xml = xml.decode('utf-8')
            #deb('Decoded XML is %s' % xml)
            items = re.compile(Skin.SKIN_XML_REGEX).findall(xml)

            for item in items:
                #deb('Skin in XML: %s' % str(item))
                skin_list.append(SkinObject(name=str(item[0]), url=str(item[1]), version=float(item[2]), minGuideVersion=Skin.parseVersion(item[3]), icon=(Skin.NEW_SKINS_BASE_URL + item[4]).replace(' ', '%20'), fanart=(Skin.NEW_SKINS_BASE_URL + item[5]).replace(' ', '%20'), description=item[6]))
                #deb('Skin: %s, img: %s' % ( skin_list[len(skin_list)-1].name, skin_list[len(skin_list)-1].icon ))
        else:
            deb('Failed to download online skin list')

        currentGuideVersion   = Skin.getCurrentGuideVersion()
        for skin in skin_list:
            addSkin = True
            if skin.minGuideVersion > currentGuideVersion:
                addSkin = False
                continue

            for skin2 in skin_list:
                if skin.name == skin2.name:
                    if skin.version != skin2.version:
                        #we dont compare same skin isinstance
                        if skin.version < skin2.version:
                            #newer version is available
                            addSkin = False
                            break

            if addSkin:
                matching_skins.append(skin)

        return matching_skins

    #@staticmethod
    #def checkForUpdates():
        #import threading
        #threading.Timer(0, Skin._checkForUpdates).start()

    @staticmethod
    def checkForUpdates():
        deb('_checkForUpdates')
        skins = Skin.getSkinList()
        regex = re.compile('version\s*=\s*(.*)', re.IGNORECASE)
        usedSkinUpdated = False
        for skin in skins:
            iniFile = os.path.join(Skin.ADDON_CUSTOM_SKINS, skin.name, 'settings.ini')
            #deb('iniFile: {}'.format(iniFile))
            if os.path.isfile(iniFile):
                try:
                    fileContent = open(iniFile, 'r').read()
                    #deb('Content: {}'.format(fileContent))
                except:
                    continue
                localVersion = float(regex.search(fileContent).group(1))
                deb('Skin: {}, local version: {}'.format(skin.name, localVersion))
                if float(skin.version) > float(localVersion):
                    deb('Skin: %s, local version: %s, online version: %s - downloading new version' % (skin.name, localVersion, skin.version))
                    success = Skin.downloadSkin(skin)
                    if success:
                        xbmcgui.Dialog().notification(strings(30702), strings(30709) + ": " + skin.name, time=7000, sound=False)
                    if success and skin.name == Skin.getSkinName():
                        usedSkinUpdated = True

        if usedSkinUpdated:
            if not xbmc.getCondVisibility('Window.IsVisible(yesnodialog)'):
                xbmcgui.Dialog().ok(strings(30709), strings(30979))

        deb('Skin finished update')
        return usedSkinUpdated

    @staticmethod
    def parseVersion(version):
        regex = re.compile('(\d*)\.(\d*)\.(\d*)', re.IGNORECASE)
        items = regex.findall(version)
        for item in items:
            return [int(item[0]), int(item[1]), int(item[2])]
        return [int(0), int(0), int(0)]

    @staticmethod
    def getCurrentGuideVersion():
        return Skin.parseVersion(ADDON.getAddonInfo('version'))

    @staticmethod
    def restoreFont(show_dialog):
        if PY3:
            try:
                PROFILE_PATH  = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
            except:
                PROFILE_PATH  = xbmcvfs.translatePath(ADDON.getAddonInfo('profile')).decode('utf-8')
        else:
            try:
                PROFILE_PATH  = xbmc.translatePath(ADDON.getAddonInfo('profile'))
            except:
                PROFILE_PATH  = xbmc.translatePath(ADDON.getAddonInfo('profile')).decode('utf-8')

        currentSkin = xbmc.getSkinDir()

        if PY3:
            kodiPath = xbmcvfs.translatePath("special://home/")
            kodiPathMain = xbmcvfs.translatePath("special://xbmc/")
            kodiSkinPath = xbmcvfs.translatePath("special://skin/")
        else:
            kodiPath = xbmc.translatePath("special://home/")
            kodiPathMain = xbmc.translatePath("special://xbmc/")
            kodiSkinPath = xbmc.translatePath("special://skin/")

        if xbmcvfs.exists(os.path.join(kodiSkinPath, 'xml/')):
            path1 = 'xml'
        elif xbmcvfs.exists(os.path.join(kodiSkinPath, '720p/')):
            path1 = '720p'
        elif xbmcvfs.exists(os.path.join(kodiSkinPath, '1080i/')):
            path1 = '1080i'
        elif xbmcvfs.exists(os.path.join(kodiSkinPath, '16x9/')):
            path1 = '16x9'

        if PY3:
            addons = xbmcvfs.translatePath(os.path.join('special://', 'home', 'addons', currentSkin, path1, 'Font.xml'))
            skins = xbmcvfs.translatePath(os.path.join('special://','skin', currentSkin, path1, 'Font.xml'))
            backup_addons = xbmcvfs.translatePath(os.path.join('special://', 'home', 'addons', currentSkin, path1, 'Font.backup'))
            backup_skins = xbmcvfs.translatePath(os.path.join('special://','skin', currentSkin, path1, 'Font.backup'))
        else:
            addons = xbmc.translatePath(os.path.join('special://', 'home', 'addons', currentSkin, path1, 'Font.xml'))
            skins = xbmc.translatePath(os.path.join('special://','skin', currentSkin, path1, 'Font.xml'))
            backup_addons = xbmc.translatePath(os.path.join('special://', 'home', 'addons', currentSkin, path1, 'Font.backup'))
            backup_skins = xbmc.translatePath(os.path.join('special://','skin', currentSkin, path1, 'Font.backup'))

        if currentSkin == 'skin.estuary' or currentSkin == 'skin.estouchy':
            check = xbmcvfs.exists(backup_addons)
            if check:
                xbmcvfs.delete(addons)
                xbmcvfs.rename(backup_addons, addons)
        else:
            check = xbmcvfs.exists(backup_skins)
            if check:
                xbmcvfs.delete(skins)
                xbmcvfs.rename(backup_skins, skins)

        if show_dialog:
            xbmcgui.Dialog().ok(strings(30770), strings(30771)+'.')

        try:
            file = os.path.join(PROFILE_PATH, 'fonts.list')
            if PY3:
                with open(file, 'w+', encoding='utf-8') as f:
                    f.write('')
            else:
                import codecs
                with codecs.open(file, 'w+', encoding='utf-8') as f:
                    f.write('')
        except:
            deb('Error: fonts.list is missing')

    @staticmethod
    def deleteCustomSkins(show_dialog):
        ADDON.setSetting(id="Skin", value=str('skin.default'))

        if os.path.isdir(Skin.ADDON_CUSTOM_SKINS_RES):
            try:
                shutil.rmtree(Skin.ADDON_CUSTOM_SKINS_RES)
            except:
                pass

        Skin.restoreFont(False)

        ### Add copy defualt skin
        Skin.fixSkinIfNeeded()

        if show_dialog:
            xbmcgui.Dialog().ok(strings(30714), strings(30969)+'.')


class SkinPicker():
    if PY3:
        try:
            PROFILE_PATH  = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
        except:
            PROFILE_PATH  = xbmcvfs.translatePath(ADDON.getAddonInfo('profile')).decode('utf-8')
    else:
        try:
            PROFILE_PATH  = xbmc.translatePath(ADDON.getAddonInfo('profile'))
        except:
            PROFILE_PATH  = xbmc.translatePath(ADDON.getAddonInfo('profile')).decode('utf-8')

    def __init__(self):
        self.download_skin_list = self.getDownloadSkinList()
        self.skin_list = self.getAllSkinList()
        self.picker = self.picker()

    def picker(self):
        listitems = list()

        skins = self.skin_list
        for skin in skins:
            listitem = xbmcgui.ListItem(skin.name)
            listitem.setArt({'thumb': self.setFanartImage(skin)})
            listitems.append(listitem)

        picker = xbmcgui.Dialog().select(strings(30702), listitems, useDetails=True)

        if picker >= 0:
            c = skins[picker]
            self.setCurrentSkin(c)
        else:
            return

    def setFanartImage(self, skin):
        if skin:
            return skin.icon

    def setCurrentSkin(self, currentlySelectedSkin):
        try:
            if currentlySelectedSkin is not None:
                success = True
                if currentlySelectedSkin in self.getDownloadSkinList():
                    success = Skin.downloadSkin(currentlySelectedSkin)
                    if success:
                        xbmcgui.Dialog().notification(strings(30710), strings(30709) + ": " + currentlySelectedSkin.name, time=7000, sound=False)
                if success:
                    Skin.setAddonSkin(currentlySelectedSkin.name)
                    try:
                        file = os.path.join(PROFILE_PATH, 'fonts.list')
                        os.remove(file)
                    except:
                        deb('Error: fonts.list is missing')

                else:
                    deb('Failed to wnload skin %s' % currentlySelectedSkin.name)
            else:
                deb('setCurrentSkin selected skin is none!')
        except:
            deb('setCurrentSkin exception: %s' % getExceptionString() )

    def getAllSkinList(self):
        skin_list = Skin.getCurrentSkinsList()
        try:
            if self.download_skin_list is None:
                download_list = self.getDownloadSkinList()
            else:
                download_list = self.download_skin_list
            if download_list is not None:
                skin_list.extend(download_list)
            else:
                deb('getAllSkinList getDownloadSkinList returned none')
        except:
            pass
        return skin_list


    def getDownloadSkinList(self):
        deb('getDownloadSkinList')
        download_list = Skin.getSkinList()
        current_list = Skin.getCurrentSkinsList()
        for skin_to_download in download_list[:]:
            try:
                current_list.index(skin_to_download)
                download_list.remove(skin_to_download)
                deb('SkinPicker Skin removing skin: %s from download list since its already installed!' % skin_to_download.name)
            except:
                pass
        return download_list

if len(sys.argv) > 1 and sys.argv[1] == 'SelectSkin':
    #Skin._checkForUpdates()
    Skin.selectSkin()

    if PY3:
        try:
            PROFILE_PATH  = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
        except:
            PROFILE_PATH  = xbmcvfs.translatePath(ADDON.getAddonInfo('profile')).decode('utf-8')
    else:
        try:
            PROFILE_PATH  = xbmc.translatePath(ADDON.getAddonInfo('profile'))
        except:
            PROFILE_PATH  = xbmc.translatePath(ADDON.getAddonInfo('profile')).decode('utf-8')
            
    currentSkin = xbmc.getSkinDir()
    try:
        with open(os.path.join(PROFILE_PATH, 'skin_fonts.ini'), "r") as f:
            lines = f.readlines()
            lines.remove(currentSkin+'\n')
            with open(os.path.join(PROFILE_PATH, 'skin_fonts.ini'), "w") as new_f:
                for line in lines:        
                    new_f.write(line)
    except:
        None

elif len(sys.argv) > 1 and sys.argv[1] == 'DeleteSkins':
    Skin.deleteCustomSkins(True)
elif len(sys.argv) > 1 and sys.argv[1] == 'RestoreFont':
    Skin.restoreFont(True)
