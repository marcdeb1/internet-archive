from lbry_internet_archive import InternetArchive
import click

@click.command()
@click.option('--collection', default='', help='Internet Archive collection name to upload.')
@click.option('--config', default='default', help='Configuration file.')
def upload(collection, config):
	ia = InternetArchive(collection_name=collection, config_name=config)
	ia.upload_collection()

if __name__ == '__main__':
    upload()