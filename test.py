from pubmedpy import iter_articles, bulk_download_articles

for article in iter_articles("PMC13900_PMC549049.xml.gz"):
    pass
    # print(article.front.article_meta)

# bulk_download_articles("epmc")

