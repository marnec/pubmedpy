import xml.etree.ElementTree as et
from article import Article
from pubmedpy import iter_articles, bulk_download_articles
import sys

for i, article in enumerate(iter_articles("PMC13900_PMC549049.xml.gz"), 1):
    a = article.todict()
    print(a)
    break
