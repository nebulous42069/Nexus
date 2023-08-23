import xbmc
import xbmcaddon
import xbmcgui
import os.path
import xbmcvfs
import os
import time

from xml.etree import ElementTree

from resources.libs.common.config import CONFIG
from resources.libs.common import logging
from resources.libs.common import tools

ORDER = ['acctmgrrd',
         'serenrd',
         'ezrard',
         'fenrd',
         'povrd',
         'umbrd',
         'shadowrd',
         'ghostrd',
         'unleashedrd',
         'chainsrd',
         'twistedrd',
         'base19rd',
         'mdrd',
         'asgardrd',
         'metvrd',
         'aliunderd',
         'patriotrd',
         'adinard',
         'artemisrd',
         'dynard',
         'loonrd',
         'myactrd',
         'yactrd',
         'rurlrd']

DEBRIDID = {
    'serenrd': {
        'name'     : 'Seren',
        'plugin'   : 'plugin.video.seren',
        'saved'    : 'serenrd',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.seren'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.seren/resources/images', 'ico-seren-3.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.seren/resources/images', 'fanart-seren-3.png'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD_RD, 'seren_rd'), #Backup location
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.seren', 'settings.xml'),
        'default'  : 'rd.client_id',
        'data'     : ['rd.auth', 'rd.client_id', 'rd.expiry', 'rd.refresh', 'rd.secret', 'rd.username', 'realdebrid.enabled'],
        'activate' : 'Addon.OpenSettings(plugin.video.seren)'},
    'ezrard': {
        'name'     : 'Ezra',
        'plugin'   : 'plugin.video.ezra',
        'saved'    : 'ezrard',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.ezra'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.ezra', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.ezra', 'fanart.png'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD_RD, 'ezra_rd'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.ezra', 'settings.xml'),
        'default'  : 'rd.client_id',
        'data'     : ['rd.username', 'rd.token', 'rd.client_id', 'rd.refresh', 'rd.secret','rd.enabled'],
        'activate' : 'Addon.OpenSettings(plugin.video.ezra)'},
    'fenrd': {
        'name'     : 'Fen',
        'plugin'   : 'plugin.video.fen',
        'saved'    : 'fenrd',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.fen'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.fen/resources/media/', 'fen_icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.fen/resources/media/', 'fen_fanart.png'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD_RD, 'fen_rd'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.fen', 'settings.xml'),
        'default'  : 'rd.client_id',
        'data'     : ['rd.client_id', 'rd.refresh', 'rd.secret', 'rd.token', 'rd.account_id', 'rd.enabled'],
        'activate' : 'Addon.OpenSettings(plugin.video.fen)'},
    'povrd': {
        'name'     : 'POV',
        'plugin'   : 'plugin.video.pov',
        'saved'    : 'povrd',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.pov'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.pov', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.pov', 'fanart.png'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD_RD, 'pov_rd'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.fen', 'settings.xml'),
        'default'  : 'rd.client_id',
        'data'     : ['rd.client_id', 'rd.refresh', 'rd.secret', 'rd.token', 'rd.account_id', 'rd.enabled'],
        'activate' : 'Addon.OpenSettings(plugin.video.pov)'},
    'umbrd': {
        'name'     : 'Umbrella',
        'plugin'   : 'plugin.video.umbrella',
        'saved'    : 'umbrd',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.umbrella'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.umbrella', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.umbrella', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD_RD, 'umb_rd'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.umbrella', 'settings.xml'),
        'default'  : 'realdebrid.clientid',
        'data'     : ['realdebridusername', 'realdebridtoken', 'realdebrid.clientid', 'realdebridsecret', 'realdebridrefresh', 'realdebrid.enable'],
        'activate' : 'Addon.OpenSettings(plugin.video.umbrella)'},
    'shadowrd': {
        'name'     : 'Shadow',
        'plugin'   : 'plugin.video.shadow',
        'saved'    : 'shadowrd',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.shadow'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.shadow', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.shadow', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD_RD, 'shadow_rd'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.shadow', 'settings.xml'),
        'default'  : 'rd.client_id',
        'data'     : ['rd.expiry', 'rd.auth', 'rd.client_id', 'rd.refresh', 'rd.secret', 'debrid_select'],
        'activate' : 'Addon.OpenSettings(plugin.video.shadow)'},
    'ghostrd': {
        'name'     : 'Ghost',
        'plugin'   : 'plugin.video.ghost',
        'saved'    : 'ghostrd',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.ghost'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.ghost', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.ghost', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD_RD, 'ghost_rd'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.ghost', 'settings.xml'),
        'default'  : 'rd.client_id',
        'data'     : ['rd.expiry', 'rd.auth', 'rd.client_id', 'rd.refresh', 'rd.secret', 'debrid_select'],
        'activate' : 'Addon.OpenSettings(plugin.video.ghost)'},
    'unleashedrd': {
        'name'     : 'Unleashed',
        'plugin'   : 'plugin.video.unleashed',
        'saved'    : 'unleashedrd',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.unleashed'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.unleashed', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.unleashed', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD_RD, 'unleashed_rd'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.unleashed', 'settings.xml'),
        'default'  : 'rd.client_id',
        'data'     : ['rd.expiry', 'rd.auth', 'rd.client_id', 'rd.refresh', 'rd.secret', 'debrid_select'],
        'activate' : 'Addon.OpenSettings(plugin.video.unleashed)'},
    'chainsrd': {
        'name'     : 'Chains Reaction',
        'plugin'   : 'plugin.video.thechains',
        'saved'    : 'chainsrd',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.thechains'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.thechains', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.thechains', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD_RD, 'chains_rd'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.thechains', 'settings.xml'),
        'default'  : 'rd.client_id',
        'data'     : ['rd.expiry', 'rd.auth', 'rd.client_id', 'rd.refresh', 'rd.secret', 'debrid_select'],
        'activate' : 'Addon.OpenSettings(plugin.video.thechains)'},
    'twistedrd': {
        'name'     : 'Twisted',
        'plugin'   : 'plugin.video.twisted',
        'saved'    : 'twistedrd',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.twisted'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.twisted', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.twisted', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD_RD, 'twisted_rd'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.twisted', 'settings.xml'),
        'default'  : 'rd.client_id',
        'data'     : ['rd.expiry', 'rd.auth', 'rd.client_id', 'rd.refresh', 'rd.secret', 'debrid_select'],
        'activate' : 'Addon.OpenSettings(plugin.video.twisted)'},
    'base19rd': {
        'name'     : 'Base 19',
        'plugin'   : 'plugin.video.base19',
        'saved'    : 'base19rd',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.base19'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.base19', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.base19', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD_RD, 'base19_rd'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.base19', 'settings.xml'),
        'default'  : 'rd.client_id',
        'data'     : ['rd.expiry', 'rd.auth', 'rd.client_id', 'rd.refresh', 'rd.secret', 'debrid_select'],
        'activate' : 'Addon.OpenSettings(plugin.video.base19)'},
    'mdrd': {
        'name'     : 'Magic Dragon',
        'plugin'   : 'plugin.video.magicdragon',
        'saved'    : 'mdrd',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.magicdragon'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.magicdragon', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.magicdragon', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD_RD, 'md_rd'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.magicdragon', 'settings.xml'),
        'default'  : 'rd.client_id',
        'data'     : ['rd.expiry', 'rd.auth', 'rd.client_id', 'rd.refresh', 'rd.secret', 'debrid_select'],
        'activate' : 'Addon.OpenSettings(plugin.video.magicdragon)'},
    'asgardrd': {
        'name'     : 'Asgard',
        'plugin'   : 'plugin.video.asgard',
        'saved'    : 'asgardrd',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.asgard'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.asgard', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.asgard', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD_RD, 'asgard_rd'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.asgard', 'settings.xml'),
        'default'  : 'rd.client_id',
        'data'     : ['rd.expiry', 'rd.auth', 'rd.client_id', 'rd.refresh', 'rd.secret', 'debrid_select'],
        'activate' : 'Addon.OpenSettings(plugin.video.asgard)'},
    'metvrd': {
        'name'     : 'M.E.T.V',
        'plugin'   : 'plugin.video.metv19',
        'saved'    : 'metvrd',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.metv19'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.metv19', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.metv19', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD_RD, 'metv_rd'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.metv19', 'settings.xml'),
        'default'  : 'rd.client_id',
        'data'     : ['rd.expiry', 'rd.auth', 'rd.client_id', 'rd.refresh', 'rd.secret', 'debrid_select'],
        'activate' : 'Addon.OpenSettings(plugin.video.metv19)'},
    'aliunderd': {
        'name'     : 'Aliunde K19',
        'plugin'   : 'plugin.video.aliundek19',
        'saved'    : 'aliunderd',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.aliundek19'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.aliundek19', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.aliundek19', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD_RD, 'aliunde_rd'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.aliundek19', 'settings.xml'),
        'default'  : 'rd.client_id',
        'data'     : ['rd.expiry', 'rd.auth', 'rd.client_id', 'rd.refresh', 'rd.secret', 'debrid_select'],
        'activate' : 'Addon.OpenSettings(plugin.video.aliunde)'},
    'patriotrd': {
        'name'     : 'Patriot',
        'plugin'   : 'plugin.video.patriot',
        'saved'    : 'patriotrd',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.patriot'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.patriot', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.patriot', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD_RD, 'patriot_rd'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.patriot', 'settings.xml'),
        'default'  : 'rd.client_id',
        'data'     : ['rd.expiry', 'rd.auth', 'rd.client_id', 'rd.refresh', 'rd.secret', 'debrid_select'],
        'activate' : 'Addon.OpenSettings(plugin.video.patriot)'},
    'adinard': {
        'name'     : 'Adina',
        'plugin'   : 'plugin.video.adina',
        'saved'    : 'adinard',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.adina'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.adina', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.adina', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD_RD, 'adina_rd'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.adina', 'settings.xml'),
        'default'  : 'rd.client_id',
        'data'     : ['rd.username', 'rd.auth', 'rd.token', 'rd.client_id', 'rd.refresh', 'rd.secret'],
        'activate' : 'Addon.OpenSettings(plugin.video.adina)'},
    'artemisrd': {
        'name'     : 'Artemis',
        'plugin'   : 'plugin.video.artemis',
        'saved'    : 'artemisrd',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.artemis'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.artemis', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.artemis', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD_RD, 'artemis_rd'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.artemis', 'settings.xml'),
        'default'  : 'realdebrid.client_id',
        'data'     : ['realdebrid.username', 'realdebrid.token', 'realdebrid.client_id', 'realdebrid.refresh', 'realdebrid.secret'],
        'activate' : 'Addon.OpenSettings(plugin.video.artemis)'},
    'dynard': {
        'name'     : 'Dynasty',
        'plugin'   : 'plugin.video.dynasty',
        'saved'    : 'dynard',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.dynasty'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.dynasty', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.dynasty', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD_RD, 'dyna_rd'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.dynasty', 'settings.xml'),
        'default'  : 'realdebrid.client_id',
        'data'     : ['realdebrid.username', 'realdebrid.token', 'realdebrid.client_id', 'realdebrid.refresh', 'realdebrid.secret'],
        'activate' : 'Addon.OpenSettings(plugin.video.dynasty)'},
    'loonrd': {
        'name'     : 'Loonatics Empire',
        'plugin'   : 'plugin.video.le',
        'saved'    : 'loonrd',
        'path'     : os.path.join(CONFIG.ADDONS, 'plugin.video.le'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'plugin.video.le', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'plugin.video.le', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD_RD, 'loon_rd'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'plugin.video.le', 'settings.xml'),
        'default'  : 'realdebrid.client_id',
        'data'     : ['realdebrid.username', 'realdebrid.token', 'realdebrid.client_id', 'realdebrid.refresh', 'realdebrid.secret'],
        'activate' : 'Addon.OpenSettings(plugin.video.le)'},
    'myactrd': {
        'name'     : 'My Accounts',
        'plugin'   : 'script.module.myaccounts',
        'saved'    : 'myactrd',
        'path'     : os.path.join(CONFIG.ADDONS, 'script.module.myaccounts'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'script.module.myaccounts', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'script.module.myaccounts', 'fanart.png'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD_RD, 'myact_rd'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'script.module.myaccounts', 'settings.xml'),
        'default'  : 'realdebrid.client_id',
        'data'     : ['realdebrid.client_id', 'realdebrid.refresh', 'realdebrid.secret', 'realdebrid.token', 'realdebrid.username'],
        'activate' : 'Addon.OpenSettings(script.module.myaccounts)'},
    'yactrd': {
        'name'     : 'Your Accounts',
        'plugin'   : 'script.module.youraccounts',
        'saved'    : 'yactrd',
        'path'     : os.path.join(CONFIG.ADDONS, 'script.module.youraccounts'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'script.module.youraccounts', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'script.module.youraccounts', 'fanart.png'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD_RD, 'yact_rd'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'script.module.youraccounts', 'settings.xml'),
        'default'  : 'realdebrid.client_id',
        'data'     : ['realdebrid.client_id', 'realdebrid.refresh', 'realdebrid.secret', 'realdebrid.token', 'realdebrid.username'],
        'activate' : 'Addon.OpenSettings(script.module.youraccounts)'},
    'rurlrd': {
        'name'     : 'ResolveURL',
        'plugin'   : 'script.module.resolveurl',
        'saved'    : 'rurlrd',
        'path'     : os.path.join(CONFIG.ADDONS, 'script.module.resolveurl'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'script.module.resolveurl', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'script.module.resolveurl', 'fanart.jpg'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD_RD, 'rurl_rd'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'script.module.resolveurl', 'settings.xml'),
        'default'  : 'RealDebridResolver_client_id',
        'data'     : ['RealDebridResolver_client_id', 'RealDebridResolver_client_secret', 'RealDebridResolver_enabled', 'RealDebridResolver_refresh', 'RealDebridResolver_token', 'RealDebridResolver_cached_only'],
        'activate' : 'Addon.OpenSettings(script.module.resolveurl)'},
    'acctmgrrd': {
        'name'     : 'Account Manager',
        'plugin'   : 'script.module.accountmgr',
        'saved'    : 'acctmgrrd',
        'path'     : os.path.join(CONFIG.ADDONS, 'script.module.accountmgr'),
        'icon'     : os.path.join(CONFIG.ADDONS, 'script.module.accountmgr', 'icon.png'),
        'fanart'   : os.path.join(CONFIG.ADDONS, 'script.module.accountmgr', 'fanart.png'),
        'file'     : os.path.join(CONFIG.DEBRIDFOLD_RD, 'acctmgr_rd'),
        'settings' : os.path.join(CONFIG.ADDON_DATA, 'script.module.accountmgr', 'settings.xml'),
        'default'  : 'realdebrid.username',
        'data'     : ['realdebrid.client_id', 'realdebrid.refresh', 'realdebrid.secret', 'realdebrid.token', 'realdebrid.username'],
        'activate' : 'Addon.OpenSettings(script.module.accountmgr)'}
}


def debrid_user(who):
    user = None
    if DEBRIDID[who]:
        if os.path.exists(DEBRIDID[who]['path']):
            try:
                add = tools.get_addon_by_id(DEBRIDID[who]['plugin'])
                user = add.getSetting(DEBRIDID[who]['default'])
            except:
                pass
    return user


def debrid_it(do, who):
    if not os.path.exists(CONFIG.ADDON_DATA):
        os.makedirs(CONFIG.ADDON_DATA)
    if not os.path.exists(CONFIG.DEBRIDFOLD_RD):
        os.makedirs(CONFIG.DEBRIDFOLD_RD)
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
    elif do == 'wipeaddon':
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

