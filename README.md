I didn't like the other packages to parse xml articles so I wrote one.

Will update API and README.


```
for article in iter_articles("PMC1240577_PMC1474428.xml.gz"):
    print(article)
    break
    
Article(Front(
Journal(id='Crit Care', title='Critical Care')
Metadata(pmid='6302408', title='Intrapulmonary autologous transplant of bone marrow-derived mesenchymal stromal cells improves lipopolysaccharide-induced acute respiratory distress syndrome in rabbit', doi='10.1186/s13054-018-2272-x', authors=[Author(name=Name(pre='None' givenn='Mohammad Reza' surn='Mokhber Dezfouli' suf='None') email=mokhberd@ut.ac.ir affils=['Department of Internal Medicine, Faculty of Veterinary Medicine,  University of Tehran, ', 'Institute of Biomedical Research,  University of Tehran, ']), Author(name=Name(pre='None' givenn='Massoumeh' surn='Jabbari Fakhr' suf='None') email=mjabbarifakhr@gmail.com affils=['Institute of Biomedical Research,  University of Tehran, ']), Author(name=Name(pre='None' givenn='Sirous' surn='Sadeghian Chaleshtori' suf='None') email=s.sadeghian@ut.ac.ir affils=['Department of Internal Medicine, Faculty of Veterinary Medicine,  University of Tehran, ', 'Institute of Biomedical Research,  University of Tehran, ']), Author(name=Name(pre='None' givenn='Mohammad Mehdi' surn='Dehghan' suf='None') email=mdehghan@ut.ac.ir affils=['Department of Surgery and Radiology, Faculty of Veterinary Medicine,  University of Tehran, ', 'Institute of Biomedical Research,  University of Tehran, ']), Author(name=Name(pre='None' givenn='Alireza' surn='Vajhi' suf='None') email=avajhi@ut.ac.ir affils=['Department of Surgery and Radiology, Faculty of Veterinary Medicine,  University of Tehran, ', 'Institute of Biomedical Research,  University of Tehran, ']), Author(name=Name(pre='None' givenn='Roshanak' surn='Mokhtari' suf='None') email=roshanak.mokhtari@gmail.com affils=['Department of Surgery and Radiology, Faculty of Veterinary Medicine,  University of Tehran, '])]))
Type='research-article'
Body(
Section(title='Background', content=[Paragraph(nchars=2902)]), 
Section(title='Methods', content=[
Section(title='Isolation, primary culture, and expansion of BM-MSCs', content=[Paragraph(nchars=1182)]), 
Section(title='Experimental design', content=[
Section(title='ARDS experimental model', content=[Paragraph(nchars=479)]), 
Section(title='BM-MSC autologous transplant', content=[Paragraph(nchars=219)])]), 
Section(title='Analyses', content=[
Section(title='Clinical assessment', content=[Paragraph(nchars=451)])]), 
Section(title='Imaging', content=[
Section(title='Computed tomography and echocardiography', content=[Paragraph(nchars=485)])]), 
Section(title='Sampling', content=[
Section(title='Blood and bronchoalveolar lavage samples', content=[Paragraph(nchars=816)])]), 
Section(title='Histopathology', content=[Paragraph(nchars=326)]), 
Section(title='Statistical analysis', content=[Paragraph(nchars=307)])]), 
Section(title='Results', content=[
Section(title='Characterization of BMSCs', content=[
Section(title='Culture of BM-MSCs', content=[Paragraph(nchars=271)]), 
Section(title='Flow cytometric analysis', content=[Paragraph(nchars=386)]), 
Section(title='Differentiation', content=[Paragraph(nchars=288)])]), 
Section(title='Confirmation of ARDS experimental model', content=[Paragraph(nchars=828)]), 
Section(title='Clinical and paraclinical findings after transplant of BM-MSCs in an experimental model of ARDS', content=[
Section(title='Improved clinical signs with MSCs', content=[Paragraph(nchars=1286), Paragraph(nchars=452), Paragraph(nchars=688), Paragraph(nchars=686)])]), 
Section(title='MSCs cause blood cells and BAL cells to balance', content=[
Section(title='Blood cells', content=[Paragraph(nchars=3480), Paragraph(nchars=419), Paragraph(nchars=163), Paragraph(nchars=384)]), 
Section(title='Cells from BAL', content=[Paragraph(nchars=660), Paragraph(nchars=1356)])]), 
Section(title='Regulation of arterial blood gases with MSCs', content=[Paragraph(nchars=518), Paragraph(nchars=391), Paragraph(nchars=255), Paragraph(nchars=654)]), 
Section(title='Effect of MSCs on arterial blood electrolytes', content=[Paragraph(nchars=316)]), 
Section(title='Reduced levels of proinflammatory cytokines and increase in anti-inflammatory cytokine by MSCs', content=[Paragraph(nchars=376), Paragraph(nchars=646), Paragraph(nchars=720), Paragraph(nchars=1191)]), 
Section(title='Imaging findings', content=[
Section(title='Tomodensitometric and volumetric findings of lung CT scans', content=[Paragraph(nchars=2073)])]), 
Section(title='Echocardiography findings', content=[Paragraph(nchars=4915)]), 
Section(title='Findings of gross pathology and histopathology', content=[Paragraph(nchars=2009), Paragraph(nchars=307)])]), 
Section(title='Discussion', content=[Paragraph(nchars=264), Paragraph(nchars=439), Paragraph(nchars=718), Paragraph(nchars=1142), Paragraph(nchars=1048), Paragraph(nchars=1292), Paragraph(nchars=1870), Paragraph(nchars=1451), Paragraph(nchars=421)]), 
Section(title='Conclusions', content=[Paragraph(nchars=1017)]), 
Section(title='Additional file', content=[
Section(title='None', content=[Paragraph(nchars=86)])])))
```