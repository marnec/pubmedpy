import xml.etree.ElementTree as et
import sys


# TODO: find out how to call son method instead of placeholder
# class XmlTag(object):
#     def __init__(self, stub=None):
#
#         if stub is not None:
#             self.parse(stub)
#
#     @classmethod
#     def parse(self, stub):
#         pass


class SupplementaryMaterial(object):
    def __init__(self, stub=None):
        self.label = None
        self.caption = None
        self.content = None

        if stub is not None:
            self.parse(stub)

    def parse(self, stub):
        label = stub.find("label")
        self.label = label.text if label else None
        caption = stub.find("caption")
        self.caption = "".join(caption.itertext()) if caption else None

        self.content = []
        for ele in list(stub):
            if ele.tag not in {"caption", "label"}:
                self.content.append(html_classes[ele.tag](ele))


class GraphicMedia(object):
    def __init__(self, stub=None):
        self.obj_id = None
        self.label = None
        self.caption = None
        self.href = None

        if stub is not None:
            self.parse(stub)

    def parse(self, stub):
        label = stub.find("label")
        self.label = label.text if label else None
        caption = stub.find("caption")
        self.caption = "".join(caption.itertext()) if caption else None

        self.href = stub.get("ns0:href")

    def get_content(self, flatten=None):
        return [(self.caption, self.href)]


class Figure(object):
    def __init__(self, stub=None):
        self.label = None
        self.caption = None
        self.graphics = None
        self.namespace = None

        if stub is not None:
            self.parse(stub)

    def parse(self, stub):
        label = stub.find("label")
        self.label = label.text if label else None
        caption = stub.find("caption")
        self.caption = caption.text if caption else None
        self.namespace = stub.get("xmlns:ns0")

        self.graphics = []
        for graphic in stub.findall("graphic"):
            self.graphics.append(GraphicMedia(graphic))

    def get_content(self, flatten=None):
        return [(self.caption, self.graphics)]

class TableGroup(object):
    def __init__(self, stub=None):
        self.label = None
        self.caption = None
        self.tables = None

        if stub is not None:
            self.parse(stub)

    def __repr__(self):
        return "TableGroup(label={}, caption={}\n{})".format(self.label, self.caption, "\n".join(repr(t) for t in self.tables))

    def parse(self, stub):
        label = stub.find("label")
        self.label = label.text if label else None
        caption = stub.find("caption")
        self.caption = caption.text if caption else None

        self.tables = []
        for table in stub.findall("table-wrap"):
            self.tables.append(TableWrap(table))


class TableWrap(object):
    def __init__(self, stub=None):
        self.label = None
        self.caption = None
        self.tables = None
        self.footer = None

        if stub is not None:
            self.parse(stub)

    def __repr__(self):
        return "TableWrap(label={}, caption={}\n{})".format(self.label, self.caption, "\n".join(repr(t) for t in self.tables))

    def parse(self, stub):
        label = stub.find("label")
        self.label = label.text if label else None
        caption = stub.find("caption")
        self.caption = caption.text if caption else None
        footer = stub.find("table-wrap-foot")
        self.footer = footer.text if footer else None

        self.tables = []
        for table in stub.findall("table"):
            self.tables.append(Table(table))

    def get_content(self, flatten=None):
        return [(self.caption, self.tables)]


class Table(object):
    def __init__(self, stub=None):
        self.content = None
        self.caption = None

        if stub is not None:
            self.parse(stub)

    def __repr__(self):
        rpr = []

        for row in self.content:
            col_widths = map(lambda t: len(max(t, key=len)), zip(*self.content))
            rpr.append("  ".join("{:<{r}}".format(cell, r=align) for cell, align in zip(row, col_widths)))

        return "Table(caption='{}'\n{})".format(self.caption, "\n".join(rpr))

    def parse(self, stub):
        # parse caption
        caption = stub.find("caption")
        self.caption = caption.text if caption else None
        # parse table
        self.content = []
        rowspans = {}
        contents = {}

        for elem in stub.iter(tag="tr"):
            row = []
            cell_index = 0

            for cell in list(elem):
                cell_text = ''.join(cell.itertext()).strip()

                rowspan = cell.get("rowspan")
                rowspans[cell_index] = int(rowspan) if rowspan else (rowspans.get(cell_index, 0))
                if rowspan is not None:
                    contents[cell_index] = cell_text

                if rowspan is None and rowspans[cell_index] > 0:
                    row.append(contents[cell_index])
                    rowspans[cell_index] -= 1

                colspan = cell.get("colspan")
                colspan = int(colspan) if colspan else 1
                row.extend([''.join(cell_text)]*colspan)

                cell_index += colspan
            self.content.append(row)


class Name(object):
    def __init__(self, stub=None):
        self.surname = None
        self.given_names = None
        self.prefix = None
        self.suffix = None

        if stub is not None:
            self.parse(stub)

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
    def __init__(self, stub=None, affs=None):
        self.name = None
        self.affiliations = None
        self.email = None

        if stub is not None and affs is not None:
            self.parse(stub, affs)

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

    def parse(self, stub, affs):
        # name
        self.name = Name(stub.find("name"))
        # email
        email = stub.find("address/email")
        self.email = email.text if email is not None else None
        # affiliations
        affils = stub.findall("xref[@ref-type='aff']")
        self.affiliations = [affs.get(aff.get("rid")) for aff in affils if aff is not None]


class Metadata(object):
    def __init__(self, stub=None):
        self.pmid = None
        self.title = None
        self.doi = None
        self.authors = None

        if stub is not None:
            self.parse(stub)

    def __repr__(self):
        return "Metadata(pmid='{}', title='{}', doi='{}', authors={})".format(
            self.pmid, self.title, self.doi, self.authors)

    def parse(self, stub):
        pmid = stub.find("article-id[@pub-id-type='pmid']")
        pmcid = stub.find("article-id[@pub-id-type='pmcid']")
        doi = stub.find("article-id[@pub-id-type='doi']")
        self.pmid = pmid.text if pmid is not None else None
        self.pmcid = pmcid.text if pmcid is not None else None
        self.doi = doi.text if doi is not None else None

        self.title = stub.find("title-group/article-title").text
        self.authors = self._parse_authors(
            stub.findall("contrib-group/contrib[@contrib-type='author']"),
            stub.findall("contrib-group/aff"))

    @staticmethod
    def _parse_authors(contrib_group, aff):
        authors = []
        affiliations = {}

        for affil in aff:
            aff = Affiliation(affil)
            affiliations[aff.aid] = aff

        for contrib in contrib_group:
            author = Author(contrib, affiliations)
            authors.append(author)

        return authors


class Affiliation(object):
    def __init__(self, stub=None):
        self.institution = None
        self.aid = None

        if stub is not None:
            self.parse(stub)

    def __repr__(self):
        return "Affiliation(id='{}' institution='{}')".format(self.aid, ' '.join(self.institution))

    def parse(self, stub):
        self.aid = stub.get('id')

        inst_wrap = stub.find("institution-wrap")
        if inst_wrap is not None:
            self.institution = [e.text for e in inst_wrap.findall("institution") if e is not None]

            geo = inst_wrap.tail
            if geo is not None:
                self.institution.append(geo)


class Journal(object):
    def __init__(self, stub=None):
        self.jid = None
        self.title = None

        if stub is not None:
            self.parse(stub)

    def __repr__(self):
        return "Journal(id='{}', title='{}')".format(self.jid, self.title)

    def parse(self, stub):
        title = stub.find("journal-title-group/journal-title")
        self.title = title.text if title else None
        self.jid = stub.find("journal-id").text


class Front(object):
    def __init__(self, stub=None):
        self.journal_meta = None
        self.article_meta = None

        if stub is not None:
            self.parse(stub)

    def __repr__(self):
        rpr = "Front("
        if self.journal_meta is not None:
            rpr += "\n" + repr(self.journal_meta)
        if self.article_meta is not None:
            rpr += "\n" + repr(self.article_meta)
        rpr += ')'

        return rpr

    def parse(self, stub):
        self.journal_meta = Journal(stub.find("journal-meta"))
        self.article_meta = Metadata(stub.find("article-meta"))


class Paragraph(object):
    def __init__(self, stub=None):
        self.title = None
        self.text = None

        if stub is not None:
            self.parse(stub)

    def __repr__(self):
        return "Paragraph(nchars={})".format(len(self.text))

    def parse(self, stub):
        self.text = ''.join(stub.itertext())

    def get_content(self, flatten=None):
        """
        Mock method to comply with paragraphs that are direct children of Body.

        Using this method Body.get_nested() and Body.get_flat() can retrieve text within
        paragraphs that are direct children of Body without the need of handling specific
        Types.

        :param flatten:
        :return:
        """
        return [(None, self.text)]


class Section(object):
    def __init__(self, stub=None):
        self.title = None
        self.content = []

        if stub is not None:
            self.parse(stub)

    def __repr__(self):
        return "\nSection(title='{}', content={})".format(self.title, self.content)

    def __len__(self):
        return len(self.content)

    def parse(self, stub):
        for i, elem in enumerate(list(stub)):
            if elem.tag == "title":
                self.title = "".join(elem.itertext())
            else:
                try:
                    self.content.append(html_classes[elem.tag](elem))
                except KeyError:
                    if elem.tag == "italic":
                        pass
                    else:
                        print(et.tostring(stub))
                        print(i, et.tostring(elem))
                        sys.exit()
            # elif elem.tag == "sec":
            #     self.content.append(Section(elem))
            # elif elem.tag == 'p':
            #     self.content.append(Paragraph(elem))
            # elif elem.tag == "table-wrap":
            #     self.content.append(TableWrap(elem))
            # elif elem.tag == "table-wrap-group":
            #     self.content.append(TableGroup(elem))
            # elif elem.tag == "fig":
            #     self.content.append(Figure(elem))
            # elif elem.tag == "graphic":
            #     self.content.append(Graphic(elem))
            # elif elem.tag == "supplementary-material":
            #     pass
            # elif elem.tag == "italic":
            #     pass

    def get_content(self, flatten=False):
        # TODO: make all types compliant with get_content
        txt = []
        for ele in self.content:
            if isinstance(ele, Section):
                if flatten is True:
                    txt.extend(ele.get_content(flatten=flatten))
                else:
                    txt.append((ele.title, ele.get_content(flatten=flatten)))
            elif isinstance(ele, (Paragraph, TableWrap, Figure, GraphicMedia)):
                txt.append(ele.get_content())
            else:
                raise ValueError("I was expecting Section or Paragraph, got %s", type(ele))
        return txt

    def get_titles(self):
        return [ele.title for ele in self.content if isinstance(ele, Section)]


class Body(object):
    def __init__(self, stub=None):
        self.sections = []

        if stub is not None:
            self.parse(stub)

    def __len__(self):
        return len(self.sections)

    def __repr__(self):
        return "Body({})".format(', '.join([repr(s) for s in self]))

    def __iter__(self):
        for ele in self.sections:
            yield ele

    def parse(self, stub):
        for elem in list(stub):
            self.sections.append(html_classes[elem.tag](elem))

    def get_structure(self, main_sections=False):
        if main_sections is True:
            sections = [ele.title for ele in self if isinstance(ele, Section)]
        else:
            sections = [(ele.title, ele.get_titles()) for ele in self if isinstance(ele, Section)]
        return sections

    def get_flat(self, sections=None):
        bd = []
        for sec in self:
            if sections is None or (isinstance(sections, list) and sec.title in sections):
                bd.extend(sec.get_content(flatten=True))
        return bd

    def get_nested(self, main_sections=False, sections=None):
        if main_sections is True:
            secs = [(sec.title, " ".join(sec.get_content(flatten=True))) for sec in self]
        else:
            secs = [(sec.title, sec.get_content()) for sec in self]

        if sections is not None:
            secs = [e for e in secs if e[0] in sections]

        return secs


class Article(object):
    def __init__(self, xml=None):
        self.type = None
        self.front = None
        self.body = None
        self.back = None

        if xml is not None:
            self.parse(xml)

    def __repr__(self):
        rpr = "Article("
        if self.front is not None:
            rpr += repr(self.front)
        if self.type is not None:
            rpr += "\nType='{}'".format(self.type)
        if self.body is not None:
            rpr += "\n" + repr(self.body)
        rpr += ')'

        return rpr

    def parse(self, xml):
        if isinstance(xml, str):
            xml_tree = et.parse(xml)
        elif isinstance(xml, et.Element):
            xml_tree = xml
        else:
            raise ValueError("Expecting str or ET.Element, got (%s)", type(xml))

        self.type = xml_tree.attrib.get("article-type")

        for elem in list(xml_tree):
            if elem.tag == "front":
                self.front = Front(elem)
            elif elem.tag == "body":
                self.body = Body(elem)
            elif elem.tag == "back":
                pass
            elif elem.tag == "floats-group":
                pass

    def get_simple_text(self):
        return "\n".join(self.body.get_flat())

    def get_nested_text(self, main_sections=False):
        return self.body.get_nested(main_sections=main_sections)

    def get_body_structure(self, main_sections=False):
        return self.body.get_structure(main_sections=main_sections)

    def get_authors(self):
        return self.front.article_meta.authors


html_classes = {
    "sec": Section,
    "p": Paragraph,
    "fig": Figure,
    "graphic": GraphicMedia,
    "media": GraphicMedia,
    "table": Table,
    "table-wrap": TableWrap,
    "table-wrap-group": TableGroup,
    "supplementary-material": SupplementaryMaterial
}
