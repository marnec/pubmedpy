from pubmedpy import iter_articles, bulk_download_articles

for article in iter_articles("examples/example1.xml.gz"):
    print(article)



# bulk_download_articles("pmc", use="non_comm")

