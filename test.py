import xml.etree.ElementTree as et
from article import Article
from pubmedpy import iter_articles, bulk_download_articles
import sys

for i, article in enumerate(iter_articles("PMC13900_PMC549049.xml.gz", parse=False), 1):
    # print(article.get_flat_text())
    if i % 100 == 0 and i != 0:
        print("\r{}".format(i), end='')
    try:
        article = Article(article)
        article.get_nested_text()
    except Exception as e:
        with open("examples/article{}.xml".format(i), 'wb') as f:
            f.write(et.tostring(article))
            if i not in {5690, 6034, 9172}:
                raise e
