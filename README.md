I didn't like the other packages to parse xml articles so I wrote one.

Will update API and README.


```
for article in iter_articles("PMC1240577_PMC1474428.xml.gz"):
    print(article)
    break
    
Article(Front(
Journal(id='None', title='Critical Care')
Metadata(pmid='6302408', title='Intrapulmonary autologous transplant of bone marrow-derived mesenchymal stromal cells improves lipopolysaccharide-induced acute respiratory distress syndrome in rabbit', doi='10.1186/s13054-018-2272-x', authors=[Author(name=Name(pre='None' givenn='Mohammad Reza' surn='Mokhber Dezfouli' suf='None') email=mokhberd@ut.ac.ir affils=['Department of Internal Medicine, Faculty of Veterinary Medicine,  University of Tehran, ', 'Institute of Biomedical Research,  University of Tehran, ']), Author(name=Name(pre='None' givenn='Massoumeh' surn='Jabbari Fakhr' suf='None') email=mjabbarifakhr@gmail.com affils=['Institute of Biomedical Research,  University of Tehran, ']), Author(name=Name(pre='None' givenn='Sirous' surn='Sadeghian Chaleshtori' suf='None') email=s.sadeghian@ut.ac.ir affils=['Department of Internal Medicine, Faculty of Veterinary Medicine,  University of Tehran, ', 'Institute of Biomedical Research,  University of Tehran, ']), Author(name=Name(pre='None' givenn='Mohammad Mehdi' surn='Dehghan' suf='None') email=mdehghan@ut.ac.ir affils=['Department of Surgery and Radiology, Faculty of Veterinary Medicine,  University of Tehran, ', 'Institute of Biomedical Research,  University of Tehran, ']), Author(name=Name(pre='None' givenn='Alireza' surn='Vajhi' suf='None') email=avajhi@ut.ac.ir affils=['Department of Surgery and Radiology, Faculty of Veterinary Medicine,  University of Tehran, ', 'Institute of Biomedical Research,  University of Tehran, ']), Author(name=Name(pre='None' givenn='Roshanak' surn='Mokhtari' suf='None') email=roshanak.mokhtari@gmail.com affils=['Department of Surgery and Radiology, Faculty of Veterinary Medicine,  University of Tehran, '])]))
Type='research-article'
Body(
Section(title='Background', content=[Paragraph(nchars=2902)]), 
Section(title='Statistical analysis', content=[Paragraph(nchars=1182), None, Paragraph(nchars=479), None, Paragraph(nchars=219), None, None, Paragraph(nchars=451), None, None, Paragraph(nchars=485), None, None, Paragraph(nchars=816), None, None, Paragraph(nchars=326), None, Paragraph(nchars=307), None]), 
Section(title='Findings of gross pathology and histopathology', content=[Paragraph(nchars=271), None, Paragraph(nchars=386), None, Paragraph(nchars=288), None, None, Paragraph(nchars=828), None, Paragraph(nchars=1286), Paragraph(nchars=452), Paragraph(nchars=688), Paragraph(nchars=686), None, None, Paragraph(nchars=3480), Paragraph(nchars=419), Paragraph(nchars=163), Paragraph(nchars=384), None, Paragraph(nchars=660), Paragraph(nchars=1356), None, None, Paragraph(nchars=518), Paragraph(nchars=391), Paragraph(nchars=255), Paragraph(nchars=654), None, Paragraph(nchars=316), None, Paragraph(nchars=376), Paragraph(nchars=646), Paragraph(nchars=720), Paragraph(nchars=1191), None, Paragraph(nchars=2073), None, None, Paragraph(nchars=4915), None, Paragraph(nchars=2009), Paragraph(nchars=307), None]), 
Section(title='Discussion', content=[Paragraph(nchars=264), Paragraph(nchars=439), Paragraph(nchars=718), Paragraph(nchars=1142), Paragraph(nchars=1048), Paragraph(nchars=1292), Paragraph(nchars=1870), Paragraph(nchars=1451), Paragraph(nchars=421)]), 
Section(title='Conclusions', content=[Paragraph(nchars=1017)]), 
Section(title='Additional file', content=[Paragraph(nchars=86), None])))
```