#!/usr/bin/env python
from xbmcswift import Plugin, download_page
from BeautifulSoup import BeautifulSoup as BS, SoupStrainer as SS
from urlparse import urljoin
from resources.lib.getflashvideo import YouTube
import re

__plugin_name__ = 'New Academic Earth'
__plugin_id__ = 'plugin.video.newacademicearth'

plugin = Plugin(__plugin_name__, __plugin_id__)

BASE_URL = 'http://academicearth.org'
def full_url(path):
    return urljoin(BASE_URL, path)

def htmlify(url):
    return BS(download_page(url))

def filter_free(items):
    return filter(lambda item: not item['label'].startswith('Online'), items)

@plugin.route('/')
def show_index():
    items = [
        {'label': 'Subjects', 'url': plugin.url_for('show_subjects')},
        {'label': 'Universities', 'url': plugin.url_for('show_universities')},
        {'label': 'Instructors', 'url': plugin.url_for('show_instructors')},
    ]
    return plugin.add_items(items)

@plugin.route('/subjects/', url=full_url('subjects'))
def show_subjects(url):
    html = htmlify(url)
    parent_div = html.find('div', {'class': 'institution-list'}).parent
    subjects = parent_div.findAll('li')

    items = [{
        'label': subject.a.string,
        'url': plugin.url_for('show_topics', url=full_url(subject.a['href'])),
    } for subject in subjects]

    # Filter out non-free subjects
    items = filter(lambda item: not item['label'].startswith('Online'), items)

    return plugin.add_items(items)

@plugin.route('/universities/', url=full_url('universities'))
def show_universities(url):
    html = htmlify(url)
    parent_div = html.find('div', {'class': 'institution-list'})
    universities = parent_div.findAll('a')

    items = [{
        'label': item.string,
        'url': plugin.url_for('show_topics', url=full_url(item['href'])),
    } for item in universities]

    return plugin.add_items(items)

@plugin.route('/instructors/', url=full_url('speakers'))
def show_instructors(url):
    html = htmlify(url)
    uls = html.findAll('ul', {'class': 'professors-list'})
    professors = uls[0].findAll('li') + uls[1].findAll('li')

    items = [{
        'label': item.a.string,
        'url': plugin.url_for('show_instructor_courses', url=full_url(item.a['href'])),
    } for item in professors]

    return plugin.add_items(items)

@plugin.route('/instructors/<url>/')
def show_instructor_courses(url):
    html = htmlify(url)
    parent_div = html.find('div', {'class': 'results-list'})
    courses_lectures = parent_div.findAll('li')

    courses = filter(lambda item: '/courses/' in item.h4.a['href'], courses_lectures)
    lectures = filter(lambda item: '/lectures/' in item.h4.a['href'], courses_lectures)

    course_items = [{
        'label': item.h4.a.string,
        'url': plugin.url_for('show_lectures', url=full_url(item.h4.a['href'])),
        'thumbnail': full_url(item.find('img', {'width': '144'})['src']),
    } for item in courses]

    lecture_items = [{
        'label': 'Lecture: %s' % item.h4.a.string,
        'url': plugin.url_for('watch_lecture', url=full_url(item.h4.a['href'])),
        'thumbnail': full_url(item.find('img', {'class': 'thumb-144'})['src']),
        'is_folder': False,
        'is_playable': True,
    } for item in lectures]

    return plugin.add_items(course_items + lecture_items)

@plugin.route('/topics/<url>/')
def show_topics(url):
    # Filter our topcis taht start with 'Online'
    # if we only have one topic, redirect to teh courses/lectures page
    html = htmlify(url)
    parent_div = html.find('div', {'class': 'results-side'})
    topics = parent_div.findAll('li')

    items = [{
        'label': topic.a.string,
        'url': plugin.url_for('show_courses', url=full_url(topic.a['href'])),
    } for topic in topics]

    # Filter out non free topics
    items = filter_free(items)

    # If we only have one item, just redirect to the show_topics page, 
    # there's no need to display a single item in the list
    if len(items) == 1:
        return plugin.redirect(items[0]['url'])

    return plugin.add_items(items)

@plugin.route('/courses/<url>/')
def show_courses(url):
    def get_pagination(html):
        items = []
        pagination = html.find('ul', {'class': 'pagination'})
        if not pagination:
            return items

        previous = pagination.find(text='&lt;')
        if previous:
            items.append({
                'label': '< Previous',
                'url': plugin.url_for('show_courses', url=full_url(previous.parent['href'])),
            })

        next = pagination.find(text='&gt;')
        if next:
            items.append({
                'label': 'Next >',
                'url': plugin.url_for('show_courses', url=full_url(next.parent['href'])),
            })
        return items

    html = htmlify(url)
    parent_div = html.find('div', {'class': 'video-results'})

    # Need to filter out <li>'s that are only used for spacing.
    # Spacing li's look like <li class="break">
    courses_lectures = parent_div.findAll('li', {'class': lambda c: c != 'break'})

    # Some of the results can be a standalone lecture, not a link to a course
    # page. We need to display these separately.
    courses = filter(lambda item: '/courses/' in item.h3.a['href'], courses_lectures)
    lectures = filter(lambda item: '/lectures/' in item.h3.a['href'], courses_lectures)

    course_items = [{
        'label': item.h3.a.string,
        'url': plugin.url_for('show_lectures', url=full_url(item.h3.a['href'])),
        'thumbnail': full_url(item.find('img', {'class': 'thumb-144'})['src']),
    } for item in courses]

    lecture_items = [{
        'label': 'Lecture: %s' % item.h3.a.string,
        'url': plugin.url_for('watch_lecture', url=full_url(item.h3.a['href'])),
        'thumbnail': full_url(item.find('img', {'class': 'thumb-144'})['src']),
        'is_folder': False,
        'is_playable': True,
    } for item in lectures]

    pagination_items = get_pagination(html)

    return plugin.add_items(pagination_items + course_items + lecture_items)

@plugin.route('/lectures/<url>/')
def show_lectures(url):
    html = htmlify(url)
    parent_div = html.find('div', {'class': 'results-list'})
    lectures = parent_div.findAll('li')

    items = [{
        'label': item.h4.a.string,
        'url': plugin.url_for('watch_lecture', url=full_url(item.h4.a['href'])),
        'thumbnail': full_url(item.find('img', {'class': 'thumb-144'})['src']),
        'is_folder': False,
        'is_playable': True,
        'info': {'plot': item.p.string},
    } for item in lectures]

    return plugin.add_items(items)

@plugin.route('/watch/<url>/')
def watch_lecture(url):
    src = download_page(url)
    # There are 2 different hosts for lectures.
    # blip.tv and youtube.

    # Attempt to match blip.tv
    flv_ptn = re.compile(r'flashVars.flvURL = "(.+?)"')
    m = flv_ptn.search(src)
    if m:
        return plugin.set_resolved_url(m.group(1))

    # If we're still here attempt to match youtube
    #videoid_ptn = 
    ytid_ptn = re.compile(r'flashVars.ytID = "(.+?)"')
    m = ytid_ptn.search(src)
    if m:
        video_url = YouTube.get_flashvideo_url(videoid=m.group(1))
        return plugin.set_resolved_url(video_url)

    raise Exception, 'No video url found. Please alert plugin author.'


if __name__ == '__main__': 
    plugin.run()





