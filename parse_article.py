import xml.etree.ElementTree as et
from collections import UserList
# from urllib import request
# request.urlretrieve('ftp://server/path/to/file', 'file')


class Name(object):
    def __init__(self):
        self.surname = None
        self.given_names = None
        self.prefix = None
        self.suffix = None

    def __iter__(self):
        for n in [self.prefix, self.given_names, self.surname, self.suffix]:
            yield n

    def __repr__(self):
        return "Name(pre='{}' givenn='{}' surn='{}' suf='{}')".format(*self)

    def __str__(self):
        return ' '.join(n for n in self if n is not None)

    def parse(self, stub):
        if stub:
            surname = stub.find("surname")
            gname = stub.find("given-names")
            prefix = stub.find("prefix")
            suffix = stub.find("suffix")

            self.surname = surname.text if surname is not None else None
            self.given_names = gname.text if gname is not None else None
            self.prefix = prefix.text if prefix is not None else None
            self.suffix = suffix.text if suffix is not None else None


class Author(object):
    def __init__(self):
        self.name = None
        self.affiliations = None
        self.email = None

    def __repr__(self):
        author_repr = "Author("
        if self.name:
            author_repr += "name={}".format(repr(self.name))
        if self.email is not None:
            author_repr += " email={}".format(self.email)
        if self.affiliations is not None:
            author_repr += " affils={}".format(self.affiliations)
        author_repr += ')'

        return author_repr



class Metadata(object):
    def __init__(self):
        self.pmid = None
        self.title = None
        self.doi = None
        self.authors = None

    def __repr__(self):
        return "Metadata(pmid='{}', title='{}', doi='{}')".format(self.pmid, self.title, self.doi)


class Journal(object):
    def __init__(self):
        self.jid = None
        self.title = None

    def __repr__(self):
        return "Journal(id='{}', title='{}')".format(self.jid, self.title)


class Paragraph(object):
    def __init__(self):
        self.text = None

    def __repr__(self):
        return "Paragraph(nchars={})".format(len(self.text))


class Section(object):
    def __init__(self):
        self.title = None
        self.content = []

    def __repr__(self):
        return "\nSection(title='{}', content={})".format(self.title, self.content)

    def __len__(self):
        return len(self.content)

    def get_content(self, flatten=False):
        txt = []
        for ele in self.content:
            if isinstance(ele, Section):
                if flatten is True:
                    txt.extend(ele.get_content(flatten=flatten))
                else:
                    txt.append((ele.title, ele.get_content(flatten=flatten)[0]))
            elif isinstance(ele, Paragraph):
                txt.append(ele.text)
            else:
                raise("I was expecting Section or Paragraph, got %s", type(ele))
        return txt

    def get_titles(self):
        return [ele.title for ele in self.content if isinstance(ele, Section)]


class Body(object):
    def __init__(self):
        self.sections = []

    def __len__(self):
        return len(self.sections)

    def __repr__(self):
        return "Body({})".format(', '.join([repr(s) for s in self.sections]))

    def get_structure(self, main_sections=False):
        if main_sections is True:
            sections = [ele.title for ele in self.sections]
        else:
            sections = [(ele.title, ele.get_titles()) for ele in self.sections]
        return sections

    def get_flat_body(self, sections=None):
        bd = []
        for sec in self.sections:
            if sections is None or (isinstance(sections, list) and sec.title in sections):
                bd.extend(sec.get_content(flatten=True))
        return bd

    def get_nested_body(self, main_sections=False, sections=None):
        if main_sections is True:
            secs = [(sec.title, " ".join(sec.get_content(flatten=True))) for sec in self.sections]
        else:
            secs = [(sec.title, sec.get_content()) for sec in self.sections]

        if sections is not None:
            secs = [e for e in secs if e[0] in sections]

        return secs


class Article(object):
    def __init__(self):
        self.journal = None
        self.metadata = None
        self.article_type = None
        self.body = None

    def __repr__(self):
        rpr = "Article("
        if self.journal is not None:
            rpr += "\n" + repr(self.journal)
        if self.metadata is not None:
            rpr += "\n" + repr(self.metadata)
        if self.article_type is not None:
            rpr += "\nType='{}'".format(self.article_type)
        if self.body is not None:
            rpr += "\n" + repr(self.body)
        rpr += ')'

        return rpr

    def get_simple_text(self):
        return " ".join(self.body.get_flat_body())

    def get_nested_text(self, main_sections=False):
        return self.body.get_nested_body(main_sections=main_sections)

    def get_body_structure(self, main_sections=False):
        return self.body.get_structure(main_sections=main_sections)


def iter_articles(xml_file):
    for event, elem in et.iterparse(xml_file, events=("end",)):
        if event == 'end':
            if elem.tag == 'article':
                yield elem


def parse_body(body):
    bd = Body()
    for section in list(body):
        sec_txt = parse_section(section)
        bd.sections.append(sec_txt)
    return bd


def parse_section(section):
    sec = Section()
    for elem in list(section):
        if elem.tag == "title":
            sec.title = elem.text

        elif elem.tag == "sec":
            # recursive call
            sec.content.append(parse_section(elem))

        elif elem.tag == 'p':
            p = Paragraph()
            p.text = ''.join(elem.itertext())
            sec.content.append(p)

        else:
            print(elem.tag)

    return sec


def parse_authors(contrib_group, aff):
    authors = []
    affiliations = {}

    for affil in aff:
        # TODO: find a way to parse affil text (etree doesn't catch it apparently)
        geo = affil.text
        aid = affil.get('id')
        inst = ' '.join(e.text for e in affil.findall("institution-wrap/institution") if e is not None)
        affiliations[aid] = inst

    for contrib in contrib_group:
        author = Author()
        # name
        author.name = Name()
        author.name.parse(contrib.find("name"))
        # email
        email = contrib.find("address/email")
        author.email = email.text if email is not None else None
        # affiliations

        affils = contrib.findall("xref[@ref-type='aff']")
        author.affiliations = [affiliations.get(aff.get("rid")) for aff in affils if aff is not None]
        authors.append(author)

    return authors







def parse_front(front):
    jrn = Journal()
    jrn.title = front.find("journal-meta/journal-title-group/journal-title").text
    jrn.id = front.find("journal-meta/journal-id").text

    meta = Metadata()
    meta.pmid = front.find("article-meta/article-id[@pub-id-type=\"pmcid\"]").text
    meta.doi = front.find("article-meta/article-id[@pub-id-type=\"doi\"]").text
    meta.title = front.find("article-meta/title-group/article-title").text
    meta.authors = parse_authors(front.findall("article-meta/contrib-group/contrib[@contrib-type='author']"),
                            front.findall("article-meta/contrib-group/aff"))

    return jrn, meta


def parse_article(xml):
    if isinstance(xml, str):
        xml_tree = et.parse(xml)
    elif isinstance(xml, et.Element):
        xml_tree = xml
    else:
        raise ValueError("Expecting str or ET.Element, got (%s)", type(xml))

    art = Article()
    art.article_type = xml_tree.attrib.get("article-type")

    for elem in list(xml_tree):
        if elem.tag == "front":
            art.journal, art.metadata = parse_front(elem)
        elif elem.tag == "body":
            art.body = parse_body(elem)
        elif elem.tag == "back":
            pass
        elif elem.tag == "floats-group":
            pass
    return art
