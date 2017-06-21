import requests
import json
import os
from slugify import slugify
from settings import *


class LBRYObject:
    path = None
    document = None

    def __init__(self, path, document):
        self.path = path
        self.document = document

    def build_data(self):
        data = dict()
        data['method'] = 'publish'
        document_metadata = self.document['metadata']
        params = dict()
        params['name'] = slugify(document_metadata['identifier'])
        params['file_path'] = os.path.abspath(MEDIA_DIR + self.path)
        params['bid'] = BID
        metadata = dict()
        settings = {'title': 'title', 'description': 'description', 'author': 'creator'}
        metadata = self.add_params(settings, document_metadata)
        metadata['nsfw'] = False
        metadata['license'] = 'LBRY Inc'
        metadata['language'] = 'en'

        if CHANNEL_NAME:
            params['channel_name'] = CHANNEL_NAME

        params['metadata'] = metadata
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
