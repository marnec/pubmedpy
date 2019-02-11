from parse_article import iter_articles

for article in iter_articles("examples/example0.xml"):
    print(article.get_body_structure(main_sections=True))
