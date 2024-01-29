# -*- coding: utf-8 -*-
import time
from windows.base_window import open_window, create_window
from caches.settings_cache import get_setting
from scrapers import external, folders
from modules import debrid, kodi_utils, settings, metadata, watched_status
from modules.player import FenLightPlayer
from modules.source_utils import get_cache_expiry, make_alias_dict
from modules.utils import clean_file_name, string_to_float, safe_string, remove_accents, get_datetime, append_module_to_syspath, manual_function_import, manual_module_import
# logger = kodi_utils.logger

get_icon, notification, sleep, int_window_prop = kodi_utils.get_icon, kodi_utils.notification, kodi_utils.sleep, kodi_utils.int_window_prop
select_dialog, confirm_dialog, close_all_dialog = kodi_utils.select_dialog, kodi_utils.confirm_dialog, kodi_utils.close_all_dialog
json, show_busy_dialog, hide_busy_dialog, xbmc_player = kodi_utils.json, kodi_utils.show_busy_dialog, kodi_utils.hide_busy_dialog, kodi_utils.xbmc_player
Thread, get_property, set_property, clear_property = kodi_utils.Thread, kodi_utils.get_property, kodi_utils.set_property, kodi_utils.clear_property
auto_play, active_internal_scrapers, provider_sort_ranks, audio_filters = settings.auto_play, settings.active_internal_scrapers, settings.provider_sort_ranks, settings.audio_filters
check_prescrape_sources, external_scraper_info, auto_resume = settings.check_prescrape_sources, settings.external_scraper_info, settings.auto_resume
store_resolved_to_cloud, source_folders_directory, watched_indicators = settings.store_resolved_to_cloud, settings.source_folders_directory, settings.watched_indicators
quality_filter, sort_to_top = settings.quality_filter, settings.sort_to_top
scraping_settings, include_prerelease_results, auto_rescrape_with_all = settings.scraping_settings, settings.include_prerelease_results, settings.auto_rescrape_with_all
ignore_results_filter, results_sort_order, results_format, filter_status = settings.ignore_results_filter, settings.results_sort_order, settings.results_format, settings.filter_status
autoplay_next_episode, autoscrape_next_episode, limit_resolve = settings.autoplay_next_episode, settings.autoscrape_next_episode, settings.limit_resolve
debrid_enabled = debrid.debrid_enabled
erase_bookmark, clear_local_bookmarks = watched_status.erase_bookmark, watched_status.clear_local_bookmarks
get_progress_percent, get_bookmarks = watched_status.get_progress_percent, watched_status.get_bookmarks
internal_include_list = ['easynews', 'pm_cloud', 'rd_cloud', 'ad_cloud']
external_exclude_list = ['easynews', 'gdrive', 'library', 'filepursuit', 'plexshare']
sd_check = ('SD', 'CAM', 'TELE', 'SYNC')
rd_info, pm_info, ad_info = ('apis.real_debrid_api', 'RealDebridAPI'), ('apis.premiumize_api', 'PremiumizeAPI'), ('apis.alldebrid_api', 'AllDebridAPI')
debrids = {'Real-Debrid': rd_info, 'rd_cloud': rd_info, 'rd_browse': rd_info, 'Premiumize.me': pm_info, 'pm_cloud': pm_info, 'pm_browse': pm_info,
			'AllDebrid': ad_info, 'ad_cloud': ad_info, 'ad_browse': ad_info}
debrid_providers = ('Real-Debrid', 'Premiumize.me', 'AllDebrid')
quality_ranks = {'4K': 1, '1080p': 2, '720p': 3, 'SD': 4, 'SCR': 5, 'CAM': 5, 'TELE': 5}
cloud_scrapers, folder_scrapers = ('rd_cloud', 'pm_cloud', 'ad_cloud'), ('folder1', 'folder2', 'folder3', 'folder4', 'folder5')
default_internal_scrapers = ('easynews', 'rd_cloud', 'pm_cloud', 'ad_cloud', 'folders')
main_line = '%s[CR]%s[CR]%s'
scraper_timeout = 25

class Sources():
	def __init__(self):
		self.params = {}
		self.prescrape_scrapers, self.prescrape_threads, self.prescrape_sources, self.uncached_results = [], [], [], []
		self.threads, self.providers, self.sources, self.internal_scraper_names, self.remove_scrapers = [], [], [], [], ['external']
		self.post_results_processed, self.clear_properties, self.filters_ignored, self.active_folders, self.resolve_dialog_made = False, True, False, False, False
		self.sources_total = self.sources_4k = self.sources_1080p = self.sources_720p = self.sources_sd = 0
		self.prescrape, self.disabled_ext_ignored, self.default_ext_only = 'true', 'false', 'false'
		self.ext_name, self.ext_folder, self.provider_defaults, self.ext_sources = '', '', [], None
		self.progress_dialog, self.progress_thread = None, None
		self.playing_filename = ''
		self.count_tuple = (('sources_4k', '4K', self._quality_length), ('sources_1080p', '1080p', self._quality_length), ('sources_720p', '720p', self._quality_length),
							('sources_sd', '', self._quality_length_sd), ('sources_total', '', self._quality_length_final))

	def playback_prep(self, params=None):
		hide_busy_dialog()
		if params: self.params = params
		params_get = self.params.get
		self.play_type, self.background, self.prescrape = params_get('play_type', ''), params_get('background', 'false') == 'true', params_get('prescrape', self.prescrape) == 'true'
		self.random, self.random_continual = params_get('random', 'false') == 'true', params_get('random_continual', 'false') == 'true'
		if self.play_type:
			if self.play_type == 'autoplay_nextep': self.autoplay_nextep, self.autoscrape_nextep = True, False
			elif self.play_type == 'random_continual': self.autoplay_nextep, self.autoscrape_nextep = False, False
			else: self.autoplay_nextep, self.autoscrape_nextep = False, True
		else: self.autoplay_nextep, self.autoscrape_nextep = autoplay_next_episode(), autoscrape_next_episode()
		self.autoscrape = self.autoscrape_nextep and self.background
		self.auto_rescrape_with_all = auto_rescrape_with_all()
		self.nextep_settings, self.disable_autoplay_next_episode = params_get('nextep_settings', {}), params_get('disable_autoplay_next_episode', 'false') == 'true'
		self.ignore_scrape_filters = params_get('ignore_scrape_filters', 'false') == 'true'
		self.disabled_ext_ignored = params_get('disabled_ext_ignored', self.disabled_ext_ignored) == 'true'
		self.default_ext_only = params_get('default_ext_only', self.default_ext_only) == 'true'
		self.folders_ignore_filters = get_setting('fenlight.results.folders_ignore_filters', 'false') == 'true'
		self.filter_size = get_setting('fenlight.results.filter_size') == 'true'
		self.media_type, self.tmdb_id = params_get('media_type'), params_get('tmdb_id')
		self.custom_title, self.custom_year = params_get('custom_title', None), params_get('custom_year', None)
		self.custom_season, self.custom_episode = params_get('custom_season', None), params_get('custom_episode', None)
		if 'autoplay' in self.params: self.autoplay = params_get('autoplay', 'false') == 'true'
		else: self.autoplay = auto_play(self.media_type)
		if 'season' in self.params: self.season = int(params_get('season'))
		else: self.season = ''
		if 'episode' in self.params: self.episode = int(params_get('episode'))
		else: self.episode = ''
		self.get_meta()
		self.determine_scrapers_status()
		self.sleep_time, self.provider_sort_ranks, self.scraper_settings = 100, provider_sort_ranks(), scraping_settings()
		self.include_prerelease_results, self.ignore_results_filter, self.limit_resolve = include_prerelease_results(), ignore_results_filter(), limit_resolve()
		self.filter_hevc, self.filter_hdr = filter_status('hevc'), filter_status('hdr')
		self.filter_dv, self.filter_av1, self.filter_audio = filter_status('dv'), filter_status('av1'), 3
		self.hevc_filter_key, self.hdr_filter_key, self.dolby_vision_filter_key, self.av1_filter_key = '[B]HEVC[/B]', '[B]HDR[/B]', '[B]D/VISION[/B]', '[B]AV1[/B]'
		self.audio_filter_key = audio_filters()
		self.sort_function, self.quality_filter = results_sort_order(), self._quality_filter()
		self.hybrid_allowed = self.filter_hdr in (0, 2)
		self.include_unknown_size = get_setting('fenlight.results.include.unknown.size', 'false') == 'true'
		self.include_3D_results = get_setting('fenlight.include_3d_results', 'true') == 'true'
		self.make_search_info()
		if self.autoscrape: self.autoscrape_nextep_handler()
		else: return self.get_sources()

	def determine_scrapers_status(self):
		self.active_internal_scrapers = active_internal_scrapers()
		if not 'external' in self.active_internal_scrapers and (self.disabled_ext_ignored or self.default_ext_only): self.active_internal_scrapers.append('external')
		self.active_external = 'external' in self.active_internal_scrapers
		if self.active_external:
			self.debrid_enabled = debrid_enabled()
			if not self.debrid_enabled: return self.disable_external()
			self.ext_folder, self.ext_name = external_scraper_info()
			if not self.ext_folder or not self.ext_name: return self.disable_external()

	def get_sources(self):
		if not self.progress_dialog and not self.background: self._make_progress_dialog()
		results = []
		if self.prescrape and any(x in self.active_internal_scrapers for x in default_internal_scrapers):
			if self.prepare_internal_scrapers():
				results = self.collect_prescrape_results()
				if results: results = self.process_results(results)
		if not results:
			self.prescrape = False
			self.prepare_internal_scrapers()
			if self.active_external:
				self.activate_external_providers()
			elif not self.active_internal_scrapers: self._kill_progress_dialog()
			self.orig_results = self.collect_results()
			if not self.orig_results and not self.active_external: self._kill_progress_dialog()
			results = self.process_results(self.orig_results)
		if not results: return self._process_post_results()
		if self.autoscrape: return results
		else: return self.play_source(results)

	def collect_results(self):
		self.sources.extend(self.prescrape_sources)
		threads_append = self.threads.append
		if self.active_folders: self.append_folder_scrapers(self.providers)
		self.providers.extend(self.internal_sources())
		if self.providers:
			for i in self.providers: threads_append(Thread(target=self.activate_providers, args=(i[0], i[1], False), name=i[2]))
			[i.start() for i in self.threads]
		if self.active_external or self.background:
			if self.active_external:
				self.external_args = (self.meta, self.external_providers, self.debrid_enabled, self.internal_scraper_names,
										self.prescrape_sources, self.progress_dialog, self.disabled_ext_ignored)
				self.activate_providers('external', external, False)
			if self.background: [i.join() for i in self.threads]
		elif self.active_internal_scrapers: self.scrapers_dialog()
		return self.sources

	def collect_prescrape_results(self):
		threads_append = self.prescrape_threads.append
		if self.active_folders:
			if self.autoplay or check_prescrape_sources('folders', self.media_type):
				self.append_folder_scrapers(self.prescrape_scrapers)
				self.remove_scrapers.append('folders')
		self.prescrape_scrapers.extend(self.internal_sources(True))
		if not self.prescrape_scrapers: return []
		for i in self.prescrape_scrapers: threads_append(Thread(target=self.activate_providers, args=(i[0], i[1], True), name=i[2]))
		[i.start() for i in self.prescrape_threads]
		self.remove_scrapers.extend(i[2] for i in self.prescrape_scrapers)
		if self.background: [i.join() for i in self.prescrape_threads]
		else: self.scrapers_dialog()
		return self.prescrape_sources

	def process_results(self, results):
		if self.prescrape: self.all_scrapers = self.active_internal_scrapers
		else:
			self.all_scrapers = list(set(self.active_internal_scrapers + self.remove_scrapers))
			clear_property('fs_filterless_search')
		self.uncached_results = self.sort_results([i for i in results if 'Uncached' in i.get('cache_provider', '')])
		results = [i for i in results if not i in self.uncached_results]
		if self.ignore_scrape_filters:
			self.filters_ignored = True
			results = self.sort_results(results)
			results = self._sort_first(results)
		else:
			results = self.filter_results(results)
			results = self.sort_results(results)
			results = self._special_filter(results, self.audio_filter_key, self.filter_audio)
			results = self._special_filter(results, self.hdr_filter_key, self.filter_hdr)
			results = self._special_filter(results, self.dolby_vision_filter_key, self.filter_dv)
			results = self._special_filter(results, self.av1_filter_key, self.filter_av1)
			results = self._special_filter(results, self.hevc_filter_key, self.filter_hevc)
			results = self._sort_first(results)
		return results

	def filter_results(self, results):
		if self.folders_ignore_filters:
			folder_results = [i for i in results if i['scrape_provider'] == 'folders']
			results = [i for i in results if not i in folder_results]
		else: folder_results = []
		results = [i for i in results if i['quality'] in self.quality_filter]
		if not self.include_3D_results: results = [i for i in results if not '3D' in i['extraInfo']]
		if self.filter_size:
			min_size = 0.00 if self.include_unknown_size else 0.02
			duration = self.meta['duration'] or (5400 if self.media_type == 'movie' else 2400)
			max_size = ((0.125 * (0.90 * string_to_float(get_setting('fenlight.results.line_speed', '20'), '20'))) * duration)/1000
			results = [i for i in results if i['scrape_provider'] == 'folders' or min_size <= i['size'] <= max_size]
		results += folder_results
		return results

	def sort_results(self, results):
		def _add_keys(item):
			provider = item['scrape_provider']
			if provider == 'external': account_type = item['debrid'].lower()
			else: account_type = provider.lower()
			item['provider_rank'] = self._get_provider_rank(account_type)
			item['quality_rank'] = self._get_quality_rank(item.get('quality', 'SD'))
		for item in results: _add_keys(item)
		results.sort(key=self.sort_function)
		results = self._sort_uncached_results(results)
		return results

	def prepare_internal_scrapers(self):
		if self.active_external and len(self.active_internal_scrapers) == 1: return
		active_internal_scrapers = [i for i in self.active_internal_scrapers if not i in self.remove_scrapers]
		if self.prescrape and not self.active_external and all([check_prescrape_sources(i, self.media_type) for i in active_internal_scrapers]): return False
		if 'folders' in active_internal_scrapers:
			self.folder_info = [i for i in self.get_folderscraper_info() if source_folders_directory(self.media_type, i[1])]
			if self.folder_info:
				self.active_folders = True
				self.internal_scraper_names = [i for i in active_internal_scrapers if not i == 'folders'] + [i[0] for i in self.folder_info]
			else: self.internal_scraper_names = [i for i in active_internal_scrapers if not i == 'folders']
		else:
			self.folder_info = []
			self.internal_scraper_names = active_internal_scrapers[:]
		self.active_internal_scrapers = active_internal_scrapers
		if self.clear_properties: self._clear_properties()
		return True

	def activate_providers(self, module_type, function, prescrape):
		sources = self._get_module(module_type, function).results(self.search_info)
		if not sources: return
		if prescrape: self.prescrape_sources.extend(sources)
		else: self.sources.extend(sources)

	def activate_external_providers(self):
		if not self.import_external_scrapers(): return self.disable_external('Error Importing External Module')
		self.external_providers = self.external_sources()
		if not self.external_providers: self.disable_external('No External Providers Enabled')
	
	def import_external_scrapers(self):
		try:
			append_module_to_syspath('special://home/addons/%s/lib' % self.ext_folder)
			self.ext_sources = manual_module_import('%s.sources_%s' % (self.ext_name, self.ext_name))
			self.provider_defaults = [k.split('.')[1] for k, v in manual_function_import('%s.modules.control' % self.ext_name, 'getProviderDefaults')().items() if v == 'true']
		except: return False
		return True

	def disable_external(self, line1=''):
		if line1: notification(line1, 2000)
		try: self.active_internal_scrapers.remove('external')
		except: pass
		self.active_external, self.external_providers = False, []

	def internal_sources(self, prescrape=False):
		active_sources = [i for i in self.active_internal_scrapers if i in internal_include_list]
		try: sourceDict = [('internal', manual_function_import('scrapers.%s' % i, 'source'), i) for i in active_sources \
												if not (prescrape and not check_prescrape_sources(i, self.media_type))]
		except: sourceDict = []
		return sourceDict

	def external_sources(self):
		try:
			all_sources = self.ext_sources.total_providers['torrents']
			if self.disabled_ext_ignored: active_sources = all_sources
			elif self.default_ext_only: active_sources = [i for i in self.provider_defaults if i in all_sources]
			else: active_sources = [i for i in all_sources if json.loads(get_property('%s_settings' % self.ext_name)).get('provider.%s' % i, 'false') == 'true']
			sourceDict = [(i, manual_function_import('%s.sources_%s.%s.%s' % (self.ext_name, self.ext_name, 'torrents', i), 'source')) for i in active_sources]
		except: sourceDict = self.legacy_external_sources()
		return sourceDict

	def legacy_external_sources(self):
		try: sourceDict = manual_function_import(self.ext_name, 'sources')(specified_folders=['torrents'], ret_all=self.disabled_ext_ignored)
		except: sourceDict = []
		return sourceDict

	def folder_sources(self):
		def import_info():
			for item in self.folder_info:
				scraper_name = item[0]
				module = manual_function_import('scrapers.folders', 'source')
				yield ('folders', (module, (item[1], scraper_name, item[2])), scraper_name)
		sourceDict = list(import_info())
		try: sourceDict = list(import_info())
		except: sourceDict = []
		return sourceDict

	def play_source(self, results):
		if self.background or self.autoplay: return self.play_file(results)
		return self.display_results(results)

	def append_folder_scrapers(self, current_list):
		current_list.extend(self.folder_sources())

	def get_folderscraper_info(self):
		folder_info = [(get_setting('fenlight.%s.display_name' % i), i, source_folders_directory(self.media_type, i)) for i in folder_scrapers]
		return [i for i in folder_info if not i[0] in (None, 'None', '') and i[2]]

	def scrapers_dialog(self):
		def _scraperDialog():
			monitor = kodi_utils.monitor
			start_time = time.time()
			while not self.progress_dialog.iscanceled() and not monitor.abortRequested():
				try:
					remaining_providers = [x.getName() for x in _threads if x.is_alive() is True]
					self._process_internal_results()
					current_progress = max((time.time() - start_time), 0)
					line1 = ', '.join(remaining_providers).upper()
					percent = int((current_progress/float(scraper_timeout))*100)
					self.progress_dialog.update_scraper(self.sources_sd, self.sources_720p, self.sources_1080p, self.sources_4k, self.sources_total, line1, percent)
					sleep(self.sleep_time)
					if len(remaining_providers) == 0: break
					if percent >= 100: break
				except:	return self._kill_progress_dialog()
		if self.prescrape: scraper_list, _threads = self.prescrape_scrapers, self.prescrape_threads
		else: scraper_list, _threads = self.providers, self.threads
		self.internal_scrapers = self._get_active_scraper_names(scraper_list)
		if not self.internal_scrapers: return
		_scraperDialog()
		try: del monitor
		except: pass

	def display_results(self, results):
		window_format, window_number = results_format()
		action, chosen_item = open_window(('windows.sources', 'SourcesResults'), 'sources_results.xml',
				window_format=window_format, window_id=window_number, results=results, meta=self.meta,
				scraper_settings=self.scraper_settings, prescrape=self.prescrape, filters_ignored=self.filters_ignored, uncached_results=self.uncached_results)
		if not action: self._kill_progress_dialog()
		elif action == 'play': return self.play_file(results, chosen_item)
		elif self.prescrape and action == 'perform_full_search':
			self.prescrape, self.clear_properties = False, False
			return self.get_sources()

	def _get_active_scraper_names(self, scraper_list):
		return [i[2] for i in scraper_list]

	def _process_post_results(self):
		if self.auto_rescrape_with_all in (1, 2) and self.active_external and not self.post_results_processed:
			if self.auto_rescrape_with_all == 1 or confirm_dialog(heading=self.meta.get('rootname', ''), text='No results. Retry With All Scrapers?'):
				self.threads, self.post_results_processed, self.disabled_ext_ignored, self.prescrape = [], True, True, False
				return self.get_sources()
		if self.orig_results and not self.background:
			if self.ignore_results_filter == 0: return self._no_results()
			if self.ignore_results_filter == 1 or confirm_dialog(heading=self.meta.get('rootname', ''), text='No results. Access Filtered Results?'):
				return self._process_ignore_filters()
		return self._no_results()

	def _process_ignore_filters(self):
		if self.autoplay: notification('Filters Ignored & Autoplay Disabled')
		self.filters_ignored, self.autoplay = True, False
		results = self.sort_results(self.orig_results)
		results = self._sort_first(results)
		return self.play_source(results)

	def _no_results(self):
		self._kill_progress_dialog()
		hide_busy_dialog()
		if self.background: return notification('[B]Next Up:[/B] No Results', 5000)
		notification('No Results', 2000)

	def get_search_title(self):
		search_title = self.meta.get('custom_title', None) or self.meta.get('english_title') or self.meta.get('title')
		return search_title

	def get_search_year(self):
		year = self.meta.get('custom_year', None) or self.meta.get('year')
		return year

	def get_season(self):
		season = self.meta.get('custom_season', None) or self.meta.get('season')
		try: season = int(season)
		except: season = None
		return season

	def get_episode(self):
		episode = self.meta.get('custom_episode', None) or self.meta.get('episode')
		try: episode = int(episode)
		except: episode = None
		return episode

	def get_ep_name(self):
		ep_name = None
		if self.meta['media_type'] == 'episode':
			ep_name = self.meta.get('ep_name')
			try: ep_name = safe_string(remove_accents(ep_name))
			except: ep_name = safe_string(ep_name)
		return ep_name

	def _process_internal_results(self):
		for i in self.internal_scrapers:
			win_property = get_property(int_window_prop % i)
			if win_property in ('checked', '', None): continue
			try: sources = json.loads(win_property)
			except: continue
			set_property(int_window_prop % i, 'checked')
			self._sources_quality_count(sources)
	
	def _sources_quality_count(self, sources):
		for item in self.count_tuple: setattr(self, item[0], getattr(self, item[0]) + item[2](sources, item[1]))

	def _quality_filter(self):
		setting = 'results_quality_%s' % self.media_type if not self.autoplay else 'autoplay_quality_%s' % self.media_type
		filter_list = quality_filter(setting)
		if self.include_prerelease_results and 'SD' in filter_list: filter_list += ['SCR', 'CAM', 'TELE']
		return filter_list

	def _get_quality_rank(self, quality):
		return quality_ranks[quality]

	def _get_provider_rank(self, account_type):
		return self.provider_sort_ranks[account_type] or 11

	def _sort_first(self, results):
		try:
			sort_first_scrapers = []
			if 'folders' in self.all_scrapers and sort_to_top('folders'): sort_first_scrapers.append('folders')
			sort_first_scrapers.extend([i for i in self.all_scrapers if i in cloud_scrapers and sort_to_top(i)])
			if not sort_first_scrapers: return results
			sort_first = [i for i in results if i['scrape_provider'] in sort_first_scrapers]
			sort_first.sort(key=lambda k: (self._sort_folder_to_top(k['scrape_provider']), k['quality_rank']))
			sort_last = [i for i in results if not i in sort_first]
			results = sort_first + sort_last
		except: pass
		return results

	def _sort_folder_to_top(self, provider):
		if provider == 'folders': return 0
		else: return 1

	def _sort_uncached_results(self, results):
		uncached = [i for i in results if 'Uncached' in i.get('cache_provider', '')]
		cached = [i for i in results if not i in uncached]
		return cached + uncached

	def _special_filter(self, results, key, enable_setting):
		if key == self.hevc_filter_key and enable_setting in (0,2):
			hevc_max_quality = self._get_quality_rank(get_setting('fenlight.filter_hevc.%s' % ('max_autoplay_quality' if self.autoplay else 'max_quality'), '4K'))
			results = [i for i in results if not key in i['extraInfo'] or i['quality_rank'] >= hevc_max_quality]
		if enable_setting == 1:
			if key == self.dolby_vision_filter_key and self.hybrid_allowed:
				results = [i for i in results if all(x in i['extraInfo'] for x in (key, self.hdr_filter_key)) or not key in i['extraInfo']]
			else: results = [i for i in results if not key in i['extraInfo']]
		elif enable_setting == 2 and self.autoplay:
			priority_list = [i for i in results if key in i['extraInfo']]
			remainder_list = [i for i in results if not i in priority_list]
			results = priority_list + remainder_list
		elif enable_setting == 3: results = [i for i in results if not any(x in i['extraInfo'] for x in key)]
		return results

	def get_meta(self):
		if self.media_type == 'movie': self.meta = metadata.movie_meta('tmdb_id', self.tmdb_id, get_datetime())
		else:
			self.meta = metadata.tvshow_meta('tmdb_id', self.tmdb_id, get_datetime())
			episodes_data = metadata.episodes_meta(self.season, self.meta)
			try:
				episode_data = [i for i in episodes_data if i['episode'] == self.episode][0]
				ep_thumb = episode_data.get('thumb', None) or self.meta.get('fanart') or ''
				self.meta.update({'season': episode_data['season'], 'episode': episode_data['episode'], 'premiered': episode_data['premiered'],
								'ep_name': episode_data['title'], 'ep_thumb': ep_thumb, 'plot': episode_data['plot'], 'tvshow_plot': self.meta['plot'],
								'custom_season': self.custom_season, 'custom_episode': self.custom_episode})
			except: pass
		self.meta.update({'media_type': self.media_type, 'background': self.background, 'custom_title': self.custom_title, 'custom_year': self.custom_year})

	def make_search_info(self):
		title, year, season, episode, ep_name = self.get_search_title(), self.get_search_year(), self.get_season(), self.get_episode(), self.get_ep_name()
		aliases = make_alias_dict(self.meta, title)
		expiry_times = get_cache_expiry(self.media_type, self.meta, self.season)
		self.search_info = {'media_type': self.media_type, 'title': title, 'year': year, 'tmdb_id': self.tmdb_id, 'imdb_id': self.meta.get('imdb_id'), 'aliases': aliases,
							'season': season, 'episode': episode, 'tvdb_id': self.meta.get('tvdb_id'), 'ep_name': ep_name, 'expiry_times': expiry_times,
							'total_seasons': self.meta.get('total_seasons', 1)}

	def _get_module(self, module_type, function):
		if module_type == 'external': module = function.source(*self.external_args)
		elif module_type == 'folders': module = function[0](*function[1])
		else: module = function()
		return module

	def _clear_properties(self):
		for item in default_internal_scrapers: clear_property(int_window_prop % item)
		if self.active_folders:
			for item in self.folder_info: clear_property(int_window_prop % item[0])

	def _make_progress_dialog(self):
		self.progress_dialog = create_window(('windows.sources', 'SourcesPlayback'), 'sources_playback.xml', meta=self.meta)
		self.progress_thread = Thread(target=self.progress_dialog.run)
		self.progress_thread.start()

	def _make_resolve_dialog(self):
		self.resolve_dialog_made = True
		if not self.progress_dialog: self._make_progress_dialog()
		self.progress_dialog.enable_resolver()

	def _make_resume_dialog(self, percent):
		if not self.progress_dialog: self._make_progress_dialog()
		self.progress_dialog.enable_resume(percent)
		return self.progress_dialog.resume_choice

	def _make_nextep_dialog(self, default_action='cancel', play_type='autoplay_nextep', focus_button=11):
		try: action = open_window(('windows.next_episode', 'NextEpisode'), 'next_episode.xml',
			meta=self.meta, default_action=default_action, play_type=play_type, focus_button=focus_button)
		except: action = 'cancel'
		return action

	def _kill_progress_dialog(self):
		success = 0
		try:
			self.progress_dialog.close()
			success += 1
		except: pass
		try:
			self.progress_thread.join()
			success += 1
		except: pass
		if not success == 2: close_all_dialog()
		del self.progress_dialog
		del self.progress_thread
		self.progress_dialog, self.progress_thread = None, None

	def debridPacks(self, debrid_provider, name, magnet_url, info_hash, download=False):
		show_busy_dialog()
		debrid_info = {'Real-Debrid': 'rd_browse', 'Premiumize.me': 'pm_browse', 'AllDebrid': 'ad_browse'}[debrid_provider]
		debrid_function = self.debrid_importer(debrid_info)
		try: debrid_files = debrid_function().display_magnet_pack(magnet_url, info_hash)
		except: debrid_files = None
		debrid_files = debrid_function().display_magnet_pack(magnet_url, info_hash)
		hide_busy_dialog()
		if not debrid_files: return notification('Error')
		debrid_files.sort(key=lambda k: k['filename'].lower())
		if download: return debrid_files, debrid_function
		list_items = [{'line1': '%.2f GB | %s' % (float(item['size'])/1073741824, clean_file_name(item['filename']).upper())} for item in debrid_files]
		kwargs = {'items': json.dumps(list_items), 'heading': name, 'enumerate': 'true', 'narrow_window': 'true'}
		chosen_result = select_dialog(debrid_files, **kwargs)
		if chosen_result is None: return None
		link = self.resolve_internal(debrid_info, chosen_result['link'], '')
		name = chosen_result['filename']
		self._kill_progress_dialog()
		return FenLightPlayer().run(link, 'video')

	def play_file(self, results, source={}):
		self.playback_successful, self.cancel_all_playback = None, False
		try:
			hide_busy_dialog()
			url = None
			results = [i for i in results if not 'Uncached' in i.get('cache_provider', '')]
			if not source: source = results[0]
			items = [source]
			if not self.limit_resolve: 
				source_index = results.index(source)
				results.remove(source)
				leading_index = max(source_index-3, 0)
				items_prev = results[leading_index:source_index]
				trailing_index = 7 - len(items_prev)
				items_next = results[source_index+1:source_index+trailing_index]
				items = items + items_next + items_prev
			processed_items = []
			processed_items_append = processed_items.append
			for count, item in enumerate(items, 1):
				resolve_item = dict(item)
				provider = item['scrape_provider']
				if provider == 'external': provider = item['debrid'].replace('.me', '')
				elif provider == 'folders': provider = item['source']
				provider_text = provider.upper()
				extra_info = '[B]%s[/B] | [B]%s[/B] | %s' %  (item['quality'], item['size_label'], item['extraInfo'])
				display_name = item['display_name'].upper()
				resolve_item['resolve_display'] = '%s[CR]%s[CR]%s' % ('%02d. [B]%s[/B]' % (count, provider_text), extra_info, display_name)
				processed_items_append(resolve_item)
				if provider == 'easynews':
					for retry in range(1, 2):
						resolve_item = dict(item)
						resolve_item['resolve_display'] = '%s[CR]%s[CR]%s' % ('%02d. [B]%s (RETRYx%s)[/B]' % (count, provider_text, retry), extra_info, display_name)
						processed_items_append(resolve_item)
			items = list(processed_items)
			if not self.continue_resolve_check(): return self._kill_progress_dialog()
			hide_busy_dialog()
			self.playback_percent = self.get_playback_percent()
			if self.playback_percent == None: return self._kill_progress_dialog()
			if not self.resolve_dialog_made: self._make_resolve_dialog()
			if self.background: sleep(1000)
			monitor = kodi_utils.monitor
			url = None
			for count, item in enumerate(items, 1):
				try:
					hide_busy_dialog()
					if not self.progress_dialog: break
					self.progress_dialog.reset_is_cancelled()
					self.progress_dialog.update_resolver(text=item['resolve_display'])
					self.progress_dialog.busy_spinner()
					if count > 1:
						sleep(1500)
						try: del player
						except: pass
					player = FenLightPlayer()
					url, self.playback_successful, self.cancel_all_playback = None, None, False
					self.playing_filename = item['name']
					try:
						if self.progress_dialog.iscanceled() or monitor.abortRequested(): break
						url = self.resolve_sources(item)
						if url:
							resolve_percent = 0
							self.progress_dialog.busy_spinner('false')
							self.progress_dialog.update_resolver(percent=resolve_percent)
							sleep(200)
							player.run(url, self)
						if self.cancel_all_playback: break
						if self.playback_successful: break
						if count == len(items):
							self.cancel_all_playback = True
							player.stop()
							break
					except: pass
				except: pass
		except: self._kill_progress_dialog()
		if self.cancel_all_playback: return self._kill_progress_dialog()
		if not self.playback_successful or not url: self.playback_failed_action()
		try: del monitor
		except: pass

	def get_playback_percent(self):
		if self.media_type == 'episode' and any((self.random, self.random_continual)): return 0.0
		percent = get_progress_percent(get_bookmarks(watched_indicators(), self.media_type), self.tmdb_id, self.season, self.episode)
		if not percent: return 0.0
		action = self.get_resume_status(percent)
		if action == 'cancel': return None
		if action == 'start_over':
			erase_bookmark(self.media_type, self.tmdb_id, self.season, self.episode)
			return 0.0
		return float(percent)

	def get_resume_status(self, percent):
		if auto_resume(self.media_type): return float(percent)
		return self._make_resume_dialog(percent)

	def playback_failed_action(self):
		self._kill_progress_dialog()
		if self.prescrape and self.autoplay:
			self.resolve_dialog_made, self.prescrape, self.prescrape_sources = False, False, []
			self.get_sources()

	def continue_resolve_check(self):
		try:
			if not self.background or self.autoscrape_nextep: return True
			if self.autoplay_nextep: return self.autoplay_nextep_handler()
			return self.random_continual_handler()
		except: return False

	def random_continual_handler(self):
		notification('[B]Next Up:[/B] %s S%02dE%02d' % (self.meta.get('title'), self.meta.get('season'), self.meta.get('episode')), 6500, self.meta.get('poster'))
		player = xbmc_player()
		while player.isPlayingVideo(): sleep(100)
		self._make_resolve_dialog()
		return True

	def autoplay_nextep_handler(self):
		if not self.nextep_settings: return False
		player = xbmc_player()
		if player.isPlayingVideo():
			total_time = player.getTotalTime()
			window_time, default_action = self.nextep_settings['window_time'], self.nextep_settings['default_action']
			action = 'close'
			continue_nextep = False
			while player.isPlayingVideo():
				try:
					remaining_time = round(total_time - player.getTime())
					if remaining_time <= window_time:
						continue_nextep = True
						break
					sleep(100)
				except: pass
			if continue_nextep:
				action = self._make_nextep_dialog(default_action=default_action)
				if not action: action = default_action
				if action == 'cancel': return False
				elif action == 'pause':
					player.stop()
					return False
				elif action == 'play':
					self._make_resolve_dialog()
					player.stop()
					return True
				else:
					while player.isPlayingVideo(): sleep(100)
					self._make_resolve_dialog()
					return True
			else: return False
		else: return False

	def autoscrape_nextep_handler(self):
		default_action = 'cancel'
		player = xbmc_player()
		if player.isPlayingVideo():
			action = self._make_nextep_dialog(play_type=self.play_type, focus_button=12)
			if action == 'cancel': return
			else:
				results = self.get_sources()
				if not results: return notification('No Auto Scrape Sources Found', 3000)
				if action == 'play': player.stop()
				else:
					notification('Auto Scrape Sources Ready', 3000)
					while player.isPlayingVideo(): sleep(100)
				self.display_results(results)
		else: return

	def debrid_importer(self, debrid_provider):
		return manual_function_import(*debrids[debrid_provider])

	def resolve_sources(self, item, meta=None):
		if meta: self.meta = meta
		url = None
		try:
			if 'cache_provider' in item:
				cache_provider = item['cache_provider']
				if self.meta['media_type'] == 'episode':
					if hasattr(self, 'search_info'):
						title, season, episode, pack = self.search_info['title'], self.search_info['season'], self.search_info['episode'], 'package' in item
					else: title, season, episode, pack = self.get_ep_name(), self.get_season(), self.get_episode(), 'package' in item
				else: title, season, episode, pack = self.get_search_title(), None, None, False
				if cache_provider in debrid_providers: url = self.resolve_cached(cache_provider, item['url'], item['hash'], title, season, episode, pack)
			elif item.get('scrape_provider', None) in default_internal_scrapers:
				url = self.resolve_internal(item['scrape_provider'], item['id'], item['url_dl'], item.get('direct_debrid_link', False))
			else: url = item['url']
		except: pass
		return url

	def resolve_cached(self, debrid_provider, item_url, _hash, title, season, episode, pack):
		debrid_function = self.debrid_importer(debrid_provider)
		store_to_cloud = store_resolved_to_cloud(debrid_provider, pack)
		try: url = debrid_function().resolve_magnet(item_url, _hash, store_to_cloud, title, season, episode)
		except: url = None
		return url

	def resolve_uncached(self, debrid_provider, item_url, pack):
		if not confirm_dialog(text='Transfer this Result to your [B]%s[/B] Cloud?' % debrid_provider.upper()): return None
		debrid_function = self.debrid_importer(debrid_provider)
		try: debrid_function().add_uncached(item_url, pack)
		except: return notification('Failed', 3500)

	def resolve_internal(self, scrape_provider, item_id, url_dl, direct_debrid_link=False):
		url = None
		try:
			if direct_debrid_link or scrape_provider == 'folders': url = url_dl
			elif scrape_provider == 'easynews':
				from indexers.easynews import resolve_easynews
				url = resolve_easynews({'url_dl': url_dl, 'play': 'false'})
			else:
				debrid_function = self.debrid_importer(scrape_provider)
				if any(i in scrape_provider for i in ('rd_', 'ad_')):
					url = debrid_function().unrestrict_link(item_id)
				else:
					if '_cloud' in scrape_provider: item_id = debrid_function().get_item_details(item_id)['link']
					url = debrid_function().add_headers_to_url(item_id)
		except: pass
		return url

	def _quality_length(self, items, quality):
		return len([i for i in items if i['quality'] == quality])

	def _quality_length_sd(self, items, dummy):
		return len([i for i in items if i['quality'] in sd_check])

	def _quality_length_final(self, items, dummy):
		return len(items)
