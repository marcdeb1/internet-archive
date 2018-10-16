# internet-archive
Extracting data from the Internet Archive (https://archive.org/) to LBRY. For more information on the LBRY project, visit https://lbry.tech/.

## Installation
.
- Install package lbry_uploader by following instructions at https://github.com/marcdeb1/lbry_uploader.
- Clone or download internet-archive repository : `git clone https://github.com/marcdeb1/internet-archive.git`.
- Run `pip install .` in cloned folder.

## How to use

The uploader takes a collection name as an input. The most simple way to use it is by running : 

`python upload.py --collection=covertartarchive   # To download https://archive.org/details/coverartarchive` 

or

```
from lbry_internet_archive import InternetArchive
uploader = InternetArchive(collection_name=collection_name, config_name=config) # config_name is optional
uploader.upload_collection()
```
In the configuration file, it is possible to set a prefix for the claim names and the channel to publish the content to.

Note: The config argument is optional. Default settings (default.ini file) will be used if not provided.

## Default values

Default values can be set in the configuration file. If values are not found or empty in the input file, the uploader will use the values from the configuration file. Edit default.ini to change the default values, or create a new 'ini' file and pass it as an argument to the uploader. The config file must be an 'ini' file. 
