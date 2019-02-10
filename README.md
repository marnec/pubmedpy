```
from urllib import request
from parse_article import iter_articles, parse_article
request.urlretrieve('ftp://server/path/to/file', 'file')

for article in iter_articles("http://europepmc.org/ftp/oa/PMC1240577_PMC1474428.xml.gz"):
    print(parse_article(article))
    
    break
```