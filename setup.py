from setuptools import setup

setup(name='lbry_internet_archive',
      version='0.2',
      description='A tool to import Internet Archive collections to LBRY',
      url='https://github.com/marcdeb1/internet-archive',
      author='marcdeb',
      author_email='marcdebrouchev@laposte.net',
      license='MIT',
      packages=['lbry_internet_archive'],
      insall_requires=['lbry-uploader', 'internetarchive', 'click', 'slugify'],
      zip_safe=False)