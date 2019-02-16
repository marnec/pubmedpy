from pubmedpy import iter_articles, bulk_download_articles
import sys

for i, article in enumerate(iter_articles("PMC13900_PMC549049.xml.gz"), 1):
    print(article.front.article_meta.title)
    # print(article.front.article_meta)

# bulk_download_articles("epmc")
# ts = "<table><tr> <th colspan='2'>65</th> <th colspan='2'>40</th> <th colspan='2'>20</th> </tr> <tr> <th>Men</th> <th>Women</th> <th>Men</th> <th>Women</th> <th>Men</th> <th>Women</th> </tr> <tr> <td>82</td> <td>85</td> <td>78</td> <td>82</td> <td>77</td> <td>81</td> </tr> </table>"
# ts2 = "<table> <caption>Invoice</caption> <tr> <th>Item / Desc.</th> <th>Qty.</th> <th>@</th> <th>Price</th> </tr> <tr> <td>Paperclips (Box)</td> <td>100</td> <td>1.15</td> <td>115.00</td> </tr> <tr> <td>Paper (Case)</td> <td>10</td> <td>45.99</td> <td>459.90</td> </tr> <tr> <td>Wastepaper Baskets</td> <td>2</td> <td>17.99</td> <td>35.98</td> </tr> <tr> <th colspan='3'>Subtotal</th> <td>610.88</td> </tr> <tr> <th colspan='2'>Tax</th> <td>7%</td> <td>42.76</td> </tr> <tr> <th colspan='3'>Total</th> <td>653.64</td> </tr> </table>"
# ts3 = "<table> <caption>Favorite and Least Favorite Things</caption> <tr> <th></th><th></th> <th>Bob</th> <th>Alice</th> </tr> <tr> <th rowspan='2'>Favorite</th> <th>Color</th> <td>Blue</td> <td>Purple</td> </tr> <tr> <th>Flavor</th> <td>Banana</td> <td>Chocolate</td> </tr> <tr> <th rowspan='2'>Least Favorite</th> <th>Color</th> <td>Yellow</td> <td>Pink</td> </tr> <tr> <th>Flavor</th> <td>Mint</td> <td>Walnut</td> </tr> </table>"
# t = et.fromstring(ts3)
# print(Table(t))