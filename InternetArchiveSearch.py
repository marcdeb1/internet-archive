import requests
from settings import *
from urllib.parse import urlencode, quote_plus
import os
import string
import json
import random
from Database import *


class InternetArchiveSearch:
    headers = {'Accept': 'application/json', 'Accept-Encoding': 'gzip'}
    base_url = "https://archive.org/advancedsearch.php?"
    output_format = "json"
    fields = ["avg_rating", "backup_location", "btih", "call_number", "collection", "contributor", "coverage", "creator", "date", "description", "downloads", "external-identifier", "foldoutcount", "format", "headerImage", "identifier", "imagecount", "language", "licenseurl", "mediatype", "members", "month", "num_reviews", "oai_updatedate", "publicdate", "publisher", "related-external-id", "reviewdate", "rights", "scanningcentre", "source", "stripped_tags", "subject", "title", "type", "volume", "week", "year"]
    number_results = 100
    start = 0
    file_type = None
    db = None

    def __init__(self, query, file_type):
        self.query = query
        self.file_type = file_type
        self.db = Database(name=COLLECTION_NAME + '.db')

    def build_query(self):
        params = dict()
        params['q'] = self.query
        params['fl[]'] = ','.join(self.fields)
        params['output'] = self.output_format
        params['rows'] = str(self.number_results)
        params['page'] = str(self.start)
        query_string = self.base_url + urlencode(params)
        return query_string

    def get_identifiers(self):
        num_found = self.get_num_found()
        self.number_results = num_found
        self.fields = ['identifier']
        documents = self.search()
        return documents

    def get_num_found(self):
        query = self.build_query()
        response = requests.get(query, headers=self.headers)
        if response.status_code != 200:
            print("Wrong status code")
        response_json = response.json()
        if 'response' not in response_json:
            print("Response error")
        num_found = response_json['response']['numFound']
        print(str(num_found) + " results found")
        return num_found

    def search(self):
        query = self.build_query()
        response = requests.get(query, headers=self.headers)
        if response.status_code != 200:
            print("Wrong status code")
        response_json = response.json()
        if 'response' not in response_json:
            print("Response error")
        documents = response_json['response']['docs']
        return documents

    def get_metadata(self, identifier):
        url = 'https://archive.org/metadata/' + quote_plus(identifier)
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            print("Wrong status code")
        response_json = response.json()
        return response_json

    def get_and_download_content(self, identifier):
        document = self.get_metadata(identifier)
        print("Downloading " + str(identifier) + "...")
        source_filename, thumbnail_filename = self.download_contents(document)
        print("Downloaded !")
        content = dict()
        content['source_filename'] = source_filename
        content['thumbnail_filename'] = thumbnail_filename
        if 'metadata' not in document:
            print("Error - No metadata")
            return False
        content['metadata'] = json.dumps(document['metadata'])
        content['name'] = self.get_name()
        content['downloaded'] = True
        content['published'] = False
        content['identifier'] = identifier
        self.db.store_item(content)
        return content

    @staticmethod
    def get_server_url(document):
        root = "http://" + document['d1']
        dir = document['dir'] + '/'
        return root + dir

    def get_source_file(self, document):
        file_name = ""
        allowed_formats = self.get_allowed_formats()
        for file in document['files']:
            if file['source'] == 'original' and file['format'] in allowed_formats:
                file_name = file['name']
                break
        return file_name

    @staticmethod
    def get_thumbnail_file(document):
        thumbnails = list()
        index = 0 # To avoid downloading first thumbnail
        if not 'files' in document:
            return False

        for file in document['files']:
            if file['format'] == 'Thumbnail':
                index += 1
                if index > 0:
                    return file['name']
                else:
                    thumbnails.append(file['name'])
        if not thumbnails:
            return False
        return thumbnails[0]

    def download_contents(self, document):
        server_url = self.get_server_url(document)
        # Download source
        source_filename = quote_plus(self.get_source_file(document))
        source_url = server_url + source_filename
        self.download_source(source_url, source_filename)
        # Download thumbnail
        thumbnail_filename = ""
        if DOWNLOAD_THUMBNAILS:
            thumbnail_filename = quote_plus(self.get_thumbnail_file(document))
            if thumbnail_filename:
                thumbnail_url = server_url + thumbnail_filename
                self.download_thumbnail(thumbnail_url, thumbnail_filename)
        return source_filename, thumbnail_filename

    def download_source(self, url, filename):
        directory = MEDIA_DIR
        return self.download_file(url, filename, directory)

    def download_thumbnail(self, url, filename):
        directory = THUMBNAIL_DIR
        return self.download_file(url, filename, directory)

    def download_file(self, url, filename, directory):
        path = directory + filename
        r = requests.get(url, stream=True, headers=self.headers)
        if r.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in r.iter_content(4096):
                    f.write(chunk)
        else:
            print("Request failed")
        return filename

    def get_name(self):
        name = str()
        if PREFIX:
            name += PREFIX + '-'
        name += self.random_string(NAME_SIZE)
        return name

    def get_allowed_formats(self):
        if self.file_type == 'VIDEO':
            return ALLOWED_VIDEO_FORMATS
        elif self.file_type == 'IMAGE':
            return ALLOWED_IMAGE_FORMATS
        else:
            return False

    def set_query(self, query):
        self.query = query
        return True

    @staticmethod
    def random_string(size):
        alphabet = string.ascii_lowercase + string.digits
        return ''.join(random.choice(alphabet) for _ in range(size))
