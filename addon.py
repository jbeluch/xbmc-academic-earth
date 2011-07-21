#!/usr/bin/env python
from xbmcswift import Plugin, download_page
from BeautifulSoup import BeautifulSoup as BS, SoupStrainer as SS
from urlparse import urljoin
import re

__plugin_name__ = 'New Academic Earth'
__plugin_id__ = 'plugin.video.newacademicearth'

plugin = Plugin(__plugin_name__, __plugin_id__)

#### Plugin Views ####

# Default View
@plugin.route('/')
def show_categories():
    items = [
        {'label': 'Show Topics', 'url': plugin.url_for('show_topics')},
    ]
    return plugin.add_items(items)

@plugin.route('/topics/')
def show_topics():
    pass


if __name__ == '__main__': 
    plugin.run()





