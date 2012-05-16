import os
import sys
from xbmcswift2.cli import testing
from xbmcswift2.cli.testing import (assert_is_playable, assert_listitems_response,
    assert_listitem, assert_media_played)

# Update sys.path in order to import our plugin
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from addon import plugin


items = []
paths_to_visit = set()
paths_visited = set()

def setup():
    plugin.set_setting('username', 'jbeluch')
    # NOCOMMIT
    plugin.set_setting('password', 'blue66')
    _items = testing.test_plugin(plugin)
    add_items(_items)

def add_items(_items):
    #global items
    for item in _items:
        path = item.get_path()
        if path not in paths_visited and path not in paths_to_visit:
            paths_to_visit.add(path)
            items.append(item)

def validate_view(item):
    _items = testing.test_plugin(plugin, item.get_path())
    assert_listitems_response(_items)
    add_items(_items)

def test_crawled_views():
    while items:
        item = items.pop(0)
        validate_view.description = ("test_view(<%s '%s'>)" %
            (item.get_label(), item.get_path())).encode('utf-8')
        yield validate_view, item

test_crawled_views.setup = setup
