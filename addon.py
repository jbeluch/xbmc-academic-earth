#!/usr/bin/env python
# Copyright 2011 Jonathan Beluch.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import re
from xbmcswift2 import Plugin, download_page, xbmcgui
from BeautifulSoup import BeautifulSoup as BS, SoupStrainer as SS
from urlparse import urljoin
from resources.lib.videohosts import resolve
from resources.lib.favorites import favorites


PLUGIN_NAME = 'Academic Earth'
PLUGIN_ID = 'plugin.video.academicearth'
plugin = Plugin(PLUGIN_NAME, PLUGIN_ID, __file__)
plugin.register_module(favorites, '/favorites')


BASE_URL = 'http://academicearth.org'
def full_url(path):
    '''Creates a full academicearth.org url from a relative path'''
    return urljoin(BASE_URL, path)


def htmlify(url):
    '''Returns a BeautifulSoup object for the given url's content.'''
    return BS(download_page(url), convertEntities=BS.HTML_ENTITIES)


def filter_free(items):
    '''Filters a list of items to remove "non-free" items'''
    return [item for item in items if not item['label'].startswith('Online')]


def is_course(url):
    '''Returns True if the given url is for a course.'''
    return '/courses/' in url


def is_lecture(url):
    '''Returns True if the given url is for a lecture.'''
    return '/lectures/' in url


@plugin.route('/')
def show_index():
    '''Main menu'''
    items = [
        {'label': plugin.get_string(30200),
         'path': plugin.url_for('show_subjects')},
        {'label': plugin.get_string(30201),
         'path': plugin.url_for('show_universities')},
        {'label': plugin.get_string(30202),
         'path': plugin.url_for('show_instructors')},
        {'label': plugin.get_string(30203),
         'path': plugin.url_for('show_top_instructors')},
        {'label': plugin.get_string(30204),
         'path': plugin.url_for('show_playlists')},
        {'label': plugin.get_string(30205),
         'path': plugin.url_for('favorites.show_favorites')},
    ]
    return items


@plugin.cached_route('/subjects/', options={'url': full_url('subjects')})
def show_subjects(url):
    '''Lists available subjects found on the website'''
    html = htmlify(url)
    subjects = html.findAll('a', {'class': 'subj-links'})

    items = [{
        'label': subject.div.string.strip(),
        'path': plugin.url_for('show_topics', url=full_url(subject['href'])),
    } for subject in subjects]
    return filter_free(items)


@plugin.cached_route('/universities/', options={'url': full_url('universities')})
def show_universities(url):
    '''Lists available universities found on the website'''
    html = htmlify(url)
    universities = html.findAll('a', {'class': 'subj-links'})

    items = [{
        'label': item.div.string.strip(),
        'path': plugin.url_for('show_topics', url=full_url(item['href'])),
    } for item in universities]
    return items


@plugin.route('/instructors/', options={'page': '1'})
@plugin.route('/instructors/<page>/', name='show_instructors_page')
def show_instructors(page):
    '''Lists instructors found on the website. Since the list is long,
    this view includes pagination list items.
    '''
    def get_pagination(html):
        items = []
        previous = html.find('span',
                             {'class': 'tab-nav-arrow tab-nav-arrow-l'})
        if int(page) > 1:
            items.append({
                'label': '< Previous',
                'path': plugin.url_for('show_instructors_page',
                                       page=str(int(page)-1)),
            })

        next = html.find('span', {'class': 'tab-nav-arrow tab-nav-arrow-r'})
        if next:
            items.append({
                'label': 'Next >',
                'path': plugin.url_for('show_instructors_page',
                                       page=str(int(page)+1)),
            })
        return items

    @plugin.cache()
    def get_instructor_items(page):
        '''This function exists so we can cache the return value based
        on the unique page number. Since we are passing a value for
        update_listing to plugin.finish() below, we cannot use the
        cached_route decorator since it doesn't keep track of side
        effects like values passed to endOfDirectory().
        '''
        url = full_url('speakers/page:%s' % page)
        html = htmlify(url)
        speakers = html.findAll('div', {'class': 'blue-hover'})

        items = [{
            'label': item.div.string,
            'path': plugin.url_for('show_instructor_courses',
                                   url=full_url(item.a['href'])),
        } for item in speakers]

        # Add pagination
        return get_pagination(html) + items

    return plugin.finish(get_instructor_items(page), update_listing=page!='1')


@plugin.cached_route('/topinstructors/', options={'url': BASE_URL})
def show_top_instructors(url):
    '''Displays the top instructors from the website homepage.'''
    html = htmlify(url)
    menu = html.find('ul', {'id': 'categories-accordion'})
    speakers = menu.findAll('a', {'class': 'accordion-item',
                                  'href': lambda h: '/speakers/' in h})

    items = [{
        'label': item.string,
        'path': plugin.url_for('show_instructor_courses',
                               url=full_url(item['href'])),
    } for item in speakers]
    return items


@plugin.cached_route('/playlists/', options={'url': full_url('playlists')})
def show_playlists(url):
    '''Displays playlists found on the website.'''
    html = htmlify(url)
    playlists = html.find('ol', {'class': 'playlist-list'}).findAll('li', recursive=False)

    items = [{
        'label': item.h4.findAll('a')[-1].string,
        'path': plugin.url_for('show_lectures', url=full_url(item.a['href'])),
        'thumbnail': full_url(item.find('img', {'width': '144'})['src']),
    } for item in playlists]
    return items


@plugin.cached_route('/instructors/courses/<url>/')
def show_instructor_courses(url):
    '''Displays courses and lectures taught by a specific speaker.'''
    html = htmlify(url)
    parent_div = html.find('div', {'class': 'results-list'})
    courses_lectures = parent_div.findAll('li')

    course_items = [{
        'label': item.h4.a.string,
        'path': plugin.url_for('show_lectures', url=full_url(item.h4.a['href'])),
        'thumbnail': full_url(item.find('img', {'width': '144'})['src']),
    } for item in courses_lectures if '/courses/' in item.h4.a['href']]

    lecture_items = [{
        'label': '%s: %s' % (plugin.get_string(30206), item.h4.a.string),
        'path': plugin.url_for('watch_lecture', url=full_url(item.h4.a['href'])),
        'thumbnail': full_url(item.find('img', {'class': 'thumb-144'})['src']),
        'is_playable': True,
    } for item in courses_lectures if '/lectures/' in item.h4.a['href']]

    return course_items + lecture_items


@plugin.cached_route('/topics/<url>/')
def show_topics(url):
    '''Displays topics available for a given subject. If there is only
    one topic available, the user will be redirected to the topics view
    instead.
    '''
    html = htmlify(url)
    topics = html.findAll('a', {'class': 'tab-details-link '})

    items = [{
        'label': topic.string,
        'path': plugin.url_for('show_courses', url=full_url(topic['href'])),
    } for topic in topics]

    # Filter out non free topics
    items = filter_free(items)

    # If we only have one item, just redirect to the show_topics page,
    # there's no need to display a single item in the list
    if len(items) == 1:
        return plugin.redirect(items[0]['path'])
    return items


@plugin.route('/courses/<url>/')
@plugin.route('/courses/<url>/<page>/', name='show_courses_page')
def show_courses(url, page='1'):
    '''Displays courses for a given topic. Uses pagination.'''
    def get_pagination(html):
        items = []
        if int(page) > 1:
            items.append({
                'label': '< Previous',
                'path': plugin.url_for('show_courses_page', url=url,
                                       page=str(int(page)-1)),
            })

        next = html.find('span', {'class': 'tab-nav-arrow tab-nav-arrow-r'})
        if next:
            items.append({
                'label': 'Next >',
                'path': plugin.url_for('show_courses_page', url=url,
                                       page=str(int(page)+1)),
            })
        return items

    @plugin.cache()
    def get_course_items(url, page):
        html = htmlify('%s/page:%s' % (url, page))
        courses_lectures = html.findAll('div', {'class': 'thumb'})

        course_items = [{
            'label': item.parent.find('a', {'class': 'editors-picks-title'}).string,
            'path': plugin.url_for('show_lectures', url=full_url(item.a['href'])),
            'thumbnail': full_url(item.find('img', {'class': 'thumb-144'})['src']),
        } for item in courses_lectures if is_course(item.a['href'])]

        lecture_items = [{
            'label': '%s: %s' % (plugin.get_string(30206),
                item.parent.find('a', {'class': 'editors-picks-title'}).string),
            'path': plugin.url_for('watch_lecture', url=full_url(item.a['href'])),
            'thumbnail': full_url(item.find('img', {'class': 'thumb-144'})['src']),
            'is_playable': True,
        } for item in courses_lectures if is_lecture(item.a['href'])]

        pagination_items = get_pagination(html)
        return pagination_items + course_items + lecture_items
    return plugin.finish(get_course_items(url, page), update_listing=page!='1')


#cache = plugin.get_cache('function_cache')
#cache.clear()
#cache.sync()

@plugin.cached_route('/lectures/<url>/')
def show_lectures(url):
    def get_plot(item):
        if item.p:
            return item.p.string
        return ''

    def get_add_to_favorites_url(item):
        path = item.find('a', {'class': 'add'})
        if path:
            return (plugin.get_string(30300), # Add to favorites
                    'XBMC.RunPlugin(%s)' % favorites.url_for(
                        'favorites.add_lecture',
                        url=full_url(path)['href']
            ))
        return

    html = htmlify(url)
    parent_div = html.find('div', {'class': 'results-list'})
    lectures = parent_div.findAll('li')

    items = [{
        'label': item.h4.a.string,
        'path': plugin.url_for('watch_lecture', url=full_url(item.h4.a['href'])),
        'thumbnail': full_url(item.find('img', {'class': 'thumb-144'})['src']),
        'is_playable': True,
        # Call to get_plot is because we are using this view to parse a course page
        # and also parse a playlist page. The playlist pages don't contain a lecture
        # description.
        #'info': {'plot': get_plot(item)},
        'context_menu': [
            (plugin.get_string(30300), # Add to favorites
             'XBMC.RunPlugin(%s)' % favorites.url_for(
                'favorites.add_lecture',
                url=full_url(item.find('a', {'class': 'add'})['href'])
            )),
        ],

    } for item in lectures]
    return items


@plugin.route('/watch/<url>/')
def watch_lecture(url):
    src = download_page(url)

    # First attempt to look for easy flv urls
    pattern = re.compile(r'flashVars.flvURL = "(.+?)"')
    m = pattern.search(src)
    if m:
        resolved_url = m.group(1)
    else:
        resolved_url = resolve(src)
    if resolved_url:
        return plugin.set_resolved_url(resolved_url)

    xbmcgui.Dialog().ok(plugin.get_string(30000), plugin.get_string(30400))
    raise Exception, 'No video url found. Please alert plugin author.'


if __name__ == '__main__':
    plugin.run()
