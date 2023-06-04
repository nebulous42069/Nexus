import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import os.path
import xbmcvfs
import sys
try:  # Python 3
    from urllib.parse import parse_qsl
except ImportError:  # Python 2
    from urlparse import parse_qsl
from resources.libs.common.config import CONFIG
from resources.libs.common import logging
from resources.libs.common import tools
from resources.libs.gui import menu
from resources.libs import var

addon = xbmcaddon.Addon
addonObject = addon('script.module.acctview')
addonInfo = addonObject.getAddonInfo
getLangString = xbmcaddon.Addon().getLocalizedString
condVisibility = xbmc.getCondVisibility
execute = xbmc.executebuiltin
monitor = xbmc.Monitor()
transPath = xbmcvfs.translatePath
joinPath = os.path.join
dialog = xbmcgui.Dialog()

amgr_icon = joinPath(os.path.join(xbmcaddon.Addon('script.module.acctview').getAddonInfo('path'), 'resources', 'icons'), 'accountmgr.png')
rd_icon = joinPath(os.path.join(xbmcaddon.Addon('script.module.acctview').getAddonInfo('path'), 'resources', 'icons'), 'realdebrid.png')
pm_icon = joinPath(os.path.join(xbmcaddon.Addon('script.module.acctview').getAddonInfo('path'), 'resources', 'icons'), 'premiumize.png')
ad_icon = joinPath(os.path.join(xbmcaddon.Addon('script.module.acctview').getAddonInfo('path'), 'resources', 'icons'), 'alldebrid.png')
trakt_icon = joinPath(os.path.join(xbmcaddon.Addon('script.module.acctview').getAddonInfo('path'), 'resources', 'icons'), 'trakt.png')

class Router:
    def __init__(self):
        self.route = None
        self.params = {}

    def _log_params(self, paramstring):
        _url = sys.argv[0]

        self.params = dict(parse_qsl(paramstring))

        logstring = '{0}: '.format(_url)
        for param in self.params:
            logstring += '[ {0}: {1} ] '.format(param, self.params[param])

        logging.log(logstring, level=xbmc.LOGDEBUG)

        return self.params

    def dispatch(self, handle, paramstring):
        self._log_params(paramstring)

        mode = self.params['mode'] if 'mode' in self.params else None
        url = self.params['url'] if 'url' in self.params else None
        name = self.params['name'] if 'name' in self.params else None
        action = self.params['action'] if 'action' in self.params else None

        # MAIN MENU
        if mode is None:
            self._finish(handle)
                 
        elif mode == 'trakt':  # Trakt Account Viewer
            menu.trakt_menu()
            self._finish(handle)
            
        elif mode == 'realdebrid':  # Real-Debrid Account Viewer
            menu.debrid_menu()
            self._finish(handle)

        elif mode == 'premiumize':  # Premiumize Account Viewer
            menu.premiumize_menu()
            self._finish(handle)

        elif mode == 'alldebrid':  # All-Debird Account Viewer
            menu.alldebrid_menu()
            self._finish(handle)

        elif mode == 'allaccts':  # All Accounts Viewer
            menu.all_accounts_menu()
            self._finish(handle)
            

            
        # TRAKT MANAGER
        elif mode == 'savetrakt':  # Save Trakt Data
            from resources.libs import traktit
            traktit.trakt_it('update', name)
        elif mode == 'savetrakt_myacct':  # Save Trakt Data via Myacct settings menu
            from resources.libs import traktit
            traktit.trakt_it('update', name)
            xbmcgui.Dialog().notification('Account Manager', 'Trakt Backup Complete!', trakt_icon, 3000)
        elif mode == 'restoretrakt':  # Recover All Saved Trakt Data
            from resources.libs import traktit
            traktit.trakt_it_restore('restore', name)
            xbmcgui.Dialog().notification('Account Manager', 'Trakt Data Restored!', trakt_icon, 3000)
        elif mode == 'addontrakt':  # Clear All Addon Trakt Data
            from resources.libs import traktit
            traktit.trakt_it_revoke('clearaddon', name)
        elif mode == 'cleartrakt':  # Clear All Saved Trakt Data
            from resources.libs import traktit
            traktit.clear_saved(name)
        elif mode == 'opentraktsettings':  # Authorize Trakt
            from resources.libs import traktit
            traktit.open_settings_trakt(name)
            xbmc.executebuiltin('Container.Refresh()')
        elif mode == 'updatetrakt':  # Update Saved Trakt Data
            from resources.libs import traktit
            traktit.auto_update('all')
            
        # DEBRID MANAGER RD
        elif mode == 'savedebrid_rd':  # Save Debrid Data
            from resources.libs import debridit_rd
            debridit_rd.debrid_it('update', name)
        elif mode == 'savedebrid_myacct_rd':  # Save Debrid Datavia Myacct settings menu
            from resources.libs import debridit_rd
            debridit_rd.debrid_it('update', name)
            xbmcgui.Dialog().notification('Account Manager', 'Real-Debrid Backup Complete!', rd_icon, 3000)
        elif mode == 'restoredebrid_rd':  # Recover All Saved Debrid Data
            from resources.libs import debridit_rd
            debridit_rd.debrid_it('restore', name)
            xbmcgui.Dialog().notification('Account Manager', 'Real-Debrid Data Restored!', rd_icon, 3000)
        elif mode == 'addondebrid_rd':  # Clear All Addon Debrid Data
            from resources.libs import debridit_rd
            debridit_rd.debrid_it('clearaddon', name)
        elif mode == 'cleardebrid_rd':  # Clear All Saved Debrid Data
            from resources.libs import debridit_rd
            debridit_rd.clear_saved(name)
        elif mode == 'opendebridsettings_rd':  # Authorize Debrid
            from resources.libs import debridit_rd
            debridit_rd.open_settings_debrid(name)
            xbmc.executebuiltin('Container.Refresh()')
        elif mode == 'updatedebrid_rd':  # Update Saved Debrid Data
            from resources.libs import debridit_rd
            debridit_rd.auto_update('all')

        # DEBRID MANAGER PM
        elif mode == 'savedebrid_pm':  # Save Debrid Data
            from resources.libs import debridit_pm
            debridit_pm.debrid_it('update', name)
        elif mode == 'savedebrid_myacct_pm':  # Save Debrid Data via Myacct settings menu
            from resources.libs import debridit_pm
            debridit_pm.debrid_it('update', name)
            xbmcgui.Dialog().notification('Account Manager', 'Premiumize Backup Complete!', pm_icon, 3000)
        elif mode == 'restoredebrid_pm':  # Recover All Saved Debrid Data
            from resources.libs import debridit_pm
            debridit_pm.debrid_it('restore', name)
            xbmcgui.Dialog().notification('Account Manager', 'Premiumize Data Restored!', pm_icon, 3000)
        elif mode == 'addondebrid_pm':  # Clear All Addon Debrid Data
            from resources.libs import debridit_pm
            debridit_pm.debrid_it('clearaddon', name)
        elif mode == 'cleardebrid_pm':  # Clear All Saved Debrid Data
            from resources.libs import debridit_pm
            debridit_pm.clear_saved(name)
        elif mode == 'opendebridsettings_pm':  # Authorize Debrid
            from resources.libs import debridit_pm
            debridit_pm.open_settings_debrid(name)
            xbmc.executebuiltin('Container.Refresh()')
        elif mode == 'updatedebrid_pm':  # Update Saved Debrid Data
            from resources.libs import debridit_pm
            debridit_pm.auto_update('all')

        # DEBRID MANAGER AD
        elif mode == 'savedebrid_ad':  # Save Debrid Data
            from resources.libs import debridit_ad
            debridit_ad.debrid_it('update', name)
        elif mode == 'savedebrid_myacct_ad':  # Save Debrid Data via Myacct settings menu
            from resources.libs import debridit_ad
            debridit_ad.debrid_it('update', name)
            xbmcgui.Dialog().notification('Account Manager', 'All-Debrid Backup Complete!', ad_icon, 3000)
        elif mode == 'restoredebrid_ad':  # Recover All Saved Debrid Data
            from resources.libs import debridit_ad
            debridit_ad.debrid_it('restore', name)
            xbmcgui.Dialog().notification('Account Manager', 'All-Debrid Data Restored!', ad_icon, 3000)
        elif mode == 'addondebrid_ad':  # Clear All Addon Debrid Data
            from resources.libs import debridit_ad
            debridit_ad.debrid_it('clearaddon', name)
        elif mode == 'cleardebrid_ad':  # Clear All Saved Debrid Data
            from resources.libs import debridit_ad
            debridit_ad.clear_saved(name)
        elif mode == 'opendebridsettings_ad':  # Authorize Debrid
            from resources.libs import debridit_ad
            debridit_ad.open_settings_debrid(name)
            xbmc.executebuiltin('Container.Refresh()')
        elif mode == 'updatedebrid_ad':  # Update Saved Debrid Data
            from resources.libs import debridit_ad
            debridit_ad.auto_update('all')
            
        # REVOKE ALL DEBRID ACCOUNTS
        elif mode == 'revokeall':  # Clear Addon Data for all Debrid services
            from resources.libs import debridit_rd, debridit_pm, debridit_ad 
            debridit_rd.debrid_it('wipeaddon', name)
            debridit_pm.debrid_it('wipeaddon', name)
            debridit_ad.debrid_it('wipeaddon', name)
            xbmcgui.Dialog().notification('Account Manager', 'All Add-ons Revoked!', amgr_icon, 3000)
            
        #BACKUP ALL DEBRID ACCOUNTS
        elif mode == 'backupall':  # Save Debrid Data via Myacct settings menu
            if str(var.chk_accountmgr_tk_rd) != '' or str(var.chk_accountmgr_tk_pm) != '' or str(var.chk_accountmgr_tk_pm) != '': #Skip sync if no Debrid accounts authorized
                from resources.libs import debridit_rd, debridit_pm, debridit_ad
                debridit_rd.debrid_it('update', name)
                debridit_pm.debrid_it('update', name)
                debridit_ad.debrid_it('update', name)
                xbmcgui.Dialog().notification('Account Manager', 'Backup Complete!', amgr_icon, 3000)
            if str(var.chk_accountmgr_tk_rd) == '': #If Account Mananger is not Authorized notify user
                xbmcgui.Dialog().notification('Account Manager', 'No Debrid Accounts Active!', amgr_icon, 3000)
            
        #RESTORE ALL DEBRID ACCOUNTS
        elif mode == 'restoreall':  # Recover All Saved Debrid Data
            from resources.libs import debridit_rd, debridit_pm, debridit_ad
            debridit_rd.debrid_it('restore', name)
            debridit_pm.debrid_it('restore', name)
            debridit_ad.debrid_it('restore', name)
            xbmcgui.Dialog().notification('Account Manager', 'Data Restored!', amgr_icon, 3000)
            
        #CLEAR ALL SAVED DATA FOR DEBRID ACCOUNTS
        elif mode == 'clearall':  # Clear All Saved Debrid Data
            from resources.libs import debridit_rd, debridit_pm, debridit_ad
            debridit_rd.clear_all_saved(name)
            debridit_pm.clear_all_saved(name)
            debridit_ad.clear_all_saved(name)
            xbmcgui.Dialog().notification('Account Manager', 'Data Cleared!', amgr_icon, 3000)

        # REVOKE/WIPE CLEAN ALL ADD-ONS
        elif mode == 'wipeclean':  # Clear data and restore stock API Keys for all add-ons
            yes = dialog.yesno('Account Manager', 'WARNING! This will completely wipe all data and restore add-ons to default settings. Click proceed to continue or cancel to quit.', 'Cancel', 'Proceed')
            if yes:
                from resources.libs import traktit, debridit_rd, debridit_pm, debridit_ad
                traktit.trakt_it_revoke('wipeaddon', name)
                debridit_rd.debrid_it('wipeaddon', name)
                debridit_pm.debrid_it('wipeaddon', name)
                debridit_ad.debrid_it('wipeaddon', name)
                debridit_rd.clear_all_saved(name)
                debridit_pm.clear_all_saved(name)
                debridit_ad.clear_all_saved(name)
                xbmcgui.Dialog().notification('Account Manager', 'All Data Cleared!', amgr_icon, 3000)

            
    def _finish(self, handle):
        from resources.libs.common import directory
        
        directory.set_view()
        
        xbmcplugin.setContent(handle, 'files')
        xbmcplugin.endOfDirectory(handle)                       
