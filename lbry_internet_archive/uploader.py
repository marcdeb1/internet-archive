import logging
import configparser as cp
import string
import json
import os
import random
from internetarchive import search_items, get_item, download
import time
from lbry_uploader import Uploader
from slugify import slugify

class InternetArchive:
    def __init__(self, collection_name, config_name="default"):
        self.logger = self.getLogger()
        # Settings
        self.config = cp.ConfigParser()
        settings_file = 'config/' + config_name + '.ini'
        self.config.read(settings_file)
        if 'MainConfig' in self.config:
            self.settings = self.config['MainConfig']
        else:
            self.logger.error("Could not find settings file or MainConfig section.")
        self.collection_name = collection_name
        self.metadata = []
        self.items = []
        # Uploader
        self.uploader = Uploader()

    def upload_collection(self):
        self.logger.info("Searching the Internet Archive...")
        results = search_items(query='collection:' + self.collection_name, fields=["identifier"])
        number_items = results.num_found
        self.logger.info(str(number_items) + " items found in collection '" + str(self.collection_name) + "'.")
        metadata = []
        self.logger.info("Starting download...")
        for i,s in enumerate(results):
            identifier = s.get("identifier")
            item = get_item(identifier)
            m = self.get_metadata(item)
            if not m:
                continue
            r = self.download_item(m)
            p = self.uploader.upload_claim(m)
        return True
        
    def get_metadata(self, item):
        m = {}
        m["name"] = self.get_name(item)
        m["title"] = item.metadata.get("title")
        m["description"] = item.metadata.get("description") if item.metadata.get("description") else m["title"]
        m["author"] = item.metadata.get("author")
        m["license_url"] = item.metadata.get("licenseurl")
        m["license"] = item.metadata.get("rights")
        m["metadata"] = item.metadata
        m["identifier"] = item.metadata.get("identifier")
        file_name = self.get_source_file(item)
        if not file_name:
            self.logger.warning("Could not find file for item '" + str(m.get('identifier')) + "'. Skipping item.")
            return False
        m["file_name"] = file_name
        file_path = self.get_file_directory() + "/" + file_name
        m["file_path"] = file_path.replace("/", "\\")
        m["thumbnail"] = self.get_thumbnail_path(item)
        m["preview"] = m["thumbnail"]
        return m

    def download_item(self, metadata):
        dest_dir = self.get_file_directory()
        d = download(metadata.get('identifier'), files=[metadata.get('file_name')], destdir=dest_dir, silent=True, no_directory=True, retries=3,             ignore_existing=True, ignore_errors=True)
        return d
    
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
        
    def get_name(self, item):
        name = str()
        if self.settings["prefix"]:
            name += self.settings["prefix"] + '-'
        name += slugify(item.metadata.get('title'))
        return name

    def get_allowed_formats(self, item):
        return self.settings["allowed_video_formats"] + self.settings["allowed_image_formats"]
        
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