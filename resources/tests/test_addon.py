import os
import sys
from xbmcswift2.cli import testing
from xbmcswift2.cli.testing import (assert_is_playable, assert_listitems_response,
    assert_listitem, assert_media_played)
from unittest import TestCase

# Update sys.path in order to import our plugin
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from addon import plugin


class TestAddon(testing.XBMCAddonTestCase):

    def setUp(self):
        cache = plugin.get_cache('function_cache')
        cache.clear()
        cache.sync()

    def test_stuff(self):
        items = testing.test_plugin(plugin)
        self.assert_listitems_response(items)

    def test_subjects(self):
        url = 'plugin://plugin.video.academicearth/subjects/'
        items = testing.test_plugin(plugin, url)
        self.assert_listitems_response(items)

    def test_topic(self):
        url = 'plugin://plugin.video.academicearth/topics/http%3A%2F%2Facademicearth.org%2Fsubjects%2FAA/'
        items = testing.test_plugin(plugin, url)
        self.assert_listitems_response(items)

    def test_course(self):
        url = 'plugin://plugin.video.academicearth/lectures/http%3A%2F%2Facademicearth.org%2Fcourses%2Froman-architecture/'
        items = testing.test_plugin(plugin, url)
        self.assert_listitems_response(items)
        for item in items:
            self.assert_is_playable(item)
        
    def test_lecture_video(self):
        url = 'plugin://plugin.video.academicearth/watch/http%3A%2F%2Facademicearth.org%2Flectures%2Fintro-roman-architecture/'
        items = testing.test_plugin(plugin, url)
        self.assert_media_played(items)
        assert items[0].get_path().startswith('plugin://plugin.video.youtube')

    def test_get_favorites(self):
        plugin.set_setting('username', 'jbeluch')
        # NOCOMMIT
        plugin.set_setting('password', 'blue66')
        #raise Exception, 'Must set username/password in code'
        url = 'plugin://plugin.video.academicearth/favorites/'
        items = testing.test_plugin(plugin, url)
        self.assert_listitems_response(items)
        for item in items:
            self.assert_is_playable(item)
