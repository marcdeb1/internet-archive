import requests
import json
import os
import string
import random
import lbry
from slugify import slugify
from settings import *
from Database import *


class LBRYUpload:
    headers = {'Accept': 'application/json', 'Accept-Encoding': 'gzip'}

    def __init__(self):
        self.db = Database(name=COLLECTION_NAME + '.db')

    def build_data(self, content):
        params = dict()
        params['name'] = content['name']
        params['file_path'] = os.path.abspath(MEDIA_DIR + content['source_filename'])
        params['bid'] = BID
        if CHANNEL_NAME:
            params['channel_name'] = CHANNEL_NAME

        settings = {'title': 'title', 'description': 'description', 'author': 'creator', 'license': 'licenseurl'}
        metadata = self.add_params(settings, json.loads(content['metadata']))
        metadata['nsfw'] = False
        metadata['language'] = 'en'
        thumbnail_path = content['thumbnail_filename']
        if thumbnail_path:
            metadata['thumbnail'] = os.path.abspath(THUMBNAIL_DIR + thumbnail_path)
        params['metadata'] = metadata
        return params

    def publish(self, content):
        data = self.build_data(content)
        print("Publishing " + str(data['name']) + "...")
        r = lbry.publish(name=data["name"], bid=data["bid"], file_path=data["file_path"],
                         channel_name=data["channel_name"], metadata=data["metadata"], headers=self.headers)
        print("Transaction : " + str(r) + '\n')
        self.db.update_published(content['identifier'])
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
