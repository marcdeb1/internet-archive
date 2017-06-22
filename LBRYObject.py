import requests
import json
import os
import string
import random
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
        data = dict()
        data['method'] = 'publish'
        params = dict()
        params['name'] = self.get_name()
        params['file_path'] = os.path.abspath(MEDIA_DIR + self.source_path)
        if self.thumbnail_path:
            params['thumbnail'] = os.path.abspath(THUMBNAIL_DIR + self.thumbnail_path)
        params['bid'] = BID
        params['claim_address'] = self.get_wallet_address()
        if CHANNEL_NAME:
            params['channel_name'] = CHANNEL_NAME

        settings = {'title': 'title', 'description': 'description', 'author': 'creator', 'license': 'licenseurl'}
        metadata = self.add_params(settings, self.metadata)
        metadata['nsfw'] = False
        metadata['language'] = 'en'

        params['metadata'] = metadata
        data['params'] = params
        return json.dumps(data)

    def get_name(self):
        name = str()
        if PREFIX:
            name += PREFIX + '-'
        name += self.random_string(NAME_SIZE)
        return name

    def publish(self):
        data = self.build_data()
        r = requests.get(DAEMON_URL, data=data, headers=self.headers)
        if r.status_code != 200:
            print(r.content)
            return False
        else:
            return r.content

    def get_wallet_address(self):
        data = dict()
        data['method'] = 'wallet_unused_address'
        r = requests.get(DAEMON_URL, data=json.dumps(data), headers=self.headers)
        response_json = r.json()
        if r.status_code == 200:
            if 'result' in response_json:
                return response_json["result"]
        return False

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
