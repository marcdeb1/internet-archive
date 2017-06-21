import requests
import json
import os
from .settings import *


class LBRYObject:
    path = None
    document = None

    def __init__(self, path, document):
        self.path = path
        self.document = document

    def build_data(self):
        data = dict()
        data['method'] = 'publish'
        metadata = self.document['metadata']
        settings = {'name': 'identifier', 'title': 'title', 'description': 'description', 'author': 'creator', 'language': 'language'}
        params = self.add_params(settings, metadata)
        params['nsfw'] = False
        params['license'] = 'LBRY Inc.'
        params['bid'] = BID
        params['file_path'] = os.path.abspath(MEDIA_DIR + self.path)

        if CHANNEL_NAME:
            params['channel_name'] = CHANNEL_NAME

        data['params'] = params
        return json.dumps(data)

    def publish(self):
        data = self.build_data()
        print(data)
        r = requests.get(DAEMON_URL, data=data)
        if r.status_code != 200:
            print(r.content)
            return False
        else:
            return r.content

    @staticmethod
    def add_params(settings, metadata):
        params = dict()
        for key, value in settings.items():
            if value not in metadata:
                continue
            else:
                params[key] = metadata[value]
        return params
