import os
import sys
from xbmcswift2.cli import testing
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

    
'''
 # test gen stuff for nose


    def check_view(self, item):
        TestAljazeeraViews.check_view.description = ("test_view(<%s '%s'>)" % (item.get_label(), item.get_path())).encode('utf-8')
        response = addon.plugin.test(Modes.ONCE, [])
        self.assert_listitems_response(item, response)
        self.to_visit.extend(i for i in response if i not in self.visited and i not in self.to_visit and not i.get_played())

    def test_view_generator(self):
        while self.to_visit:
            item = self.to_visit.pop(0)
            #self.check_view.description = ("test_view(<%s '%s'>)" % (item.get_label(), item.get_path())).encode('utf-8')
            #setattr(self.check_view, 'description', 'poop')
            #yield self.check_view, self.to_visit.pop(0)
            yield TestAljazeeraViews.check_view, self, item

'''
