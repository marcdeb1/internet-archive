import requests
import json
from .InternetArchiveSearch import *
from .LBRYObject import *

url = "http://localhost:5279/lbryapi"

ia = InternetArchiveSearch()
d = ia.get_identifiers()
transactions = list()

for id in d:
    identifier = id['identifier']
    print(identifier)
    document = ia.get_metadata(identifier)
    url = ia.get_file_url(document)
    f = ia.download_file(url)
    lbry_object = LBRYObject(f, document)
    # transaction = lbry_object.publish()
    # transactions.append(transaction)
