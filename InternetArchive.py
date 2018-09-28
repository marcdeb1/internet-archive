import logging
import configparser as cp
import string
import json
import os
import random
from internetarchive import search_items, get_item, download
import time
from lbry_uploader import Uploader

class InternetArchive:
    def __init__(self, collection_name, config_name="default"):
        self.logger = self.getLogger()
        # Settings
        self.config = cp.ConfigParser()
        settings_file = 'config/' + config_name + '.ini'
        self.config.read(settings_file)
        if 'MainConfig' in self.config:
            self.settings = self.config['MainConfig']
            self.logger.info("Using '" + config_name + "' settings.")
        else:
            self.logger.error("Could not find settings file or MainConfig section.")
        self.collection_name = collection_name
        self.metadata = []
        self.items = []

    def upload_collection(self):
        self.items = self.get_items()
        self.metadata = self.get_metadata()
        r = self.download_items()
        self.save_metadata()
        self.upload()
    
    def get_items(self):
        self.logger.info("Searching the Internet Archive...")
        search = search_items(query='collection:' + self.collection_name, fields=["identifier"])
        num_found = search.num_found
        self.logger.info(str(num_found) + " items found in collection '" + str(self.collection_name) + "'.")
        items = []
        for s in search:
            identifier = s.get("identifier")
            item = get_item(identifier)
            items.append(item)
        return items
        
    def get_metadata(self):
        metadata = []
        for item in self.items:
            m = {}
            m["name"] = self.get_name()
            m["title"] = item.metadata.get("title")
            m["description"] = item.metadata.get("description")
            m["author"] = item.metadata.get("author")
            m["language"] = item.metadata.get("language")
            m["license_url"] = item.metadata.get("licenseurl")
            m["license"] = item.metadata.get("rights")
            m["metadata"] = item.metadata
            m["identifier"] = item.metadata.get("identifier")
            file_name = self.get_source_file(item)
            if not file_name:
                self.logger.warning("Could not find file for item '" + str(m.get('identifier')) + "'. Skipping item.")
                continue
            m["file_name"] = file_name
            file_path = self.get_file_directory() + "/" + file_name
            m["file_path"] = file_path.replace("/", "\\")
            m["thumbnail"] = self.get_thumbnail_path(item)
            m["preview"] = m["thumbnail"]
            metadata.append(m)
        return metadata

    def download_items(self):
        self.logger.info("Starting download...")
        dest_dir = self.get_file_directory()
        number_items = len(self.metadata)
        for i,m in enumerate(self.metadata):
            d = download(m.get('identifier'), files=[m.get('file_name')], destdir=dest_dir, silent=True, no_directory=True, retries=3)
            self.printProgressBar(i + 1, number_items)
        return True

    def save_metadata(self):
        dir = self.get_file_directory() + "/"
        json_name = self.collection_name + '.json'
        with open(dir + json_name, 'w') as f:
            json.dump(self.metadata, f, ensure_ascii=False)
        self.logger.info("Saved metadata for collection '" + str(self.collection_name) + "'.") 
        return True
    
    def upload(self):
        input = self.get_file_directory() + "/" + self.collection_name + '.json'
        uploader = Uploader()
        r = uploader.upload(input)
        return r
    
    def get_source_file(self, item):
        file_name = ""
        allowed_formats = self.get_allowed_formats(item)
        for file in item.files:
            if file['source'] == 'original' and file['format'] in allowed_formats:
                file_name = file.get("name")
                break
        return file_name

    def get_file_directory(self):
        dir = os.getcwd() + "\\" + self.settings["media_dir"] + self.collection_name
        return dir
    
    def get_thumbnail_path(self, item):
        thumbnails = list()
        index = 0 # To avoid downloading first thumbnail
        for file in item.files:
            if 'Thumb' in file.get("format"):
                index += 1
                if index > 0:
                    return file.get("name")
                else:
                    thumbnails.append(file.get("name"))
        if not thumbnails:
            return None
        return thumbnails[0]
        
    def get_name(self):
        name = str()
        if self.settings["prefix"]:
            name += self.settings["prefix"] + '-'
        name += self.random_string(self.settings["name_size"])
        return name

    def get_allowed_formats(self, item):
        if item.metadata["mediatype"] == 'movies':
            return self.settings["allowed_video_formats"]
        elif item.metadata["mediatype"] == 'image':
            return self.settings["allowed_image_formats"]
        else:
            return False
       
    def getLogger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        log_name = time.strftime("%Y%m%d-%H%M%S")
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
        
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(formatter)
        logger.addHandler(consoleHandler)
        
        fileHandler = logging.FileHandler("{0}/{1}.log".format("log", log_name))
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)
        return logger

    @staticmethod
    def random_string(size):
        alphabet = string.ascii_lowercase + string.digits
        return ''.join(random.choice(alphabet) for _ in range(int(size)))
        
    @staticmethod
    def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
        # Print New Line on Complete
        if iteration == total: 
            print()