import xml.etree.ElementTree as et
from article import Table
from article import Article
from pubmedpy import iter_articles, bulk_download_articles
import sys

for i, article in enumerate(iter_articles("PMC13900_PMC549049.xml.gz"), 1):
    a = article.get_paragraphs()
    if i == 11:
    # if any(isinstance(e, Table) for e in a):
        print('\n'.join(e.text for e in a))

        break
