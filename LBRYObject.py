import requests
import json
import os


class LBRYObject:
    path = None
    document = None
    bid = 0.0001
    daemon_url = 'http://localhost:5279/lbryapi/'
    media_dir = 'media/'
    channel_name = '@internet-archive-movies'

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
        params['bid'] = self.bid
        params['file_path'] = os.path.abspath(self.media_dir + self.path)

        if self.channel_name:
            params['channel_name'] = self.channel_name

        data['params'] = params
        return json.dumps(data)

    def publish(self):
        data = self.build_data()
        print(data)
        r = requests.get(self.daemon_url, data=data)
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
