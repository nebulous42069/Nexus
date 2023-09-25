import xbmc
import xbmcaddon
import xbmcgui

import os
import time

from xml.etree import ElementTree

from resources.libs.common.config import CONFIG
from resources.libs.common import logging
from resources.libs.common import tools

ORDER = ['seren',
         'fen',
         'ezra',
         'coal',
         'pov',
         'umb',
         'shadow',
         'ghost',
         'base19',
         'unleashed',
         'chains',
         'twisted',
         'md',
         'asgard',
         'patriot',
         'blackl',
         'metv',
         'aliunde',
         'acctmgr',
         'myact',
         'rurl']

DEBRIDID = {
    'seren': {
        'name'     : 'Seren',
        'plugin'   : 'plugin.video.seren',
        'saved'    : 'seren',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.seren'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.seren/resources/images', 'ico-seren-3.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.seren/resources/images', 'fanart-seren-3.png'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD, 'seren'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.seren', 'settings.xml'),
        'default_rd'  : 'rd.username',
        'default_pm'  : 'premiumize.username',
        'default_ad'  : 'alldebrid.username',
        'data'     : [],
        'activate' : 'Addon.OpenSettings(plugin.video.seren)'},
    'fen': {
        'name'     : 'Fen',
        'plugin'   : 'plugin.video.fen',
        'saved'    : 'fen',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.fen'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.fen/resources/media/', 'fen_icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.fen/resources/media/', 'fen_fanart.png'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD, 'fen'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.fen', 'settings.xml'),
        'default_rd'  : 'rd.account_id',
        'default_pm'  : 'pm.account_id',
        'default_ad'  : 'ad.account_id',
        'data'     : [],
        'activate' : 'Addon.OpenSettings(plugin.video.fen)'},
    'ezra': {
        'name'     : 'Ezra',
        'plugin'   : 'plugin.video.ezra',
        'saved'    : 'ezra',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.ezra'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.ezra', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.ezra', 'fanart.png'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD, 'ezra'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.ezra', 'settings.xml'),
        'default_rd'  : 'rd.username',
        'default_pm'  : 'pm.account_id',
        'default_ad'  : 'ad.account_id',
        'data'     : [],
        'activate' : 'Addon.OpenSettings(plugin.video.ezra)'},
    'coal': {
        'name'     : 'Coalition',
        'plugin'   : 'plugin.video.coalition',
        'saved'    : 'coal',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.coalition'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.coalition', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.coalition', 'fanart.png'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD, 'coal'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.coalition', 'settings.xml'),
        'default_rd'  : 'rd.username',
        'default_pm'  : 'pm.account_id',
        'default_ad'  : 'ad.account_id',
        'data'     : [],
        'activate' : 'Addon.OpenSettings(plugin.video.coalition)'},
    'pov': {
        'name'     : 'POV',
        'plugin'   : 'plugin.video.pov',
        'saved'    : 'povrd',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.pov'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.pov', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.pov', 'fanart.png'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD, 'pov_rd'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.pov', 'settings.xml'),
        'default_rd'  : 'rd.username',
        'default_pm'  : 'pm.account_id',
        'default_ad'  : 'ad.account_id',
        'data'     : [],
        'activate' : 'Addon.OpenSettings(plugin.video.pov)'},
    'umb': {
        'name'     : 'Umbrella',
        'plugin'   : 'plugin.video.umbrella',
        'saved'    : 'umb',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.umbrella'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.umbrella', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.umbrella', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD, 'umb'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.umbrella', 'settings.xml'),
        'default_rd'  : 'realdebridusername',
        'default_pm'  : 'premiumizeusername',
        'default_ad'  : 'alldebridusername',
        'data'     : [],
        'activate' : 'Addon.OpenSettings(plugin.video.umbrella)'},
    'shadow': {
        'name'     : 'Shadow',
        'plugin'   : 'plugin.video.shadow',
        'saved'    : 'shadow',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.shadow'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.shadow', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.shadow', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD, 'shadow'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.shadow', 'settings.xml'),
        'default_rd'  : 'rd.client_id',
        'default_pm'  : 'premiumize.token',
        'default_ad'  : 'alldebrid.username',
        'data'     : [],
        'activate' : 'Addon.OpenSettings(plugin.video.shadow)'},
    'base19': {
        'name'     : 'Base 19',
        'plugin'   : 'plugin.video.base19',
        'saved'    : 'base19',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.base19'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.base19', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.base19', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD, 'base19'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.base19', 'settings.xml'),
        'default_rd'  : 'rd.client_id',
        'default_pm'  : 'premiumize.token',
        'default_ad'  : 'alldebrid.username',
        'data'     : [],
        'activate' : 'Addon.OpenSettings(plugin.video.base19)'},
    'ghost': {
        'name'     : 'Ghost',
        'plugin'   : 'plugin.video.ghost',
        'saved'    : 'ghost',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.ghost'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.ghost', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.ghost', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD, 'ghost'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.ghost', 'settings.xml'),
        'default_rd'  : 'rd.client_id',
        'default_pm'  : 'premiumize.token',
        'default_ad'  : 'alldebrid.username',
        'data'     : [],
        'activate' : 'Addon.OpenSettings(plugin.video.ghost)'},
    'unleashed': {
        'name'     : 'Unleashed',
        'plugin'   : 'plugin.video.unleashed',
        'saved'    : 'unleashed',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.unleashed'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.unleashed', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.unleashed', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD, 'unleashed'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.unleashed', 'settings.xml'),
        'default_rd'  : 'rd.client_id',
        'default_pm'  : 'premiumize.token',
        'default_ad'  : 'alldebrid.username',
        'data'     : [],
        'activate' : 'Addon.OpenSettings(plugin.video.unleashed)'},
    'chains': {
        'name'     : 'Chains Reaction',
        'plugin'   : 'plugin.video.thechains',
        'saved'    : 'chains',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.thechains'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.thechains', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.thechains', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD, 'chains'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.thechains', 'settings.xml'),
        'default_rd'  : 'rd.client_id',
        'default_pm'  : 'premiumize.token',
        'default_ad'  : 'alldebrid.username',
        'data'     : [],
        'activate' : 'Addon.OpenSettings(plugin.video.thechains)'},
    'twisted': {
        'name'     : 'Twisted',
        'plugin'   : 'plugin.video.twisted',
        'saved'    : 'twisted',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.twisted'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.twisted', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.twisted', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD, 'twisted'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.twisted', 'settings.xml'),
        'default_rd'  : 'rd.client_id',
        'default_pm'  : 'premiumize.token',
        'default_ad'  : 'alldebrid.username',
        'data'     : [],
        'activate' : 'Addon.OpenSettings(plugin.video.twisted)'},
    'md': {
        'name'     : 'Magic Dragon',
        'plugin'   : 'plugin.video.magicdragon',
        'saved'    : 'md',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.magicdragon'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.magicdragon', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.magicdragon', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD, 'md'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.magicdragon', 'settings.xml'),
        'default_rd'  : 'rd.client_id',
        'default_pm'  : 'premiumize.token',
        'default_ad'  : 'alldebrid.username',
        'data'     : [],
        'activate' : 'Addon.OpenSettings(plugin.video.magicdragon)'},
    'asgard': {
        'name'     : 'Asgard',
        'plugin'   : 'plugin.video.asgard',
        'saved'    : 'asgard',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.asgard'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.asgard', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.asgard', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD, 'asgard'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.asgard', 'settings.xml'),
        'default_rd'  : 'rd.client_id',
        'default_pm'  : 'premiumize.token',
        'default_ad'  : 'alldebrid.username',
        'data'     : [],
        'activate' : 'Addon.OpenSettings(plugin.video.asgard)'},
    'patriot': {
        'name'     : 'Patriot',
        'plugin'   : 'plugin.video.patriot',
        'saved'    : 'patriot',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.patriot'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.patriot', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.patriot', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD, 'patriot'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.patriot', 'settings.xml'),
        'default_rd'  : 'rd.client_id',
        'default_pm'  : 'premiumize.token',
        'default_ad'  : 'alldebrid.username',
        'data'     : [],
        'activate' : 'Addon.OpenSettings(plugin.video.patriot)'},
    'blackl': {
        'name'     : 'Black Lightning',
        'plugin'   : 'plugin.video.blacklightning',
        'saved'    : 'blackl',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.blacklightning'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.blacklightning', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.blacklightning', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD, 'blackl'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.blacklightning', 'settings.xml'),
        'default_rd'  : 'rd.client_id',
        'default_pm'  : 'premiumize.token',
        'default_ad'  : 'alldebrid.username',
        'data'     : [],
        'activate' : 'Addon.OpenSettings(plugin.video.blacklightning)'},
    'metv': {
        'name'     : 'M.E.T.V',
        'plugin'   : 'plugin.video.metv19',
        'saved'    : 'metv',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.metv19'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.metv19', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.metv19', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD, 'metv'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.metv19', 'settings.xml'),
        'default_rd'  : 'rd.client_id',
        'default_pm'  : 'premiumize.token',
        'default_ad'  : 'alldebrid.username',
        'data'     : [],
        'activate' : 'Addon.OpenSettings(plugin.video.metv19)'},
    'aliunde': {
        'name'     : 'Aliunde K19',
        'plugin'   : 'plugin.video.aliunde',
        'saved'    : 'aliunde',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.aliundek19'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.aliundek19', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.aliundek19', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD, 'aliunde'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.aliundek19', 'settings.xml'),
        'default_rd'  : 'rd.client_id',
        'default_pm'  : 'premiumize.token',
        'default_ad'  : 'alldebrid.username',
        'data'     : [],
        'activate' : 'Addon.OpenSettings(plugin.video.aliundek19)'},
    'acctmgr': {
        'name'     : 'Account Manager',
        'plugin'   : 'script.module.accountmgr',
        'saved'    : 'acctmgr',
        'path'     : os.path.join(CONFIG.ADDONS, 'script.module.accountmgr'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'script.module.accountmgr', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'script.module.accountmgr', 'fanart.png'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD, 'acctmgr'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'script.module.accountmgr', 'settings.xml'),
        'default_rd'  : 'realdebrid.username',
        'default_pm'  : 'premiumize.username',
        'default_ad'  : 'alldebrid.username',
        'data'     : [],
        'activate' : 'Addon.OpenSettings(script.module.accountmgr)'},
    'myact': {
        'name'     : 'My Accounts',
        'plugin'   : 'script.module.myaccounts',
        'saved'    : 'myact',
        'path'     : os.path.join(CONFIG.ADDONS, 'script.module.myaccounts'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'script.module.myaccounts', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'script.module.myaccounts', 'fanart.png'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD, 'myact'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'script.module.myaccounts', 'settings.xml'),
        'default_rd'  : 'realdebrid.username',
        'default_pm'  : 'premiumize.username',
        'default_ad'  : 'alldebrid.username',
        'data'     : [],
        'activate' : 'Addon.OpenSettings(script.module.myaccounts)'},
    'rurl': {
        'name'     : 'ResolveURL',
        'plugin'   : 'script.module.resolveurl',
        'saved'    : 'rurl',
        'path'     : os.path.join(CONFIG.ADDONS, 'script.module.resolveurl'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'script.module.resolveurl', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'script.module.resolveurl', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD, 'rurl'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'script.module.resolveurl', 'settings.xml'),
        'default_rd'  : 'RealDebridResolver_client_id',
        'default_pm'  : 'PremiumizeMeResolver_token',
        'default_ad'  : 'AllDebridResolver_token',
        'data'     : [],
        'activate' : 'Addon.OpenSettings(script.module.resolveurl)'}
}

def debrid_user_rd(who):
    user_rd = None
    if DEBRIDID[who]:
        if os.path.exists(DEBRIDID[who]['path']):
            try:
                add = tools.get_addon_by_id(DEBRIDID[who]['plugin'])
                user_rd = add.getSetting(DEBRIDID[who]['default_rd'])
            except:
                pass
    return user_rd

def debrid_user_pm(who):
    user_pm = None
    if DEBRIDID[who]:
        if os.path.exists(DEBRIDID[who]['path']):
            try:
                add = tools.get_addon_by_id(DEBRIDID[who]['plugin'])
                user_pm = add.getSetting(DEBRIDID[who]['default_pm'])
            except:
                pass
    return user_pm

def debrid_user_ad(who):
    user_ad = None
    if DEBRIDID[who]:
        if os.path.exists(DEBRIDID[who]['path']):
            try:
                add = tools.get_addon_by_id(DEBRIDID[who]['plugin'])
                user_ad = add.getSetting(DEBRIDID[who]['default_ad'])
            except:
                pass
    return user_ad

def debrid_it(do, who):
    if not os.path.exists(CONFIG.ADDON_DATA):
        os.makedirs(CONFIG.ADDON_DATA)
    if not os.path.exists(CONFIG.DEBRIDFOLD):
        os.makedirs(CONFIG.DEBRIDFOLD)
    if who == 'all':
        for log in ORDER:
            if os.path.exists(DEBRIDID[log]['path']):
                try:
                    addonid = tools.get_addon_by_id(DEBRIDID[log]['plugin'])
                    default = DEBRIDID[log]['default']
                    user = addonid.getSetting(default)
                    
                    update_debrid(do, log)
                except:
                    pass
            else:
                logging.log('[Debrid Info] {0}({1}) is not installed'.format(DEBRIDID[log]['name'], DEBRIDID[log]['plugin']), level=xbmc.LOGERROR)
        CONFIG.set_setting('debridnextsave', tools.get_date(days=3, formatted=True))
    else:
        if DEBRIDID[who]:
            if os.path.exists(DEBRIDID[who]['path']):
                update_debrid(do, who)
        else:
            logging.log('[Debrid Info] Invalid Entry: {0}'.format(who), level=xbmc.LOGERROR)


def clear_saved(who, over=False):
    if who == 'all':
        for debrid in DEBRIDID:
            clear_saved(debrid,  True)
    elif DEBRIDID[who]:
        file = DEBRIDID[who]['file']
        if os.path.exists(file):
            os.remove(file)
    if not over:
        xbmc.executebuiltin('Container.Refresh()')


def update_debrid(do, who):
    file = DEBRIDID[who]['file']
    settings = DEBRIDID[who]['settings']
    data = DEBRIDID[who]['data']
    addonid = tools.get_addon_by_id(DEBRIDID[who]['plugin'])
    saved = DEBRIDID[who]['saved']
    default = DEBRIDID[who]['default']
    user = addonid.getSetting(default)
    suser = CONFIG.get_setting(saved)
    name = DEBRIDID[who]['name']
    icon = DEBRIDID[who]['icon']

    if do == 'update':
        if not user == '':
            try:
                root = ElementTree.Element(saved)
                
                for setting in data:
                    debrid = ElementTree.SubElement(root, 'debrid')
                    id = ElementTree.SubElement(debrid, 'id')
                    id.text = setting
                    value = ElementTree.SubElement(debrid, 'value')
                    value.text = addonid.getSetting(setting)
                  
                tree = ElementTree.ElementTree(root)
                tree.write(file)
                
                user = addonid.getSetting(default)
                CONFIG.set_setting(saved, user)
                
                logging.log('Debrid Info Saved for {0}'.format(name), level=xbmc.LOGINFO)
            except Exception as e:
                logging.log("[Debrid Info] Unable to Update {0} ({1})".format(who, str(e)), level=xbmc.LOGERROR)
        else:
            logging.log('Debrid Info Not Registered for {0}'.format(name))
    elif do == 'restore':
        if os.path.exists(file):
            tree = ElementTree.parse(file)
            root = tree.getroot()
            
            try:
                for setting in root.findall('debrid'):
                    id = setting.find('id').text
                    value = setting.find('value').text
                    addonid.setSetting(id, value)
                
                user = addonid.getSetting(default)
                CONFIG.set_setting(saved, user)
                logging.log('Debrid Info Restored for {0}'.format(name), level=xbmc.LOGINFO)
            except Exception as e:
                logging.log("[Debrid Info] Unable to Restore {0} ({1})".format(who, str(e)), level=xbmc.LOGERROR)
        else:
            logging.log('Debrid Info Not Found for {0}'.format(name))
    elif do == 'clearaddon':
        logging.log('{0} SETTINGS: {1}'.format(name, settings))
        if os.path.exists(settings):
            try:
                tree = ElementTree.parse(settings)
                root = tree.getroot()
                
                for setting in root.findall('setting'):
                    if setting.attrib['id'] in data:
                        logging.log('Removing Setting: {0}'.format(setting.attrib))
                        root.remove(setting)
                            
                tree.write(settings)
                
                logging.log_notify("[COLOR {0}]{1}[/COLOR]".format(CONFIG.COLOR1, name),
                                   '[COLOR {0}]Addon Data: Cleared![/COLOR]'.format(CONFIG.COLOR2),
                                   2000,
                                   icon)
            except Exception as e:
                logging.log("[Debrid Info] Unable to Clear Addon {0} ({1})".format(who, str(e)), level=xbmc.LOGERROR)
    xbmc.executebuiltin('Container.Refresh()')


def auto_update(who):
    if who == 'all':
        for log in DEBRIDID:
            if os.path.exists(DEBRIDID[log]['path']):
                auto_update(log)
    elif DEBRIDID[who]:
        if os.path.exists(DEBRIDID[who]['path']):
            u = debrid_user(who)
            su = CONFIG.get_setting(DEBRIDID[who]['saved'])
            n = DEBRIDID[who]['name']
            if not u or u == '':
                return
            elif su == '':
                debrid_it('update', who)
            elif not u == su:
                dialog = xbmcgui.Dialog()

                if dialog.yesno(CONFIG.ADDONTITLE,
                                    "Would you like to save the [COLOR {0}]Debrid Info[/COLOR] for [COLOR {1}]{2}[/COLOR]?".format(CONFIG.COLOR2, CONFIG.COLOR1, n),
                                    "Addon: [COLOR springgreen][B]{0}[/B][/COLOR]".format(u),
                                    "Saved:[/COLOR] [COLOR red][B]{0}[/B][/COLOR]".format(su) if not su == '' else 'Saved:[/COLOR] [COLOR red][B]None[/B][/COLOR]',
                                    yeslabel="[B][COLOR springreen]Save Debrid[/COLOR][/B]",
                                    nolabel="[B][COLOR red]No, Cancel[/COLOR][/B]"):
                    debrid_it('update', who)
            else:
                debrid_it('update', who)


def import_list(who):
    if who == 'all':
        for log in DEBRIDID:
            if os.path.exists(DEBRIDID[log]['file']):
                import_list(log)
    elif DEBRIDID[who]:
        if os.path.exists(DEBRIDID[who]['file']):
            file = DEBRIDID[who]['file']
            addonid = tools.get_addon_by_id(DEBRIDID[who]['plugin'])
            saved = DEBRIDID[who]['saved']
            default = DEBRIDID[who]['default']
            suser = CONFIG.get_setting(saved)
            name = DEBRIDID[who]['name']
            
            tree = ElementTree.parse(file)
            root = tree.getroot()
            
            for setting in root.findall('debrid'):
                id = setting.find('id').text
                value = setting.find('value').text
            
                addonid.setSetting(id, value)

            logging.log_notify("[COLOR {0}]{1}[/COLOR]".format(CONFIG.COLOR1, name),
                       '[COLOR {0}]Debrid Info: Imported![/COLOR]'.format(CONFIG.COLOR2))


def open_settings_debrid(who):
    addonid = tools.get_addon_by_id(DEBRIDID[who]['plugin'])
    addonid.openSettings()

