import xml.etree.ElementTree as et
import sys


class List(object):
    def __init__(self, stub=None):
        self.elements = None

        if stub is not None:
            self.parse(stub)

    def __iter__(self):
        for e in self.elements:
            yield e

    def repr(self):
        return "List({})".format(self.elements)

    def parse(self, stub):
        self.elements = []
        for item in stub.iter(tag="list-item"):
            self.elements.append("".join(item.itertext()))


class NestedContainer(object):
    def __init__(self, stub=None):
        self.title = None
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
        title = stub.find("title")
        self.title = "".join(title.itertext()) if title is not None else None

        if self.title is None:
            self.title = ""
        if self.label is not None:
            self.title += self.label
        if self.caption is not None:
            self.title += self.caption
        # self.title = self.title if self.title else None

        self.content = []
        for ele in list(stub):
            if ele.tag not in {"caption", "label", "title"} | unspported_tags:
                self.content.append(html_classes[ele.tag](ele))

    def get_content(self, flatten=False):
        cnt = []
        for ele in self.content:
            if flatten is True:
                cnt.extend(ele.get_content(flatten=flatten))
            else:
                cnt.append((ele.title, ele.get_content(flatten=flatten)))
        return cnt


class ReferencedContent(object):
    def __init__(self, stub=None):
        self.obj_id = None
        self.label = None
        self.title = None
        self.caption = None
        self.href = None

        if stub is not None:
            self.parse(stub)

    def parse(self, stub):
        label = stub.find("label")
        self.label = label.text if label else None
        caption = stub.find("caption")
        self.caption = "".join(caption.itertext()) if caption else None
        title = stub.find("title")
        self.title = "".join(title.itertext()) if title is not None else None

        if self.title is None:
            self.title = ""
        if self.label is not None:
            self.title += self.label
        if self.caption is not None:
            self.title += self.caption

        self.href = stub.get("ns0:href")

    def get_content(self, **kwargs):
        return [self.href]


class Figure(object):
    def __init__(self, stub=None):
        self.label = None
        self.title = None
        self.caption = None
        self.graphics = None
        self.namespace = None

        if stub is not None:
            self.parse(stub)

    def parse(self, stub):
        label = stub.find("label")
        self.label = label.text if label else None
        caption = stub.find("caption")
        self.caption = "".join(caption.itertext()) if caption else None
        title = stub.find("title")
        self.title = "".join(title.itertext()) if title is not None else None

        if self.title is None:
            self.title = ""
        if self.label is not None:
            self.title += self.label
        if self.caption is not None:
            self.title += self.caption

        self.namespace = stub.get("xmlns:ns0")

        self.graphics = []
        for graphic in stub.findall("graphic"):
            self.graphics.append(ReferencedContent(graphic))

    def get_content(self, flatten=False):
        return [(self.title, self.graphics)] if flatten is False else list(map(repr, self.graphics))


class TableGroup(object):
    def __init__(self, stub=None):
        self.label = None
        self.title = None
        self.caption = None
        self.tables = None

        if stub is not None:
            self.parse(stub)

    def __repr__(self):
        return "TableGroup(title={}, caption={}\n{})".format(self.title, self.caption, "\n".join(self.tables))

    def parse(self, stub):
        label = stub.find("label")
        self.label = label.text if label else None
        caption = stub.find("caption")
        self.caption = "".join(caption.itertext()) if caption else None
        title = stub.find("title")
        self.title = "".join(title.itertext()) if title is not None else None

        if self.title is None:
            self.title = ""
        if self.label is not None:
            self.title += self.label
        if self.caption is not None:
            self.title += self.caption


class TableWrap(object):
    def __init__(self, stub=None):
        self.label = None
        self.title = None
        self.caption = None
        self.tables = None
        self.footer = None

        if stub is not None:
            self.parse(stub)

    def __repr__(self):
        return "TableWrap(title={}, caption={}\n{})".format(self.title, self.caption, "\n".join(self.tables))

    def parse(self, stub):
        label = stub.find("label")
        self.label = label.text if label else None
        caption = stub.find("caption")
        self.caption = "".join(caption.itertext()) if caption else None
        title = stub.find("title")
        self.title = "".join(title.itertext()) if title is not None else None

        if self.title is None:
            self.title = ""
        if self.label is not None:
            self.title += self.label
        if self.caption is not None:
            self.title += self.caption

        footer = stub.find("table-wrap-foot")
        self.footer = footer.text if footer else None

        self.tables = []
        for table in stub.findall("table"):
            self.tables.append(Table(table))

    def get_content(self, flatten=False):
        return [(self.title, self.tables)] if flatten is False else [repr(t) for t in self.tables]


class Table(object):
    def __init__(self, stub=None):
        self.title = None
        self.content = None

        if stub is not None:
            self.parse(stub)

    def __repr__(self):
        return "\n{}".format("\n".join(self._tabulate()))

    def _tabulate(self):
        rpr = []

        for row in self.content:
            col_widths = map(lambda t: len(max(t, key=len)), zip(*self.content))
            rpr.append("  ".join("{:<{r}}".format(cell, r=align) for cell, align in zip(row, col_widths)))
        return rpr

    def parse(self, stub):
        # parse caption
        self.title = stub.get("id")

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
        self.pmcid = None
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
    i = 1

    def __init__(self, stub=None):
        self.title = "Paragraph{}".format(self.i)
        self.text = None
        Paragraph.i += 1

        if stub is not None:
            self.parse(stub)

    def __repr__(self):
        return "Paragraph(nchars={})".format(len(self.text))

    def parse(self, stub):
        # self.title = stub.get("id")
        self.text = ''.join(stub.itertext())

    def get_content(self, **kwargs):
        """
        Mock method to comply with paragraphs that are direct children of Body.

        Using this method Body.get_nested() and Body.get_flat() can retrieve text within
        paragraphs that are direct children of Body without the need of handling specific
        Types.
        """
        return [self.text]


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
        for elem in list(stub):
            if elem.tag in {"title"}:
                self.title = "".join(elem.itertext())
            elif elem.tag in unspported_tags:
                pass  # ignore
            else:
                try:
                    self.content.append(html_classes[elem.tag](elem))
                except KeyError as e:
                    print(elem.tag, et.tostring(elem))
                    raise KeyError(e)


    def get_content(self, flatten=False):
        cnt = []
        for ele in self.content:
            if flatten is True or not isinstance(ele, (Section, NestedContainer)):
                cnt.extend(ele.get_content(flatten=flatten))
            else:
                cnt.append((ele.title, ele.get_content(flatten=flatten)))
        return cnt

    def get_text(self, flatten=False):
        txt = []
        for ele in self.content:
            # TODO: find other text-bearing elements
            if isinstance(ele, (Section, Paragraph)):
                if flatten is True:
                    txt.extend(ele.get_content(flatten=flatten))
                else:
                    txt.append((ele.title, ele.get_content(flatten=flatten)))
        return txt

    def get_titles(self):
        return [ele.title for ele in self.content if isinstance(ele, Section)]


class Body(object):
    def __init__(self, stub=None):
        self.content = []

        if stub is not None:
            self.parse(stub)

    def __len__(self):
        return len(self.content)

    def __repr__(self):
        return "Body({})".format(', '.join(map(repr, self)))

    def __iter__(self):
        for ele in self.content:
            yield ele

    def parse(self, stub):
        for elem in list(stub):
            if elem.tag not in unspported_tags:
                self.content.append(html_classes[elem.tag](elem))

    def get_structure(self, main_sections=False):
        if main_sections is True:
            sections = [ele.title for ele in self if isinstance(ele, Section)]
        else:
            sections = [(ele.title, ele.get_titles()) for ele in self if isinstance(ele, Section)]
        return sections

    def get_flat(self, sections=None, text=False):
        bd = []
        for ele in self:
            if sections is None or (isinstance(sections, list) and ele.title in sections):
                if text is False or not(isinstance(ele, (Figure, ReferencedContent))):
                    bd.extend(ele.get_content(flatten=True))
        return bd

    def get_nested(self, main_sections=False, sections=None):
        if main_sections is True:
            secs = [(ele.title, " ".join(ele.get_content(flatten=True))) for ele in self]
        else:
            secs = [(ele.title, ele.get_content()) for ele in self]

        if sections is not None:
            secs = [e for e in secs if e[0] in sections]

        return secs


class Article(object):
    def __init__(self, xml=None):
        self.type = None
        self.front = None
        self.body = None
        self.back = None
        self.xml = None
        Paragraph.i = 1

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

        self.xml = xml_tree
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

    # TODO: implement clean option
    def get_flat_text(self, sections=None, clean=False):
        return self.body.get_flat(sections=sections, text=True) if self.body is not None else None

    def get_flat_content(self, sections=None):
        return self.body.get_flat(sections=sections) if self.body is not None else None

    # TODO: implement this function
    def get_nested_text(self, sections=None):
        pass

    def get_nested_content(self, main_sections=False, sections=None):
        return self.body.get_nested(main_sections=main_sections, sections=sections) if self.body is not None else None

    def get_body_structure(self, main_sections=False):
        return self.body.get_structure(main_sections=main_sections) if self.body is not None else None

    def get_authors(self):
        return self.front.article_meta.authors


# TODO: add support for tags
unspported_tags = {"disp-quote", "ref-list", "def-list", "verse-group", "array"}

html_classes = {
    "sec": Section,
    "p": Paragraph,
    "fig": Figure,
    "graphic": ReferencedContent,
    "media": ReferencedContent,
    "disp-formula": ReferencedContent,
    "table": Table,
    "table-wrap": TableWrap,
    "table-wrap-group": TableGroup,
    "supplementary-material": NestedContainer,
    "boxed-text": NestedContainer,
    "list": List
}
