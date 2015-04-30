#!/usr/bin/env python3

# Standard library
import os
import sys
import threading
import unittest

# Third-party libraries
import bs4
import requests

# Code under test -- first, add project to path:
path_to_this_file     = os.path.realpath(__file__)
path_to_this_folder   = os.path.dirname(path_to_this_file)
path_to_parent_folder = os.path.dirname(path_to_this_folder)
sys.path.append(path_to_parent_folder)

import wikisum

server_base = 'http://localhost:5000'

def fetch(pageid):
    """Submit an HTTP GET request for the identified page, and return a
    response object having `status_code` and `text` properties.
    """
    return requests.get("{}/page/{}".format(server_base, pageid))

def start_server():
    thread = threading.Thread(target=wikisum.main, args=[True])
    thread.start()
    return thread

def stop_server(thread):
    requests.get("{}/quit".format(server_base))
    thread.join()

class WikisumKrakowTest(unittest.TestCase):
    """Tests response against known data for the Kraków page."""

    def setUp(self):
        self.server_thread = start_server()
        self.response = fetch(16815)    # 16815 is the Kraków page ID.

    def tearDown(self):
        stop_server(self.server_thread)

    def test_status(self):
        self.assertEqual(200, self.response.status_code)

    def test_data(self):
        # NB: We ignore fields that are not mocked by wikisum's test mode.
        soup = bs4.BeautifulSoup(self.response.text)
        keys = [th.text for th in soup.find_all('th')]
        data = [td.text for td in soup.find_all('td')]
        rows = dict(zip(keys, data))
        expected = {
            'Title'       : 'Kraków',
            'URL'         : 'http://en.wikipedia.org/wiki/Krak%C3%B3w',
            'Page ID'     : '16815',
            'Parent ID'   : '657359058',
            'Revision ID' : '658830708'
        }
        for k, v in expected.items():
            self.assertEqual(rows[k], v)

class WikisumNonesuchTest(unittest.TestCase):
    """Tests response when a non-existent page is requested."""

    def setUp(self):
        self.server_thread = start_server()
        self.response = fetch(0)        # No page has ID 0.

    def tearDown(self):
        stop_server(self.server_thread)

    def test_status(self):
        self.assertEqual(404, self.response.status_code)

    def test_content(self):
        self.assertIn("Not Found", self.response.text)

if __name__ == '__main__':
    unittest.main()
