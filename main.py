from InternetArchiveSearch import *
from LBRYObject import *


def process_document(item, ia):
    identifier = item['identifier']
    content = ia.get_and_download_content(identifier)
    lbry_object = LBRYObject(content)
    print("Publishing " + str(identifier) + "...")
    transaction = lbry_object.publish()
    print("Transaction : " + str(transaction) + '\n')


def process_collection(collection_name, collection_type):
    query = "collection:" + collection_name
    ia = InternetArchiveSearch(query=query, file_type=collection_type)
    documents = ia.get_identifiers()
    for d in documents:
        process_document(d, ia)

process_collection("earthdayimagegallery", 'IMAGE')