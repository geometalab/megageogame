# -*- coding:utf-8 -*-
'''
Created on 03.04.2014

@author: Ausleihe
'''
from urllib2 import build_opener
import json


class ArcgisScraper(object):
    '''
    This class scrapes pages and returns
    their content in json-form, here used to
    scrape the arcgis-feature-servers, but actually
    can be used for any pages with json-content
    '''
    def __init__(self):
        self.opener = build_opener()
        self.opener.addheaders = [(
            'User-agent',
            (
                'Mozilla/5.0 (Windows NT 6.1;'
                'WOW64; rv:27.0) Gecko/20100101 Firefox/27.0'
            ))]

    def get_json(self, url):
        '''
        Returns the content of page 'url'
        in json-format
        '''
        response = self.opener.open(url)
        page = json.load(response)
        return page
