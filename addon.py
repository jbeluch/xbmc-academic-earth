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
from operator import itemgetter
from xbmcswift2 import Plugin
from resources.lib.academicearth import api

PLUGIN_NAME = 'Academic Earth'
PLUGIN_ID = 'plugin.video.academicearth'
plugin = Plugin(PLUGIN_NAME, PLUGIN_ID, __file__)
AE = api.AcademicEarth()


@plugin.route('/')
def show_index():
    items = [
        {'label': plugin.get_string(30200),
         'path': plugin.url_for('show_subjects')},

        {'label': plugin.get_string(30201),
         'path': plugin.url_for('show_universities')},

        {'label': plugin.get_string(30202),
         'path': plugin.url_for('show_speakers')},
    ]
    return items


@plugin.route('/universities/', 'show_universities', {'fetch_func': AE.get_universities, 'next_view': 'show_university_info'})
@plugin.route('/subjects/', 'show_subjects', {'fetch_func': AE.get_subjects, 'next_view': 'show_subject_info'})
@plugin.route('/speakers/', 'show_speakers', {'fetch_func': AE.get_speakers, 'next_view': 'show_speaker_info'})
def show_topnav_items(fetch_func, next_view):
    items = []
    for obj in fetch_func():
        item = {
            'label': obj.name,
            'path': plugin.url_for(next_view, url=obj.url),
        }
        if hasattr(obj, 'icon'):
            item['icon'] = obj.icon
        items.append(item)

    sorted_items = sorted(items, key=lambda item: item['label'])
    return sorted_items


@plugin.route('/subjects/<url>/', 'show_subject_info', {'cls': api.Subject})
@plugin.route('/universities/<url>/', 'show_university_info', {'cls': api.University})
@plugin.route('/speakers/<url>/', 'show_speaker_info', {'cls': api.Speaker})
def show_info(url, cls):
    uni = cls.from_url(url)

    courses = [{
        'label': course.name,
        'path': plugin.url_for('show_course_info', url=course.url),
    } for course in uni.courses]

    lectures = [{
        'label': 'Lecture: %s' % lecture.name,
        'path': plugin.url_for('play_lecture', url=lecture.url),
        'is_playable': True,
    } for lecture in uni.lectures]

    by_label = itemgetter('label')
    items = sorted(courses, key=by_label) + sorted(lectures, key=by_label)
    return items


@plugin.route('/courses/<url>/')
def show_course_info(url):
    course = api.Course.from_url(url)
    lectures = [{
        'label': 'Lecture: %s' % lecture.name,
        'path': plugin.url_for('play_lecture', url=lecture.url),
        'is_playable': True,
    } for lecture in course.lectures]

    return sorted(lectures, key=itemgetter('label'))


@plugin.route('/lectures/<url>/')
def play_lecture(url):
    lecture = api.Lecture.from_url(url)
    url = 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % lecture.youtube_id
    plugin.log.info('Playing url: %s' % url)
    plugin.set_resolved_url(url)


if __name__ == '__main__':
    plugin.run()
