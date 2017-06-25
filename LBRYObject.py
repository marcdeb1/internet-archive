import requests
import json
import os
import string
import random
import lbry
from slugify import slugify
from settings import *


class LBRYObject:
    headers = {'Accept': 'application/json', 'Accept-Encoding': 'gzip'}
    source_path = None
    thumbnail_path = None
    metadata = None

    def __init__(self, content):
        self.source_path = content['source_filename']
        self.thumbnail_path = content['thumbnail_filename']
        self.metadata = content['metadata']

    def build_data(self):
        params = dict()
        params['name'] = self.get_name()
        params['file_path'] = os.path.abspath(MEDIA_DIR + self.source_path)
        params['bid'] = BID
        if CHANNEL_NAME:
            params['channel_name'] = CHANNEL_NAME

        settings = {'title': 'title', 'description': 'description', 'author': 'creator', 'license': 'licenseurl'}
        metadata = self.add_params(settings, self.metadata)
        metadata['nsfw'] = False
        metadata['language'] = 'en'
        if self.thumbnail_path:
            metadata['thumbnail'] = os.path.abspath(THUMBNAIL_DIR + self.thumbnail_path)
        params['metadata'] = metadata
        return params

    def get_name(self):
        name = str()
        if PREFIX:
            name += PREFIX + '-'
        name += self.random_string(NAME_SIZE)
        return name

    def publish(self):
        data = self.build_data()
        r = lbry.publish(name=data["name"], bid=data["bid"], file_path=data["file_path"],
                         channel_name=data["channel_name"], metadata=data["metadata"], headers=self.headers)
        return r

    @staticmethod
    def add_params(settings, metadata):
        params = dict()
        for key, value in settings.items():
            if value not in metadata:
                continue
            else:
                attribute = metadata[value]
                if isinstance(attribute, list):
                    params[key] = ', '.join(attribute)
                else:
                    params[key] = attribute
        return params

    @staticmethod
    def random_string(size):
        alphabet = string.ascii_lowercase + string.digits
        return ''.join(random.choice(alphabet) for _ in range(size))
