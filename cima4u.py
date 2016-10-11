# -*- coding: utf-8 -*-
import os
import re
import sys
import urllib
from urlparse import parse_qsl
import cf
import easy_cache
#import requests
import urlresolver

try:
    import YDStreamExtractor

    yd = True
except ImportError:
    yd = False

from bs4 import BeautifulSoup

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

scraper = cf.create_scraper()
# important variables
_plugin_handle = int(sys.argv[1])
_plugin_url = sys.argv[0]
_plugin_id = xbmcaddon.Addon().getAddonInfo('id')
plugin_path = xbmcaddon.Addon().getAddonInfo('path')
FavsDir = xbmc.translatePath("special://profile/addon_data/" + _plugin_id + "/")
FavsFile = xbmc.translatePath("special://profile/addon_data/" + _plugin_id + "/favorites")
CacheFile = xbmc.translatePath("special://profile/addon_data/" + _plugin_id + "/cache")
user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
headers = {'User-Agent': user_agent}
dialog = xbmcgui.Dialog()
unsupported_servers = ('Videorev', 'THEVID', 'Estream', 'FlashX', 'Mail')
locally_supported_servers = ('vidbom', 'vidshare', 'vidtodo')
rmv_txt = 'مشاهدة فيلم '

# art variables
plugin_fanart = xbmcaddon.Addon().getAddonInfo('fanart')
plugin_icon = xbmcaddon.Addon().getAddonInfo('icon')
art_path = os.path.join(plugin_path, 'resources', 'art')
folder_thumb = os.path.join(art_path, 'folder.png')
settings_thumb = os.path.join(art_path, 'settings.png')
search_thumb = os.path.join(art_path, 'search.png')
like_thumb = os.path.join(art_path, 'like.png')
new_thumb = os.path.join(art_path, 'new.png')
popular_thumb = os.path.join(art_path, 'popular.png')
next_page_thumb = os.path.join(art_path, 'nextpage.png')
# important website urls
# website main url
base_url = 'http://cima4u.tv/'
# arabic movies
arabic_movies_url = 'http://cima4u.tv/category/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%B9%D8%B1%D8%A8%D9%8A-arabic-movies/'
# english movies
english_movies_url = 'http://cima4u.tv/category/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D8%AC%D9%86%D8%A8%D9%8A-movies-english/'
# cartoon
cartoon_url = 'http://cima4u.tv/category/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D9%83%D8%B1%D8%AA%D9%88%D9%86-movies-anime-cartoon/'
# free wrestling
free_wrestling_url = 'http://cima4u.tv/category/%D9%85%D8%B5%D8%A7%D8%B1%D8%B9%D8%A9-%D8%AD%D8%B1%D8%A9-wwe/'
# indian movies
indian_movies = 'http://cima4u.tv/category/%D8%A7%D9%81%D9%84%D8%A7%D9%85-%D9%87%D9%86%D8%AF%D9%8A-indian-movies/'
# series
egypt_series_url = 'http://live.cima4u.tv/10.%D9%85%D8%B3%D9%84%D8%B3%D9%84%D8%A7%D8%AA+%D9%85%D8%B5%D8%B1%D9%8A%D9%87.html'
gulf_series_url = 'http://live.cima4u.tv/11.%D9%85%D8%B3%D9%84%D8%B3%D9%84%D8%A7%D8%AA+%D8%AE%D9%84%D9%8A%D8%AC%D9%8A%D9%87.html'
english_series_url = 'http://live.cima4u.tv/25.%D9%85%D8%B3%D9%84%D8%B3%D9%84%D8%A7%D8%AA+%D8%A7%D8%AC%D9%86%D8%A8%D9%89.html'
turkish_se_trans_url = 'http://live.cima4u.tv/13.%D9%85%D8%B3%D9%84%D8%B3%D9%84%D8%A7%D8%AA+%D8%AA%D8%B1%D9%83%D9%8A%D9%87+%D9%85%D8%AA%D8%B1%D8%AC%D9%85%D9%87.html'
turkish_se_dub_url = 'http://live.cima4u.tv/14.%D9%85%D8%B3%D9%84%D8%B3%D9%84%D8%A7%D8%AA+%D8%AA%D8%B1%D9%83%D9%8A%D9%87+%D9%85%D8%AF%D8%A8%D9%84%D8%AC%D9%87.html'
cartoon_ani_se_trans = 'http://live.cima4u.tv/17.%D9%85%D8%B3%D9%84%D8%B3%D9%84%D8%A7%D8%AA+%D8%A7%D9%86%D9%8A%D9%85%D9%8A+%D9%85%D8%AA%D8%B1%D8%AC%D9%85%D8%A9.html'
cartoon_ani_se_dub = 'http://live.cima4u.tv/16.%D9%85%D8%B3%D9%84%D8%B3%D9%84%D8%A7%D8%AA+%D8%A7%D9%86%D9%8A%D9%85%D9%8A+%D9%85%D8%AF%D8%A8%D9%84%D8%AC%D8%A9.html'
asian_se_trans = 'http://live.cima4u.tv/19.%D9%85%D8%B3%D9%84%D8%B3%D9%84%D8%A7%D8%AA+%D8%A7%D8%B3%D9%8A%D9%88%D9%8A%D8%A9+%D9%85%D8%AA%D8%B1%D8%AC%D9%85%D8%A9.html'
asian_se_dub = 'http://live.cima4u.tv/20.%D9%85%D8%B3%D9%84%D8%B3%D9%84%D8%A7%D8%AA+%D8%A7%D8%B3%D9%8A%D9%88%D9%8A%D8%A9+%D9%85%D8%AF%D8%A8%D9%84%D8%AC%D8%A9.html'
indian_se_trans = 'http://live.cima4u.tv/23.%D9%85%D8%B3%D9%84%D8%B3%D9%84%D8%A7%D8%AA+%D9%87%D9%86%D8%AF%D9%8A%D8%A9+%D9%85%D8%AA%D8%B1%D8%AC%D9%85%D8%A9.html'
indian_se_dub = 'http://live.cima4u.tv/22.%D9%85%D8%B3%D9%84%D8%B3%D9%84%D8%A7%D8%AA+%D9%87%D9%86%D8%AF%D9%8A%D8%A9+%D9%85%D8%AF%D8%A8%D9%84%D8%AC%D8%A9.html'
ramadan_sixten = 'http://live.cima4u.tv/28.%D9%85%D8%B3%D9%84%D8%B3%D9%84%D8%A7%D8%AA+%D8%B1%D9%85%D8%B6%D8%A7%D9%86+2016.html'
tv_shows_url = 'http://live.cima4u.tv/24.%D8%A8%D8%B1%D8%A7%D9%85%D8%AC+%D8%AA%D9%84%D9%81%D8%B2%D9%8A%D9%88%D9%86%D9%8A%D8%A9.html'
# search
search_url = ('http://cima4u.tv/?s=', 'http://live.cima4u.tv/Search?q=')
# http://live.cima4u.tv/structure/server.php?id=
serverphp_url = 'http://live.cima4u.tv/structure/server.php'

# important settings
open_load_yd = xbmcplugin.getSetting(_plugin_handle, 'open_load_yd')
#detalis = xbmcplugin.getSetting(_plugin_handle, 'Show_Movie_details')
detalis = 'false'
# for better viewing
xbmcplugin.setContent(_plugin_handle, 'musicvideos')


def categories():
    add_dir('[COLOR gold]Arabic Movies[/COLOR]', arabic_movies_url, 'GetMovies', folder_thumb)
    add_dir('[COLOR gold]English Movies[/COLOR]', english_movies_url, 'GetMovies', folder_thumb)
    add_dir('[COLOR gold]Indian Movies[/COLOR]', indian_movies, 'GetMovies', folder_thumb)
    add_dir('[COLOR gold]Cartoon[/COLOR]', cartoon_url, 'GetMovies', folder_thumb)
    add_dir('[COLOR gold]Egyptian Series[/COLOR]', egypt_series_url, 'GetSeries', folder_thumb)
    add_dir('[COLOR gold]Ramadan 2016 Series[/COLOR]', ramadan_sixten, 'GetSeries', folder_thumb)
    add_dir('[COLOR gold]Other Series[/COLOR]', '', 'OtherSeries', folder_thumb)
    add_dir('[COLOR gold]TV SHOWS[/COLOR]', tv_shows_url, 'GetSeries', folder_thumb)
    add_dir('[COLOR gold]free wrestling[/COLOR]', free_wrestling_url, 'GetMovies', folder_thumb)
    add_dir('[COLOR gold]List: [/COLOR]Watch Later', '', 'GetFav', folder_thumb)
    add_dir('Search', '', 'Search', search_thumb)
    add_dir('[COLOR red]Settings[/COLOR]', 'settings', 'OpenSettings', settings_thumb)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def other_series():
    add_dir('[COLOR gold]مسلسلات خليجي[/COLOR]', gulf_series_url, 'GetSeries', folder_thumb)
    add_dir('[COLOR gold]مسلسلات اجنبيه[/COLOR]', english_series_url, 'GetSeries', folder_thumb)
    add_dir('[COLOR gold]مسلسلات تركيه مترجمه[/COLOR]', turkish_se_trans_url, 'GetSeries', folder_thumb)
    add_dir('[COLOR gold]مسلسلات تركيه مدبلجه[/COLOR]', turkish_se_dub_url, 'GetSeries', folder_thumb)
    add_dir('[COLOR gold]مسلسلات انيمي مترجمه[/COLOR]', cartoon_ani_se_trans, 'GetSeries', folder_thumb)
    add_dir('[COLOR gold]مسلسلات انيمي مدبلجه[/COLOR]', cartoon_ani_se_dub, 'GetSeries', folder_thumb)
    add_dir('[COLOR gold]مسلسلات اسيويه مترجمه[/COLOR]', asian_se_trans, 'GetSeries', folder_thumb)
    add_dir('[COLOR gold]مسلسلات اسيويه مدبلجه[/COLOR]', asian_se_dub, 'GetSeries', folder_thumb)
    add_dir('[COLOR gold]مسلسلات هنديه مترجمه[/COLOR]', indian_se_trans, 'GetSeries', new_thumb)
    add_dir('[COLOR gold]مسلسلات هنديه مدبلجه[/COLOR]', indian_se_dub, 'GetSeries', folder_thumb)
    add_dir('Search', '', 'Search', search_thumb)
    add_dir('[COLOR red]Settings[/COLOR]', 'settings', 'OpenSettings', settings_thumb)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    exit()


def get_videos(url, is_this_page=False):
    content = open_this_url(url)
    soup = BeautifulSoup(content)
    all_videos = soup.find_all("div", class_="block")
    for video in all_videos:
        video_page = video.a['href']
        video_thumb = video.a.div.div['style']
        video_views = video.a.div.find_next_siblings()[0].get_text()
        video_name = video.a.div.find_next_siblings()[2].get_text()
        video_desc = video.a.div.find_next_siblings()[3].get_text()
        thumb = re.compile('url\((.*?)\)').findall(video_thumb)[0]
        title = video_name.encode('utf-8').strip()
        title = title.replace(rmv_txt, '')
        page = video_page.encode('utf-8').strip()
        thumb = thumb.encode('utf8', 'replace').strip()
        video_desc = video_desc.encode('utf-8').strip()
        if detalis == 'true':
            video_url, video_story, video_year = get_movie_detalis(page)
            add_link(title, page, 'GetServers', thumb, video_views, video_desc, video_story, video_year)
        else:
            add_link(title, page, 'GetServers', thumb, video_views, video_desc)

    # add pagination
    next_page_url = soup.find_all('div', class_='pagination')[0]
    list_pages = next_page_url.find_all('li')
    for li_p in list_pages:
        if li_p.a and not li_p.has_attr('class'):
            url = li_p.a['href'].encode('utf-8').strip()
            txt = li_p.get_text().encode('utf-8').strip()
            if 'التالية' in txt:
                txt = '[COLOR gold]' + '< الصفحة التالية' + '[/COLOR]'
            elif 'السابقة' in txt:
                txt = '[COLOR gold]' + 'الصفحة السابقة >' + '[/COLOR]'
            else:
                txt = '[COLOR gold]' + '--- صفحه ' + txt + ' ---' + '[/COLOR]'

            add_dir(txt, url, 'GetPgaeMovies', next_page_thumb)
    if is_this_page:
        xbmcplugin.endOfDirectory(int(sys.argv[1]), updateListing=True)
    else:
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    exit()


@easy_cache.persist_to_file(CacheFile)
def open_this_url(url):
    try:
        req = scraper.get(url)
    except:
        dialog.ok('Error', 'Check your internet connection')
    return req.content


def get_series(url, is_this_page=False):
    content = open_this_url(url)
    soup = BeautifulSoup(content)
    # Get Movies-series #dataTab > div:nth-child(1)
    all_videos = soup.find_all("div", class_="block")
    for video in all_videos:
        video_page = video.a['href']
        video_thumb = video.a.div.div['style']
        video_views = video.a.div.find_next_siblings()[0].get_text()
        video_name = video.a.find_next_siblings()[0].get_text()
        thumb = re.compile('url\((.*?)\)').findall(video_thumb)[0]
        title = video_name.encode('utf-8', 'replace').strip()
        # title = title.replace(rmv_txt, '')
        page = video_page.encode('utf-8', 'replace').strip()
        thumb = thumb.encode('utf8', 'replace').strip()
        add_link(title, page, 'ChooseEpisode', thumb, video_views)
    try:
        next_page_url = soup.find_all('ul', class_='pagination')[0]
        list_pages = next_page_url.find_all('li')
        for li_p in list_pages:
            if li_p.a and not li_p.has_attr('class'):
                try:
                    url = li_p.a['href'].encode('utf-8', 'replace').strip()
                    txt = li_p.get_text().encode('utf-8', 'replace').strip()
                    if 'التالى' in txt:
                        txt = '[COLOR gold]' + '< الصفحة التالية' + '[/COLOR]'
                    elif 'السابق' in txt:
                        txt = '[COLOR gold]' + 'الصفحة السابقة >' + '[/COLOR]'
                    else:
                        txt = '[COLOR gold]' + '--- صفحه ' + txt + ' ---' + '[/COLOR]'
                    add_dir(txt, url, 'GetPageSeries', next_page_thumb)
                except:
                    pass
    except:
        pass
    if is_this_page:
        xbmcplugin.endOfDirectory(int(sys.argv[1]), updateListing=True)
    else:
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    exit()


# def filter_title(string):
#     querywords = string.split()
#     resultwords = [word for word in querywords if word() not in removewords]
#     result = ' '.join(resultwords)
#     return result


def search():
    keyboard = xbmc.Keyboard("", "search keyword", False)
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText() != "":
        text = keyboard.getText()
        ret = dialog.select('Search in', ('cima4u.tv', 'live.cima4u.tv'))
        url = str(search_url[ret]) + text
        if ret == 0:
            # search movies
            get_videos(url)
        elif ret == 1:
            # search series
            get_series(url)
        elif ret == -1:
            # canceled
            pass
    else:
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        exit()


def choose_episode(url):
    content = open_this_url(url)
    soup = BeautifulSoup(content)
    # episodes
    episodes = soup.find_all('div', class_='col-md-2')
    episodes_names = list(epi.a.get_text() for epi in episodes)
    ret = dialog.select('select episode', episodes_names)
    if ret == -1:
        exit()
    episode_link = episodes[ret].a['href']
    fetch_servers_links(episode_link)


def get_movie_detalis(url):
    try:
        content = open_this_url(url)
        soup = BeautifulSoup(content)
        # مشاهده الان #
        link = soup.find_all('div', class_='leftDetails')[0]
        movie_link = link.a['href']
        # قصة الفيلم #
        movie_story = link.div.find_next_siblings()[0].get_text()
        if movie_story:
            movie_story = (movie_story.encode('utf-8', 'replace').strip())
        else:
            movie_story = ''
        # سنه الفيلم #
        link = soup.find_all('div', class_='rightDetails')[0]
        movie_year = link.div.p.find_next_siblings()[1].a.get_text()
        return movie_link, movie_story, movie_year
    except:
        return '', '', ''


def get_movie_page(url):
    content = open_this_url(url)
    soup = BeautifulSoup(content)
    link = soup.find_all('div', class_='leftDetails')[0]
    movie_link = link.a['href']
    fetch_servers_links(movie_link)


def fetch_servers_links(url):
    content = open_this_url(url)
    soup = BeautifulSoup(content)
    servers = soup.find_all('a', class_='sever_link')
    servers_names = list(server.get_text() for server in servers)
    # mark unsupported servers with red
    for i in range(0, len(servers_names)):
        if any(server in servers_names[i] for server in unsupported_servers):
            servers_names[i] = '[COLOR red]' + servers_names[i] + '[/COLOR]'
    #
    ret = dialog.select('select server', servers_names)
    if ret == -1:
        exit()
    content = scraper.get(serverphp_url, params={'id': servers[int(ret)]['data-link']}).content
    soup = BeautifulSoup(content)
    link = soup.iframe['src']
    link_resolvers(link, servers_names[int(ret)])


def link_resolvers(link, server_name):
    # we have few options to resolve the video link
    # 1 - urlresolver
    if urlresolver.HostedMediaFile(link) and ('openload' not in link or open_load_yd == 'false'):
        # urlresolver think it could resolve this url
        dialog.notification('using urlresolver module', 'trying to resolve this url..', xbmcgui.NOTIFICATION_INFO, 2000)
        stream_url = urlresolver.resolve(link)
        if stream_url:
            play(stream_url)
        else:
            dialog.notification(server_name, 'URLresolver Failed to resolve this url!',
                                xbmcgui.NOTIFICATION_INFO,
                                2000)

    # 2 - if urlresolver can't solve the url check if it can solved locally by this addon
    elif any(server in link for server in locally_supported_servers):
        dialog.notification('using local resolver', 'trying to resolve this url..', xbmcgui.NOTIFICATION_INFO, 2000)
        stream_url = resolve_this_locally(link)
        play(stream_url)
    # 3 - now last try solve by YDownloader module ( it will solve extra links like mystream , tubetv)
    elif yd is True:
        if YDStreamExtractor.mightHaveVideo(link, True):
            # YDownloader think it could resolve this url
            vid = YDStreamExtractor.getVideoInfo(link, quality=2)
            if vid:
                dialog.notification('using YD resolver', 'trying to resolve this url..', xbmcgui.NOTIFICATION_INFO,
                                    2000)
                choices = []
                if vid.hasMultipleStreams():
                    for s in vid.streams():
                        title = s['title']
                        choices.append(title)
                    index = dialog.select('choose stream', choices)
                    exit() if index == -1 else vid.selectStream(index)
                stream_url = vid.streamURL()
                play(stream_url)
            else:
                # YDownloader failed to resolve this url
                dialog.notification(server_name, 'YD Failed to resolve this url!',
                                    xbmcgui.NOTIFICATION_INFO,
                                    2000)
                xbmcplugin.setResolvedUrl(_plugin_handle, False,
                                          xbmcgui.ListItem())
    else:
        # we didn't find any resolver for this link
        dialog.notification('Unsupported Server',
                            'This Server Not Supported yet by This Addon Or URLResolver\'s Modules!',
                            xbmcgui.NOTIFICATION_INFO,
                            5000)
        xbmcplugin.setResolvedUrl(_plugin_handle, False,
                                  xbmcgui.ListItem())
    exit()


def resolve_this_locally(url):
    """ resolve vidtodo , vidbom and vidshare links """
    content = open_this_url(url)
    if 'vidtodo' in url:
        # vidtodo
        videos = re.compile('(http://[\.\w/_]+\.mp4)').findall(content)
        if len(videos) > 1:
            ret = dialog.select('Choose a Video Link', videos)
            if ret == -1:
                exit()
            return videos[ret]
        else:
            return videos[0]
    else:
        # vidbom vidshare
        videos = re.compile(',\{file:"(.*?)",label:"(.*?)"').findall(content)
        video_link = [x[0] for x in videos]
        video_res = [x[1] for x in videos]
        if len(videos) > 1:
            ret = dialog.select('Choose a Video Link', video_res)
            if ret == -1:
                exit()
            return video_link[ret]
        else:
            return video_link[0]


def play(stream_url):
    xbmcplugin.setResolvedUrl(_plugin_handle, True,
                              xbmcgui.ListItem(path=stream_url))
    exit()


def add_to_watch_later(params):
    fav = '###name###' + params['name']
    fav += '###url###' + params['url']
    fav += '###thumb###' + params['thumb']
    fav += '###mode###'+params['mode']
    fav += '###end###'
    if os.path.exists(FavsFile):
        fh = open(FavsFile, 'r')
        content = fh.read()
        fh.close()
        if content.find('###name###' + params['name']) == -1:
            fh = open(FavsFile, 'a')
            fh.write(fav)
            fh.close()
            dialog.notification('Added', 'you add new video to your watch later list',
                                xbmcgui.NOTIFICATION_INFO, 2000)
        else:
            dialog.notification('hey', 'you already added this video before.',
                                xbmcgui.NOTIFICATION_INFO, 2000)
    else:
        if not os.path.exists(FavsDir):
            os.makedirs(FavsDir)
        fh = open(FavsFile, 'w+')
        fh.write(fav + "\n")
        fh.close()
        dialog.notification('Added', 'you created a watch later list and added new video to it',
                            xbmcgui.NOTIFICATION_INFO, 2000)
    exit()


def del_from_watch_later(params):
    fh = open(FavsFile, 'r')
    filedata = fh.read()
    fh.close()
    fav = '###name###' + params['name']
    fav += '###url###' + params['url']
    fav += '###thumb###' + params['thumb']
    fav += '###mode###'+params['mode']
    fav += '###end###'
    newdata = filedata.replace(fav, "")
    fh = open(FavsFile, 'w')
    fh.write(newdata)
    fh.close()
    xbmc.executebuiltin("Container.Refresh")
    exit()


def read_watch_later_list():
    if os.path.exists(FavsFile):
        fh = open(FavsFile, 'r')
        content = fh.read()
        fh.close()
        match = re.compile('###name###(.+?)###url###(.+?)###thumb###(.+?)###mode###(.+?)###end###').findall(content)
        for name, url, thumb, mode in match:
            add_link(name, url, mode, thumb, fav=True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    else:
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        dialog.notification('Empty Watch List', '',
                            xbmcgui.NOTIFICATION_INFO, 2000)
    exit()


def add_dir(name, url, mode, thumb):
    u = _plugin_url + "?url=" + urllib.quote_plus(url) + "&mode=" + mode + "&name=" + urllib.quote_plus(
        name)
    liz = xbmcgui.ListItem(name)
    liz.setArt({'thumb': thumb, 'landscape': thumb, 'fanart': plugin_fanart})
    xbmcplugin.addDirectoryItem(handle=_plugin_handle, url=u, listitem=liz, isFolder=True)
    return


def add_link(name, url, mode, thumb, views=0, small_desc='', desc='', video_date='', fav=False):
    u = _plugin_url + "?url=" + url + "&mode=" + mode + "&name=" + urllib.quote_plus(name)
    liz = xbmcgui.ListItem(name)
    if mode == 'ChooseEpisode' or detalis == 'false':
        # series info labels
        liz.setInfo(type="Video",
                    infoLabels={'title': name, 'userRating': views, 'tagline': small_desc, 'plot': desc,
                                'mediatype': 'movie'})
    else:
        liz.setInfo(type="Video",
                    infoLabels={'title': name, 'userRating': views, 'tagline': small_desc, 'plot': desc,
                                'year': video_date, 'premiered': video_date,
                                'date': video_date, 'mediatype': 'movie'})

    liz.setArt({'poster': thumb, 'thumb': thumb, 'landscape': thumb, 'fanart': thumb})
    liz.setProperty("IsPlayable", "true")

    context_menu_items = []
    if fav:
        context_menu_items.append(('Remove From watch later list',
                                   'XBMC.RunPlugin(%s?mode=%s&name=%s&url=%s&thumb=%s&fav=%s)' % (
                                       sys.argv[0], mode, urllib.quote_plus(name), urllib.quote_plus(url),
                                       urllib.quote_plus(thumb), 'DEL')))
        context_menu_items.append(('Remove all the list', 'XBMC.RunPlugin(%s?mode=ClearFavList)' % (sys.argv[0])))
    else:
        context_menu_items.append(
            ('Add to watch later list', 'XBMC.RunPlugin(%s?mode=%s&name=%s&url=%s&thumb=%s&fav=%s)' % (
                sys.argv[0], mode, urllib.quote_plus(name), urllib.quote_plus(url), urllib.quote_plus(thumb), 'ADD')))
    context_menu_items.append(('Refresh Content', 'Container.Refresh'))
    liz.addContextMenuItems(context_menu_items)
    xbmcplugin.addDirectoryItem(handle=_plugin_handle, url=u, listitem=liz, isFolder=False)
    return


def router(params_string):
    params = dict(parse_qsl(params_string))
    if params:
        if params.get('fav') == 'ADD':
            add_to_watch_later(params)
        elif params.get('fav') == 'DEL':
            del_from_watch_later(params)
        elif params.get('mode') == 'GetServers' or params.get('mode') == 'GetFavMovieServers':
            get_movie_page(params['url'])
        elif params.get('mode') == 'OpenSettings':
            xbmcaddon.Addon().openSettings()
        elif params.get('mode') == 'Search':
            search()
        elif params.get('mode') == 'GetMovies':
            get_videos(params['url'])
        elif params.get('mode') == 'GetPgaeMovies':
            get_videos(params['url'], is_this_page=True)
        elif params.get('mode') == 'ChooseEpisode':
            choose_episode(params['url'])
        elif params.get('mode') == 'GetSeries':
            get_series(params['url'])
        elif params.get('mode') == 'GetPageSeries':
            get_series(params['url'], is_this_page=True)
        elif params.get('mode') == 'OtherSeries':
            other_series()
        # elif params.get('mode') == 'AddFav':
        #    add_to_watch_later(params)
        # elif params.get('mode') == 'DelFav':
        #     del_from_watch_later(params)
        elif params.get('mode') == 'GetFav':
            read_watch_later_list()
        elif params.get('mode') == 'ClearFavList':
            ret = dialog.yesno('Clear Your Watch List', 'Are You Sure? All Videos in This List will removed!')
            if ret == 1:
                os.remove(FavsFile)
                xbmc.executebuiltin("Container.Refresh")
                dialog.notification('Watch List Cleared', '',
                                    xbmcgui.NOTIFICATION_INFO, 2000)
    else:
        # plugin called from kodi gui without any parameters
        categories()


if __name__ == '__main__':
    # call the router function and pass the plugin parameters to it.
    router(sys.argv[2][1:])
