from pubmedpy import iter_articles

for article in iter_articles("examples/example1.xml.gz"):
    print(article)



