from xbmcswift import Module, download_page as _download_page
from BeautifulSoup import BeautifulSoup as BS
from urllib import urlencode
import cookielib
import urllib2
import os
from urlparse import urljoin
from xbmcswift import xbmcgui

favorites = Module('favorites')
BASE_URL = 'http://academicearth.org'
def full_url(path):
    return urljoin(BASE_URL, path)
LOGIN_URL = full_url('users/login')

def htmlify(url):
    return BS(s.download_page(url))

class AuthSession(object):
    '''This class handles cookies and session information.'''
    def __init__(self, get_cookie_fn_method):
        self.cookie_jar = None
        self.opener = None
        self.get_cookie_fn = get_cookie_fn_method
        self.authenticated = False

    def load_cookies_from_disk(self):
        try:
            self.cookie_jar.load(ignore_discard=True, ignore_expires=True)
        except IOError:
            pass
        
    def _set_opener(self, cookie_jar):
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))

    def _set_cookie_jar(self):
        self.cookie_jar_path = self.get_cookie_fn()
        if not os.path.exists(os.path.dirname(self.cookie_jar_path)):
            os.makedirs(os.path.dirname(self.cookie_jar_path))
        self.cookie_jar = cookielib.LWPCookieJar(self.cookie_jar_path)

    def authenticate(self, username=None, password=None):
        username = username or favorites._plugin.get_setting('username')
        password = password or favorites._plugin.get_setting('password')

        params = {
            '_method': 'POST',
            'data[User][username]': username,
            'data[User][password]': password,
            'data[User][goto]': '//',
            'header-login-submit': 'Login',
        }
        resp = self.opener.open(LOGIN_URL, urlencode(params))

        print 'LOGIN RESP.URL', resp.geturl()

        if resp.geturl().startswith(LOGIN_URL):
            dialog = xbmcgui.Dialog()
            dialog.ok('Academic Earth', 'It seems your username/password aren\'t valid.')
            favorites._plugin.open_settings()
            return False

        self.cookie_jar.save(ignore_discard=True, ignore_expires=True)

    def download_page(self, url):
        if not self.cookie_jar:
            self._set_cookie_jar()
            self._set_opener(self.cookie_jar)
        self.load_cookies_from_disk()

        resp = self.opener.open(url)

        # We need to check if we were redirected to the login page. If we were
        # then we'll call authenticate which should log in properly. If the
        # call to authenticate returns False, then there was a problem logging
        # in so we should just return None.
        if resp.geturl() == LOGIN_URL + '/':
            if self.authenticate() is False:
                return None

        resp = self.opener.open(url)
        return resp.read()

def get_cookie_fn():
    return favorites._plugin.cache_fn('.cookies')
s = AuthSession(get_cookie_fn)

## View functions for favorites
@favorites.route('/', url=full_url('favorites'))
def show_favorites(url):
    '''Shows your favorite videos from http://acadmemicearth.org/favorites.'
    '''
    src = s.download_page(url)
    if not src:
        return
    html = BS(src)

    #html = htmlify(url)
    videos = html.find('ul', {'class': 'favorites-list'}).findAll('li')

    items = [{
        'label': item.h3.a.string,
        'url': favorites.url_for('watch_lecture',
                                 url=full_url(item.h3.a['href'])),
        'thumbnail': full_url(item.img['src']),
        'is_folder': False,
        'is_playable': True,
        'context_menu': [
            ('Remove from website favorites', 
             'XBMC.RunPlugin(%s)' % favorites.url_for(
                'favorites.remove_lecture',
                url=full_url(item.find('div', {'class': 'delete'}).a['href'])
            )),
        ],
    } for item in videos]

    return favorites.add_items(items)

@favorites.route('/remove/<url>/')
def remove_lecture(url):
    '''This is a context menu view to remove an item from a user's favorites on
    academciearth.org'''
    if not s.download_page(url):
        xbmcgui.Dialog().ok('Academic Earth', 'There was a problem removing the item from your website favorites.')

@favorites.route('/add/<url>/')
def add_lecture(url):
    '''This is a context menu view to add an item to a user's favorites on
    academciearth.org'''
    if not s.download_page(url):
        xbmcgui.Dialog().ok('Academic Earth', 'There was a problem adding the item to your website favorites.')
