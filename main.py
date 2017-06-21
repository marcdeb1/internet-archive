from .InternetArchiveSearch import *
from .LBRYObject import *

ia = InternetArchiveSearch()
identifiers = ia.get_identifiers()
transactions = list()

for item in identifiers:
    identifier = item['identifier']
    print(identifier)
    document = ia.get_metadata(identifier)
    url = ia.get_file_url(document)
    f = ia.download_file(url)
    lbry_object = LBRYObject(f, document)
    transaction = lbry_object.publish()
    transactions.append(transaction)

