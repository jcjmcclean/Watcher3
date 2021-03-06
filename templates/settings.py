import os

import cherrypy
import core
import dominate
from cherrypy import expose
from dominate.tags import *
from header import Header
from head import Head


def settings_page(page):
    ''' Decorator template for settings subpages
    :param page: Sub-page content to render, written with Dominate tags, but without a Dominate instance.

    Returns rendered html from Dominate.
    '''

    def page_template(self):
        config = core.CONFIG
        doc = dominate.document(title='Watcher')

        with doc.head:
            meta(name='git_url', content=core.GIT_URL)
            Head.insert()
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/settings.css?v=03.28')
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/{}settings.css?v=03.28'.format(core.CONFIG['Server']['theme']))
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/plugin_conf_popup.css?v=03.28')
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/{}plugin_conf_popup.css?v=03.28'.format(core.CONFIG['Server']['theme']))
            script(type='text/javascript', src=core.URL_BASE + '/static/js/settings/main.js?v=03.30')
            script(type='text/javascript', src=core.URL_BASE + '/static/js/settings/save_settings.js?v=03.28')

        with doc:
            Header.insert_header(current="settings")
            with div(id="content", cls=page.__name__):
                page(self, config)

            div(id='overlay')

            div(id='plugin_conf_popup')

        return doc.render()

    return page_template


class Settings():

    @expose
    def default(self):
        raise cherrypy.InternalRedirect('/settings/server')

    @expose
    @settings_page
    def server(self, c):
        h1('Server')
        c_s = 'Server'
        with ul(id='server', cls='wide'):
            with li('Host: ', cls='bbord'):
                input(type='text', id='serverhost', value=c[c_s]['serverhost'], style='width: 17em')
                span('Typically localhost or 127.0.0.1.', cls='tip')
            with li('Port: ', cls='bbord'):
                input(type='number', id='serverport', value=c[c_s]['serverport'], style='width: 5em')
            with li(cls='bbord'):
                i(id='customwebroot', cls='fa fa-square-o checkbox', value=str(c[c_s]['customwebroot']))
                span('Use custom webroot: ')
                input(type='text', id='customwebrootpath', value=c[c_s]['customwebrootpath'], placeholder='/watcher')
                span('For access behind reverse proxies.', cls='tip')
            with li('API Key: ', cls='bbord'):
                input(type='text', id='apikey', value=c[c_s]['apikey'], style='width: 20em')
                with span(cls='tip'):
                    i(id='generate_new_key', cls='fa fa-refresh')
                    span('Generate new key.')
            with li(cls='bbord'):
                span('Keep ')
                input(type='number', id='keeplog', value=c[c_s]['keeplog'], style='width: 3em')
                span(' days of logs.')
            with li():
                i(id='verifyssl', cls='fa fa-square-o checkbox', value=str(c[c_s]['verifyssl']))
                span('Verify SSL certificates.')

        h2('Interface')
        with ul(id='interface', cls='wide'):
            with li('Theme:', cls='bbord'):
                with select(id='theme', value=c[c_s]['theme']):
                    tl = self.get_themes()
                    for opt in tl:
                        if opt == 'Default':
                            item = option(opt, value='')
                            if c[c_s]['theme'] == '':
                                item['selected'] = 'selected'
                        else:
                            item = option(opt, value='{}/'.format(opt))
                        if item['value'] == c[c_s]['theme']:
                            item['selected'] = 'selected'
            with li():
                i(id='authrequired', cls='fa fa-square-o checkbox', value=str(c[c_s]['authrequired']))
                span('Password-protect web-ui.')
                span('*Requires restart.', cls='tip')
            with li('Name: ', cls='indent bbord'):
                input(type='text', id='authuser', value=c[c_s]['authuser'], style='width: 20em')
            with li('Password: ', cls='bbord indent'):
                input(type='text', id='authpass', value=c[c_s]['authpass'], style='width: 20em')
            with li():
                i(id='launchbrowser', cls='fa fa-square-o checkbox', value=str(c[c_s]['launchbrowser']))
                span('Open browser on launch.')

        h2('Updates')
        with ul(id='updates', cls='wide'):
            with li(cls='bbord'):
                i(id='checkupdates', cls='fa fa-square-o checkbox', value=str(c[c_s]['checkupdates']))
                span('Check for updates every ')
                input(type='number', min='8', id='checkupdatefrequency', value=c[c_s]['checkupdatefrequency'], style='width: 2.25em')
                span(' hours.')
                span('Checks at program start and every X hours afterward. *Requires restart.', cls='tip')
            with li(cls='bbord'):
                i(id='installupdates', cls='fa fa-square-o checkbox', value=str(c[c_s]['installupdates']))
                span('Automatically install updates at ')
                input(type='number', min='0', max='23', id='installupdatehr', value=c[c_s]['installupdatehr'], style='width: 2.25em')
                span(':')
                input(type='number', min='0', max='59', id='installupdatemin', value=c[c_s]['installupdatemin'], style='width: 2.25em')
                span('24hr time. *Requires restart.', cls='tip')
            with li(cls='hidden'):
                input(type='text', id='gitbranch', value=c[c_s]['gitbranch'])
            with li():
                with span(id='update_check'):
                    i(cls='fa fa-arrow-circle-up')
                    span('Check for updates now.')
                    with span('Current version hash: ', cls='tip'):
                        if core.CURRENT_HASH is not None:
                            a(core.CURRENT_HASH[0:7], href='{}/commits'.format(core.GIT_URL), target='_blank')
        h2('Proxy')
        with ul(id='proxy', cls='wide'):
            with li():
                i(id='enabled', cls='fa fa-square-o checkbox', value=str(c[c_s]['Proxy']['enabled']))
                span('Enable proxy')
                span('Used when connecting to search providers.', cls='tip')
            with li('Address: ', cls='indent bbord'):
                input(type='text', id='host', value=c[c_s]['Proxy']['host'], style="width:16em")
                span('Include "http://" or "https://" for http(s) proxy.', cls='tip')
            with li('Port: ', cls='indent bbord'):
                input(type='number', min='0', max='65535', id='port', value=c[c_s]['Proxy']['port'], style='width: 6em')
            with li('User name: ', cls='indent bbord'):
                input(type='text', id='user', value=c[c_s]['Proxy']['user'])
                span('Leave blank for none.', cls='tip')
            with li('Password: ', cls='indent bbord'):
                input(type='text', id='pass', value=c[c_s]['Proxy']['pass'])
                span('Leave blank for none.', cls='tip')
            with li('Type: ', cls='indent bbord'):
                with select(id='type'):
                    opts = ['http(s)', 'socks4', 'socks5']
                    for opt in opts:
                        if opt == c[c_s]['Proxy']['type']:
                            option(opt, value=opt, selected="selected")
                        else:
                            option(opt, value=opt)
            with li('Whitelist', cls='indent'):
                input(type='text', id='whitelist', value=c[c_s]['Proxy']['whitelist'], placeholder='http://localhost:5075, http://localhost:5060', style='width:24em')
        h2()
        with ul():
            with li():
                with span(id='restart'):
                    i(cls='fa fa-refresh')
                    span('Restart')
                with span(id='shutdown'):
                    i(cls='fa fa-power-off')
                    span('Shutdown')
        with div(id='save', cat='server'):
            i(cls='fa fa-save')
            span('Save Settings')

    @expose
    @settings_page
    def search(self, c):
        c_s = 'Search'

        h1('Search')
        # set the config section at each new section. Just makes everything a little shorter and easier to write.
        with ul(id='search', cls='wide'):
            with li(cls='bbord'):
                i(id='searchafteradd', cls='fa fa-square-o checkbox', value=str(c[c_s]['searchafteradd']))
                span('Perform backlog search immediately after adding movie.')
                span('Skips wait until next scheduled search.', cls='tip')
            with li(cls='bbord'):
                i(id='autograb', cls='fa fa-square-o checkbox', value=str(c[c_s]['autograb']))
                span('Automatically grab best result.')
                span('Will still wait X days if set.', cls='tip')
            with li(cls='bbord'):
                span('RSS sync interval: ')
                input(type='number', min='10', id='rsssyncfrequency', style='width: 2.5em', value=c[c_s]['rsssyncfrequency'])
                span('minutes.')
                span('Min 10 minutes. Requires Restart.', cls='tip')
            with li():
                span('Wait ')
                input(type='number', min='0', max='14', id='waitdays', style='width: 2.0em', value=c[c_s]['waitdays'])
                span(' days for best release.')
                span('After movie is found, wait to snatch in case better match is found.', cls='tip')
            with li(cls='bbord indent'):
                i(id='skipwait', cls='fa fa-square-o checkbox', value=str(c[c_s]['skipwait']))
                span('Skip wait if release date is more than ')
                input(type='number', min='0', id='skipwaitweeks', style='width: 2.5em', value=c[c_s]['skipwaitweeks'])
                span(' weeks ago.')
            with li():
                i(id='keepsearching', cls='fa fa-square-o checkbox', value=str(c[c_s]['keepsearching']))
                span('Continue searching for ')
                input(type='number', min='0', id='keepsearchingdays', style='width: 2.5em', value=c[c_s]['keepsearchingdays'])
                span(' days for best release.')
            with li(cls='bbord indent'):
                span('Releases must score ')
                input(type='number', min='0', id='keepsearchingscore', style='width: 3em', value=c[c_s]['keepsearchingscore'])
                span(' points higher to be snatched again.')
            with li(cls='bbord'):
                span('Usenet server retention: ')
                input(type='number', min='0', id='retention', value=c[c_s]['retention'])
                span(' days.')
                span('Use 0 for no limit.', cls='tip')
            with li(cls='bbord'):
                span('Torrents require a minimum of ')
                input(type='number', min='0', id='mintorrentseeds', value=c[c_s]['mintorrentseeds'], style='width: 2.5em')
                span(' seeds.')
            with li():
                span('Add ')
                input(type='number', min='0', id='freeleechpoints', value=c[c_s]['freeleechpoints'], style='width: 3em')
                span(' points to FreeLeech torrents.')

        h2('Watchlists')
        with ul(id='watchlists'):

            with li():
                i(id='imdbsync', cls='fa fa-square-o checkbox', value=str(c[c_s]['Watchlists']['imdbsync']))
                span('Sync imdb watch list ')
                input(type='text', id='imdbrss', value=c[c_s]['Watchlists']['imdbrss'], placeholder="http://rss.imdb.com/user/...", style="width:18em;")
                span(' every ')
                input(type='number', min='15', id='imdbfrequency', value=c[c_s]['Watchlists']['imdbfrequency'], style='width: 3.0em')
                span(' minutes.')
                span('*Requires restart.', cls='tip')
            with li():
                i(id='popularmoviessync', cls='fa fa-square-o checkbox', value=str(c[c_s]['Watchlists']['popularmoviessync']))
                span('Sync Popular Movies list at ')
                input(type='number', min='0', max='23', id='popularmovieshour', value=c[c_s]['Watchlists']['popularmovieshour'], style='width: 3.0em')
                span(':')
                input(type='number', min='0', max='59', id='popularmoviesmin', value=c[c_s]['Watchlists']['popularmoviesmin'], style='width: 3.0em')
                with span(cls='tip'):
                    with a(href='https://github.com/sjlu/popular-movies', target='_blank'):
                        i(cls='fa fa-question-circle')
                    span('Updates every 24hr. *Requires restart.')
        with div(id='save', cat='search'):
            i(cls='fa fa-save')
            span('Save Settings')

    @expose
    @settings_page
    def quality(self, c):

        c_s = 'Quality'
        user_profiles = {k: v for k, v in c[c_s]['Profiles'].items() if k != 'Default'}
        default_profile = c[c_s]['Profiles']['Default']

        self.resolutions = ['4K', '1080P', '720P', 'SD']

        h1('Quality Profiles')
        with div(id='qualities'):
            self.render_profile('Default', default_profile)

            for name, profile in user_profiles.items():
                self.render_profile(name, profile)

        with div(id='add_new_profile'):
            with span(id='add_new_profile'):
                i(cls='fa fa-plus-square')
                span('Add Profile')

        h1('Sources')
        br()
        span('Specify acceptable size range in MB for each media source.', cls='indent')
        with table(id='sources'):
            with tr():
                th()
                th('Minimum Size')
                th('Maximum size')
            for k in core.RESOLUTIONS:
                v = c[c_s]['Sources'][k]
                with tr(cls='source_size'):
                    td(k, id=k)
                    with td():
                        input(type='number', cls='min_size', value=v['min'])
                    with td():
                        input(type='number', cls='max_size', value=v['max'])
        h2('Aliases')
        span('These keywords are used to determine the source media.', cls='indent')
        br()
        br()
        with table(id='aliases'):
            for name, aliases in c[c_s]['Aliases'].items():
                with tr():
                    td(name)
                    with td():
                        input(type='text', value=', '.join(aliases), id=name)

        div(','.join(self.resolutions), cls='hidden')
        with div(id='save', cat='quality'):
            i(cls='fa fa-save')
            span('Save Settings')

    def render_profile(self, name, profile):
        '''
        name: str name of profile
        profile: dict of profile Settings
        '''
        profile = core.CONFIG['Quality']['Profiles'][name]

        with div(id=name, cls='quality_profile') as profile_list:
            with div(cls='name bold'):
                if name == 'Default':
                    span('Default')
                    span('Used for Quick-Add and default API quality.', cls='tip')
                else:
                    input(value=name, type='text', cls='name')

            with div(cls='sources'):
                span('Sources', cls='sub_heading')
                with ul(cls='sortable'):
                    for res in core.RESOLUTIONS:
                        with li(id=res, sort=profile['Sources'][res][1]):
                            i(cls='fa fa-bars')
                            i(id=res, cls='fa fa-square-o checkbox', value=str(profile['Sources'][res][0]))
                            span(res)

            with div(id='filters'):
                with span('Filters', cls='sub_heading'):
                    span('Make groups with ampersands ( & ) and split groups with commas ( , )', cls='tip')
                with ul():
                    with li('Required words:', cls='bold'):
                        span('Releases must contain one of these words or groups.', cls='tip')
                    with li():
                        input(type='text', id='requiredwords', value=profile['requiredwords'])
                    with li('Preferred words:', cls='bold'):
                        span('Releases with these words score higher.', cls='tip')
                    with li():
                        input(type='text', id='preferredwords', value=profile['preferredwords'])
                    with li('Ignored words:', cls='bold'):
                        span('Releases with these words are ignored.', cls='tip')
                    with li():
                        input(type='text', id='ignoredwords', value=profile['ignoredwords'])

            with div(id='toggles'):
                span('Misc.', cls='sub_heading')
                with ul():
                    with li():
                        i(id='scoretitle', cls='fa fa-square-o checkbox', value=str(profile['scoretitle']))
                        span('Score and filter titles.')
                    with li():
                        span('May need to disable for non-English results. Can cause incorrect downloads', cls='tip')
                    with li():
                        i(id='prefersmaller', cls='fa fa-square-o checkbox', value=str(profile['prefersmaller']))
                        span('Prefer smaller file sizes for identically-scored releases.')

            if name != 'Default':
                i(cls='fa fa-trash delete_profile')

        return str(profile_list)

    @expose
    @settings_page
    def providers(self, c):
        c_s = 'Indexers'

        h1('Indexers')
        with ul(id='indexers', cls='wide'):
            with li():
                with ul(id='newznab_list'):
                    with li(cls='sub_cat'):
                        span('NewzNab Indexers')
                    for n in c[c_s]['NewzNab']:
                        with li(cls='newznab_indexer'):
                            i(cls='newznab_check fa fa-square-o checkbox', value=str(c[c_s]['NewzNab'][n][2]))
                            input(type='text', cls='newznab_url', value=c[c_s]['NewzNab'][n][0], placeholder=" http://www.indexer-url.com/")
                            input(type='text', cls='newznab_api', value=c[c_s]['NewzNab'][n][1], placeholder=" Api Key")
                            i(cls='newznab_clear fa fa-trash-o')
                            i(cls='indexer_test fa fa-plug', type='newznab')
                    with li(cls='add_newznab_row'):
                        i(cls='fa fa-plus-square', id='add_newznab_row')

                with ul(id='torznab_list'):
                    with li(cls='sub_cat'):
                        span('TorzNab Indexers')
                    for k, v in c[c_s]['TorzNab'].items():
                        with li(cls='torznab_indexer'):
                            i(cls='torznab_check fa fa-square-o checkbox', value=str(v[2]))
                            input(type='text', cls='torznab_url', value=v[0], placeholder=" http://www.indexer-url.com/")
                            input(type='text', cls='torznab_api', value=v[1], placeholder=" Api Key")
                            i(cls='torznab_clear fa fa-trash-o')
                            i(cls='indexer_test fa fa-plug', type='torznab')
                    with li(cls='add_torznab_row'):
                        i(cls='fa fa-plus-square', id='add_torznab_row')

                with ul(id='torrentindexer_list'):
                    with li(cls='sub_cat'):
                        span('Torrent Indexers')
                    with li(cls='torrent_indexer', id='extratorrent'):
                        i(cls='torrent_check fa fa-square-o checkbox', value=str(c[c_s]['Torrent']['extratorrent']))
                        span('ExtraTorrent')
                    with li(cls='torrent_indexer', id='limetorrents'):
                        i(cls='torrent_check fa fa-square-o checkbox', value=str(c[c_s]['Torrent']['limetorrents']))
                        span('LimeTorrents')
                    with li(cls='torrent_indexer', id='rarbg'):
                        i(cls='torrent_check fa fa-square-o checkbox', value=str(c[c_s]['Torrent']['rarbg']))
                        span('Rarbg')
                    with li(cls='torrent_indexer', id='skytorrents'):
                        i(cls='torrent_check fa fa-square-o checkbox', value=str(c[c_s]['Torrent']['skytorrents']))
                        span('SkyTorrents')
                    with li(cls='torrent_indexer', id='thepiratebay'):
                        i(cls='torrent_check fa fa-square-o checkbox', value=str(c[c_s]['Torrent']['thepiratebay']))
                        span('ThePirateBay')
                    with li(cls='torrent_indexer', id='torrentz2'):
                        i(cls='torrent_check fa fa-square-o checkbox', value=str(c[c_s]['Torrent']['torrentz2']))
                        span('Torrentz2')

        with div(id='save', cat='providers'):
            i(cls='fa fa-save')
            span('Save Settings')

    @expose
    @settings_page
    def downloader(self, c):
        c_s = 'Downloader'

        h1('Downloader')
        with h2():
            i(id='usenetenabled', cls='fa fa-square-o checkbox', value=str(c[c_s]['Sources']['usenetenabled']), tag='usenet')
            span('Usenet Downloaders')

        usenet_hidden = None
        if c[c_s]['Sources']['usenetenabled'] is False:
            usenet_hidden = 'hidden'

        with ul(id='usenet', cls=usenet_hidden):
            with li():
                i(id='nzbgetenabled', cls='fa fa-circle-o radio', name='usenetdownloader', tog='nzbget', value=str(c[c_s]['Usenet']['NzbGet']['enabled']))
                span('NZBGet', cls='sub_cat')
            with ul(id='nzbget', cls='nzb'):
                with li('Host & Port: ', cls='bbord'):
                    input(type='text', id='host', value=c[c_s]['Usenet']['NzbGet']['host'], style='width: 25%')
                    span(' : ')
                    input(type='number', id='port', value=c[c_s]['Usenet']['NzbGet']['port'], style='width: 25%')
                with li('User Name: ', cls='bbord'):
                    input(type='text', id='user', value=c[c_s]['Usenet']['NzbGet']['user'], style='width: 50%')
                    span('Default: nzbget.', cls='tip')
                with li('Password: ', cls='bbord'):
                    input(type='text', id='pass', value=c[c_s]['Usenet']['NzbGet']['pass'], style='width: 50%')
                    span('Default: tegbzn6789.', cls='tip')
                with li('Category: ', cls='bbord'):
                    input(type='text', id='category', value=c[c_s]['Usenet']['NzbGet']['category'], style='width: 50%')
                    span('i.e. \'movies\', \'watcher\'. ', cls='tip')
                with li('Priority: ', cls='bbord'):
                    with select(id='priority', style='width: 50%'):
                        pl = ['Very Low', 'Low', 'Normal', 'High', 'Forced']
                        for o in pl:
                            if o == c[c_s]['Usenet']['NzbGet']['priority']:
                                option(o, value=o, selected="selected")
                            else:
                                option(o, value=o)
                with li(cls='bbord'):
                    i(id='addpaused', cls='fa fa-square-o checkbox', value=str(c[c_s]['Usenet']['NzbGet']['addpaused']))
                    span('Add Paused')

                with li():
                    with span(cls='test_connection', mode='nzbget'):
                        i(cls='fa fa-plug')
                        span('Test Connection')

            with li():
                i(id='sabenabled', cls='fa fa-circle-o radio', name='usenetdownloader', tog='sabnzbd', value=str(c[c_s]['Usenet']['Sabnzbd']['enabled']))
                span('SABnzbd', cls='sub_cat')
            # I'm not 100% sure it is valid to do a ul>ul, but it only work this way so deal with it.
            with ul(id='sabnzbd', cls='nzb'):
                with li('Host & Port: ', cls='bbord'):
                    input(type='text', id='host', value=c[c_s]['Usenet']['Sabnzbd']['host'], style='width: 25%')
                    span(' : ')
                    input(type='number', id='port', value=c[c_s]['Usenet']['Sabnzbd']['port'], style='width: 25%')
                with li('Api Key: ', cls='bbord'):
                    input(type='text', id='api', value=c[c_s]['Usenet']['Sabnzbd']['api'], style='width: 50%')
                    span('Please use full api key.', cls='tip')
                with li('Category: ', cls='bbord'):
                    input(type='text', id='category', value=c[c_s]['Usenet']['Sabnzbd']['category'], style='width: 50%')
                    span('i.e. \'movies\', \'watcher\'. ', cls='tip')
                with li('Priority: ', cls='bbord'):
                    with select(id='priority', value=c[c_s]['Usenet']['Sabnzbd']['priority'], style='width: 50%'):
                        pl = ['Paused', 'Low', 'Normal', 'High', 'Forced']
                        for o in pl:
                            if o == c[c_s]['Usenet']['Sabnzbd']['priority']:
                                option(o, value=o, selected="selected")
                            else:
                                option(o, value=o)

                with li():
                    with span(cls='test_connection', mode='sabnzbd'):
                        i(cls='fa fa-plug')
                        span('Test Connection')

        with h2():
            i(id='torrentenabled', cls='fa fa-square-o checkbox', value=str(c[c_s]['Sources']['torrentenabled']), tag='torrent')
            span('Torrent Downloaders')

        torrent_hidden = None
        if c[c_s]['Sources']['torrentenabled'] is False:
            torrent_hidden = 'hidden'

        with ul(id='torrent', cls=torrent_hidden):
            with li():
                i(id='delugerpcenabled', cls='fa fa-circle-o radio', name='torrentdownloader', tog='delugerpc', value=str(c[c_s]['Torrent']['DelugeRPC']['enabled']))
                span('Deluge Daemon', cls='sub_cat')
            with ul(id='delugerpc', cls='torrent'):
                with li('Host & Port: ', cls='bbord'):
                    input(type='text', id='host', value=c[c_s]['Torrent']['DelugeRPC']['host'], style='width: 25%', placeholder='http://localhost')
                    span(' : ')
                    input(type='number', id='port', value=c[c_s]['Torrent']['DelugeRPC']['port'], style='width: 25%')
                with li('User Name: ', cls='bbord'):
                    input(type='text', id='user', value=c[c_s]['Torrent']['DelugeRPC']['user'], style='width: 50%')
                    span('Leave blank for none.', cls='tip')
                with li('Password: ', cls='bbord'):
                    input(type='text', id='pass', value=c[c_s]['Torrent']['DelugeRPC']['pass'], style='width: 50%')
                    span('Leave blank for none.', cls='tip')
                with li('Category: ', cls='bbord'):
                    input(type='text', id='category', value=c[c_s]['Torrent']['DelugeRPC']['category'], style='width: 50%')
                    span('i.e. \'movies\', \'watcher\'. ', cls='tip')
                with li('Priority: ', cls='bbord'):
                    with select(id='priority', style='width: 50%'):
                        pl = ['Normal', 'High', 'Max']
                        for o in pl:
                            if o == c[c_s]['Torrent']['DelugeRPC']['priority']:
                                option(o, value=o, selected="selected")
                            else:
                                option(o, value=o)
                with li(cls='bbord'):
                    i(id='addpaused', cls='fa fa-square-o checkbox', value=str(c[c_s]['Torrent']['DelugeRPC']['addpaused']))
                    span('Add Paused')

                with li():
                    with span(cls='test_connection', mode='delugerpc'):
                        i(cls='fa fa-plug')
                        span('Test Connection')

            with li():
                i(id='delugewebenabled', cls='fa fa-circle-o radio', name='torrentdownloader', tog='delugeweb', value=str(c[c_s]['Torrent']['DelugeWeb']['enabled']))
                span('Deluge Web UI', cls='sub_cat')
            with ul(id='delugeweb', cls='torrent'):
                with li('Host & Port: ', cls='bbord'):
                    input(type='text', id='host', value=c[c_s]['Torrent']['DelugeWeb']['host'], style='width: 25%', placeholder='http://localhost')
                    span(' : ')
                    input(type='number', id='port', value=c[c_s]['Torrent']['DelugeWeb']['port'], style='width: 25%')
                with li('Password: ', cls='bbord'):
                    input(type='text', id='pass', value=c[c_s]['Torrent']['DelugeWeb']['pass'], style='width: 50%')
                    span('Leave blank for none.', cls='tip')
                with li('Category: ', cls='bbord'):
                    input(type='text', id='category', value=c[c_s]['Torrent']['DelugeWeb']['category'], style='width: 50%')
                    span('i.e. \'movies\', \'watcher\'. ', cls='tip')
                with li('Priority: ', cls='bbord'):
                    with select(id='priority', style='width: 50%'):
                        pl = ['Normal', 'High', 'Max']
                        for o in pl:
                            if o == c[c_s]['Torrent']['DelugeWeb']['priority']:
                                option(o, value=o, selected="selected")
                            else:
                                option(o, value=o)
                with li(cls='bbord'):
                    i(id='addpaused', cls='fa fa-square-o checkbox', value=str(c[c_s]['Torrent']['DelugeWeb']['addpaused']))
                    span('Add Paused')

                with li():
                    with span(cls='test_connection', mode='delugeweb'):
                        i(cls='fa fa-plug')
                        span('Test Connection')
            with li():
                i(id='rtorrentscgienabled', cls='fa fa-circle-o radio', name='torrentdownloader', tog='rtorrentscgi', value=str(c[c_s]['Torrent']['rTorrentSCGI']['enabled']))
                span('rTorrent SCGI', cls='sub_cat')
            with ul(id='rtorrentscgi', cls='torrent'):
                with li('Host & Port: scgi://', cls='bbord'):
                    input(type='text', id='host', value=c[c_s]['Torrent']['rTorrentSCGI']['host'], style='width: 25%', placeholder='localhost:5000')
                    span(' : ')
                    input(type='number', id='port', value=c[c_s]['Torrent']['rTorrentSCGI']['port'], style='width: 25%')
                with li('Label: ', cls='bbord'):
                    input(type='text', id='label', value=c[c_s]['Torrent']['rTorrentSCGI']['label'], style='width: 50%')
                    span('i.e. \'movies\', \'watcher\'. ', cls='tip')
                with li(cls='bbord'):
                    i(id='addpaused', cls='fa fa-square-o checkbox', value=str(c[c_s]['Torrent']['rTorrentSCGI']['addpaused']))
                    span('Add Paused')
                with li():
                    with span(cls='test_connection', mode='rtorrentscgi'):
                        i(cls='fa fa-plug')
                        span('Test Connection')
            with li():
                i(id='rtorrenthttpenabled', cls='fa fa-circle-o radio', name='torrentdownloader', tog='rtorrenthttp', value=str(c[c_s]['Torrent']['rTorrentHTTP']['enabled']))
                span('rTorrent HTTP', cls='sub_cat')
            with ul(id='rtorrenthttp', cls='torrent'):
                with li('HTTP RPC address: ', cls='bbord'):
                    input(type='text', id='address', value=c[c_s]['Torrent']['rTorrentHTTP']['address'], style='width: 65%', placeholder='http://localhost/rutorrent/plugins/httprpc/action.php')
                with li('User Name: ', cls='bbord'):
                    input(type='text', id='user', value=c[c_s]['Torrent']['rTorrentHTTP']['user'], style='width: 50%')
                    span('Leave blank for none.', cls='tip')
                with li('Password: ', cls='bbord'):
                    input(type='text', id='pass', value=c[c_s]['Torrent']['rTorrentHTTP']['pass'], style='width: 50%')
                    span('Leave blank for none.', cls='tip')
                with li('Label: ', cls='bbord'):
                    input(type='text', id='label', value=c[c_s]['Torrent']['rTorrentHTTP']['label'], style='width: 50%')
                    span('i.e. \'movies\', \'watcher\'. ', cls='tip')
                with li(cls='bbord'):
                    i(id='addpaused', cls='fa fa-square-o checkbox', value=str(c[c_s]['Torrent']['rTorrentHTTP']['addpaused']))
                    span('Add Paused')
                with li():
                    with span(cls='test_connection', mode='rtorrenthttp'):
                        i(cls='fa fa-plug')
                        span('Test Connection')
            with li():
                i(id='transmissionenabled', cls='fa fa-circle-o radio', name='torrentdownloader', tog='transmission', value=str(c[c_s]['Torrent']['Transmission']['enabled']))
                span('Transmission', cls='sub_cat')
            with ul(id='transmission', cls='torrent'):
                with li('Host & Port: ', cls='bbord'):
                    input(type='text', id='host', value=c[c_s]['Torrent']['Transmission']['host'], style='width: 25%')
                    span(' : ')
                    input(type='number', id='port', value=c[c_s]['Torrent']['Transmission']['port'], style='width: 25%')
                with li('User Name: ', cls='bbord'):
                    input(type='text', id='user', value=c[c_s]['Torrent']['Transmission']['user'], style='width: 50%')
                    span('Leave blank for none.', cls='tip')
                with li('Password: ', cls='bbord'):
                    input(type='text', id='pass', value=c[c_s]['Torrent']['Transmission']['pass'], style='width: 50%')
                    span('Leave blank for none.', cls='tip')
                with li('Category: ', cls='bbord'):
                    input(type='text', id='category', value=c[c_s]['Torrent']['Transmission']['category'], style='width: 50%')
                    span('i.e. \'movies\', \'watcher\'. ', cls='tip')
                with li('Priority: ', cls='bbord'):
                    with select(id='priority', style='width: 50%'):
                        pl = ['Low', 'Normal', 'High']
                        for o in pl:
                            if o == c[c_s]['Torrent']['Transmission']['priority']:
                                option(o, value=o, selected="selected")
                            else:
                                option(o, value=o)
                with li(cls='bbord'):
                    i(id='addpaused', cls='fa fa-square-o checkbox', value=str(c[c_s]['Torrent']['Transmission']['addpaused']))
                    span('Add Paused')

                with li():
                    with span(cls='test_connection', mode='transmission'):
                        i(cls='fa fa-plug')
                        span('Test Connection')

            with li():
                i(id='qbittorrentenabled', cls='fa fa-circle-o radio', name='torrentdownloader', tog='qbittorrent', value=str(c[c_s]['Torrent']['QBittorrent']['enabled']))
                span('QBittorrent', cls='sub_cat')
            with ul(id='qbittorrent', cls='torrent'):
                with li('Host & Port: ', cls='bbord'):
                    input(type='text', id='host', value=c[c_s]['Torrent']['QBittorrent']['host'], style='width: 25%')
                    span(' : ')
                    input(type='number', id='port', value=c[c_s]['Torrent']['QBittorrent']['port'], style='width: 25%')
                with li('User Name: ', cls='bbord'):
                    input(type='text', id='user', value=c[c_s]['Torrent']['QBittorrent']['user'], style='width: 50%')
                    span('Leave blank for none.', cls='tip')
                with li('Password: ', cls='bbord'):
                    input(type='text', id='pass', value=c[c_s]['Torrent']['QBittorrent']['pass'], style='width: 50%')
                    span('Leave blank for none.', cls='tip')
                with li('Category: ', cls='bbord'):
                    input(type='text', id='category', value=c[c_s]['Torrent']['QBittorrent']['category'], style='width: 50%')
                    span('i.e. \'movies\', \'watcher\'. ', cls='tip')

                with li():
                    with span(cls='test_connection', mode='qbittorrent'):
                        i(cls='fa fa-plug')
                        span('Test Connection')

        with div(id='save', cat='downloader'):
            i(cls='fa fa-save')
            span('Save Settings')

    @expose
    @settings_page
    def postprocessing(self, c):
        h1('Post-Processing')
        c_s = 'Postprocessing'
        with ul(id='postprocessing'):
            with li(cls='bbord'):
                i(id='cleanupfailed', cls='fa fa-square-o checkbox', value=str(c[c_s]['cleanupfailed']))
                span('Delete leftover files after a failed download.')
            with li():
                i(id='renamerenabled', cls='fa fa-square-o checkbox', value=str(c[c_s]['renamerenabled']))
                span('Enable Renamer')
            with li(cls='indent'):
                input(id='renamerstring', type='text', style='width: 80%', value=str(c[c_s]['renamerstring']), placeholder='{title} ({year}) {resolution}')
            with li(cls='indent bbord'):
                i(id='replacespaces', cls='fa fa-square-o checkbox', value=str(c[c_s]['replacespaces']))
                span('Replace spaces with periods.')
            with li():
                i(id='moverenabled', cls='fa fa-square-o checkbox', value=str(c[c_s]['moverenabled']))
                span('Enable Mover')
            with li(cls='indent'):
                span('Move movie file to: ')
                input(type='text', style='width: 24em', id='moverpath', value=c[c_s]['moverpath'])
                span('Use absolute path.', cls='tip')
            with li(cls='indent'):
                span('Move additional files:')
                input(type='text', style='width: 15em', id='moveextensions', value=c[c_s]['moveextensions'], placeholder='srt, nfo')
                span('Files will be renamed with Renamer settings.', cls='tip')
            with li(cls='indent'):
                i(id='createhardlink', cls='fa fa-square-o checkbox', value=str(c[c_s]['createhardlink']))
                span('Create hardlink to enable seeding torrents.')
                span('Will disable clean up.', cls='tip')
            with li(cls='indent'):
                i(id='cleanupenabled', cls='fa fa-square-o checkbox', value=str(c[c_s]['cleanupenabled']))
                span('Clean up after move.')
            with li('Replace illegal characters with: ', cls='indent'):
                input(type='text', id='replaceillegal', value=c[c_s]['replaceillegal'], style='width: 2em')
                with span('Cannot contain ', cls='tip'):
                    span('* ? " < > |', cls='charlist')
            with li(cls='indent bbord'):
                i(id='removeadditionalfiles', cls='fa fa-square-o checkbox', value=str(c[c_s]['removeadditionalfiles']))
                span('Delete associated files in target directory.')
                span('Remove any files with identical name, ie MovieName.srt', cls='tip')
            with li():
                i(id='recyclebinenabled', cls='fa fa-square-o checkbox', value=str(c[c_s]['recyclebinenabled']))
                span('Use "Recycle Bin" folder when redownloading a movie.')
            with li('Recycle Bin path: ', cls='indent bbord'):
                input(type='text', id='recyclebindirectory', value=c[c_s]['recyclebindirectory'], style='width: 15em')
            with li('Available tags:', cls='bbord'):
                br()
                span('{title}  {year}  {resolution}  {rated}  {imdbid}  {videocodec}  {audiocodec}  {releasegroup}  {source}  {quality}', cls='taglist')
                br()
                span('Example: ')
                span('{title} ({year}) - {resolution} = Night of the Living Dead (1968) - 1080P.mkv', cls='taglist')

        h2('Remote Mapping')
        with ul(id='remote_mapping'):
            with li(cls='tip'):
                span('If your download client is on a remote server you may need to map directories '
                     'so Watcher can access files.')
                br()
                span('See the ')
                a('wiki', href='https://github.com/nosmokingbandit/watcher3/wiki', target='_blank')
                span('for more information.')
            for remote, local in c[c_s]['RemoteMapping'].items():
                with li(cls='remote_mapping_row'):
                    span('Remote path: ')
                    input(cls='remote_path', placeholder=' /home/user/downloads/watcher', type='text', value=remote)
                    span('Local path: ')
                    input(cls='local_path', placeholder=' //server/downloads/watcher', type='text', value=local)
                    i(cls='fa fa-trash-o mapping_clear')
            with li():
                i(cls='fa fa-plus-square', id='add_remote_mapping_row')

        with div(id='save', cat='postprocessing'):
            i(cls='fa fa-save')
            span('Save Settings')

    @expose
    @settings_page
    def plugins(self, c):
        added = snatched = finished = []

        for root, dirs, filenames in os.walk(os.path.join(core.PROG_PATH, core.PLUGIN_DIR)):
            folder = os.path.split(root)[1]
            if folder == 'added':
                added = filenames
            elif folder == 'snatched':
                snatched = filenames
            elif folder == 'finished':
                finished = filenames
            else:
                continue

        with div(cls='plugins'):
            h1('Plugins')

            with ul('Added Movie', id='added', cls='sortable'):
                self.render_plugins(added, 'added')

            with ul('Snatched Release', id='snatched', cls='sortable'):
                self.render_plugins(snatched, 'snatched')

            with ul('Postprocessing Finished', id='finished', cls='sortable'):
                self.render_plugins(finished, 'finished')

            with span('See the '):
                a('wiki', href='https://github.com/nosmokingbandit/watcher3/wiki', target='_blank')
                span(' for plugin instructions.')

        with div(id='save', cat='plugins'):
            i(cls='fa fa-save')
            span('Save Settings')

    def render_plugins(self, plugins, folder):
        ''' Renders <li>s for plugins list
        plugins: list of plugin files. Absolute paths.
        folder: name of folder holding plugin files.

        'folder' is used to find data in config and set element ids and classes

        Returns str html list items
        '''

        c = core.CONFIG
        c_s = 'Plugins'

        fid = 0
        for plugin in plugins:
            if plugin.endswith('.py') is False or plugin.startswith('.') is True:
                continue
            name = plugin[:-3]

            if '{}.conf'.format(name) in plugins:
                conf = '{}.conf'.format(name)
            else:
                conf = None

            plug_conf = c[c_s][folder].get(plugin)
            if plug_conf is not None:
                enabled, sort = plug_conf
            else:
                sort = 900 + fid
                enabled = 'False'
            with li(id='{}{}'.format(folder, fid), plugin=plugin, sort=sort):
                i(cls='fa fa-bars')
                i(cls='fa fa-square-o checkbox', value=str(enabled))
                span(name)
                if conf:
                    i(cls='fa fa-cog edit_conf', conf=conf)
            fid += 1
        return

    @expose
    @settings_page
    def logs(self, c):
        options = self.get_logfiles()
        with div(cls='logs'):
            h1('Log File')
            with p():
                span('Log directory: ', cls='bold')
                span(os.path.join(core.PROG_PATH, core.LOG_DIR), cls='log_dir')
            with div(id='log_actions'):
                with select(id='log_file'):
                    for opt in options:
                        option(opt, value=opt)
                with span(id='view_log'):
                    i(cls='fa fa-file-text-o')
                    span('View log')
                with span(id='download_log'):
                    i(cls='fa fa-download')
                    span('Download log')

            pre(id='log_display')

    @expose
    @settings_page
    def about(self, c):
        with div(cls='about'):
            h1('About Watcher')

            h2('Source')
            with p():
                span('Watcher is hosted and maintained on GitHub. You may view the repository at ')
                a('https://github.com/', href='https://github.com/nosmokingbandit/watcher3')

            h2('License')
            with p():
                span('''
                    Watcher is open-source and licensed under the Apache 2.0 license. The essence of the
                    Apache 2.0 license is that any user can, for any reason, modify, distribute, or
                    repackage the licesed software with the condition that this license is included with,
                    and remains applicable to, any derivative works. You may not use the Watcher logo
                    or design elements without express approval by the owner. You may not hold the
                    developers of Watcher liable for any damages incurred from use.
                    '''
                     )
            with p():
                span('You may view the full, binding license at ')
                a('http://www.apache.org/', href='http://www.apache.org/licenses/LICENSE-2.0.html')
                span(' or in license.txt included in the root folder of Watcher.')
            h2('Attribution')
            with p():
                span('''
                    Watcher is only possible because of the amazing open-source works that are
                    included in this package. The Watcher license does not apply to these
                    properties. Please check each package's license requirements when using them
                    in your own work.
                    '''
                     )
            with ul(id='libraries'):
                with li():
                    a('CherryPy', href='http://cherrypy.org/')
                with li():
                    a('SQLAlchemy', href='http://www.sqlalchemy.org/')
                with li():
                    a('Six', href='https://pypi.python.org/pypi/six')
                with li():
                    a('FuzzWuzzy', href='https://pypi.python.org/pypi/fuzzywuzzy')
                with li():
                    a('Font-Awesome', href='http://fontawesome.io/')
                with li():
                    a('JQuery', href='https://jquery.com/')
                with li():
                    a('Parse Torrent Name', href='https://pypi.python.org/pypi/parse-torrent-name')

    def get_themes(self):
        ''' Returns list of folders in static/css/
        '''

        theme_path = os.path.join(core.PROG_PATH, 'static', 'css')
        themes = []
        for i in os.listdir(theme_path):
            if os.path.isdir(os.path.join(theme_path, i)):
                themes.append(i)
        themes.append('Default')
        return themes

    def get_logfiles(self):
        ''' Returns list of logfiles in core.LOG_DIR
        '''

        logfiles = []
        logfiles_tmp = []
        files = os.listdir(core.LOG_DIR)

        for i in files:
            if os.path.isfile(os.path.join(core.LOG_DIR, i)):
                logfiles_tmp.append(i)

        logfiles.append(logfiles_tmp.pop(0))

        for i in logfiles_tmp[::-1]:
            logfiles.append(i)

        return logfiles

# pylama:ignore=W0401
