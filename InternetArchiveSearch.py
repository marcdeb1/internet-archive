import requests
from settings import *
from urllib.parse import urlencode, quote_plus
import os
import shutil


class InternetArchiveSearch:
    headers = "Accept: application/json"
    base_url = "https://archive.org/advancedsearch.php?"
    output_format = "json"
    fields = ["avg_rating", "backup_location", "btih", "call_number", "collection", "contributor", "coverage", "creator", "date", "description", "downloads", "external-identifier", "foldoutcount", "format", "headerImage", "identifier", "imagecount", "language", "licenseurl", "mediatype", "members", "month", "num_reviews", "oai_updatedate", "publicdate", "publisher", "related-external-id", "reviewdate", "rights", "scanningcentre", "source", "stripped_tags", "subject", "title", "type", "volume", "week", "year"]
    number_results = 100
    start = 0

    def __init__(self, query):
        self.query = query

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
        response = requests.get(query)
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
        response = requests.get(query)
        if response.status_code != 200:
            print("Wrong status code")
        response_json = response.json()
        if 'response' not in response_json:
            print("Response error")
        documents = response_json['response']['docs']
        return documents

    def iter_search(self):
        query = self.build_query()
        response = requests.get(query, stream=True)
        if response.status_code != 200:
            print("Wrong status code")
        response_json = response.json()
        if 'response' not in response_json:
            print("Response error")
        documents = response_json['response']['docs']
        return documents

    def get_metadata(self, identifier):
        url = 'https://archive.org/metadata/' + quote_plus(identifier)
        response = requests.get(url)
        if response.status_code != 200:
            print("Wrong status code")
        response_json = response.json()
        return response_json

    def get_file_url(self, document):
        root = "http://" + document['d1']
        dir = document['dir'] + '/'
        file_name = ""
        for file in document['files']:
            if file['source'] == 'original' and file['format'] in ALLOWED_FORMATS:
                file_name = file['name']
                break
        return root + dir + quote_plus(file_name)

    def download_file(self, url):
        local_filename = url.split('/')[-1]
        path = MEDIA_DIR + local_filename
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
        else:
            print("Request failed")
        return local_filename

    def delete_file(self, filename):
        path = MEDIA_DIR + filename
        os.remove(path)
        return filename

    def set_query(self, query):
        self.query = query
        return True
