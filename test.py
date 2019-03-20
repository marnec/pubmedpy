import xml.etree.ElementTree as et
from article import Article
from article import Table
from pubmedpy import iter_articles, bulk_download_articles
import sys

for i, article in enumerate(iter_articles("PMC13900_PMC549049.xml.gz"), 1):
    a = article.get_flat_content()
    print(any(isinstance(e, Table) for e in a))
    if any(isinstance(e, Table) for e in a):
        print(str(a))

        break
