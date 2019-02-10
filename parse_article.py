import xml.etree.ElementTree as et
from article import Article

# from urllib import request
# request.urlretrieve('ftp://server/path/to/file', 'file')


def iter_articles(xml_file):
    for event, elem in et.iterparse(xml_file, events=("end",)):
        if event == 'end':
            if elem.tag == 'article':
                yield Article(elem)
