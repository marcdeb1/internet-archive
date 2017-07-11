from InternetArchiveSearch import *
from LBRYUpload import *
from Database import *
from settings import *


def process_document(item, ia):
    identifier = item['identifier']
    db = Database(name=COLLECTION_NAME + '.db')
    lbry = LBRYUpload()
    content = db.get_item(identifier=identifier)
    if not content:
        content = ia.get_and_download_content(identifier)
    if not content['published']:
            lbry.publish(content)
    else:
        print('Content already published !\n')


def process_collection(collection_name, collection_type):
    query = "collection:" + collection_name
    ia = InternetArchiveSearch(query=query, file_type=collection_type)
    documents = ia.get_identifiers()
    for d in documents:
        process_document(d, ia)

process_collection(COLLECTION_NAME, 'VIDEO')