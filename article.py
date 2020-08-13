import xml.etree.ElementTree as ElementTree
import warnings
from countries import countries
import re

class BaseElement(object):
    def __init__(self, stub):
        self.xml = stub
        self.graph = None
        self.set_graph()

    def set_graph(self):
        graph = []
        if self.xml:
            for i, elem in enumerate(list(self.xml), 1):
                graph.append((self.xml.tag, elem.tag))
            self.graph = graph



class BaseBodyElement(BaseElement):
    def __init__(self, stub):
        super(BaseBodyElement, self).__init__(stub)
        self.label = None
        self.caption = None
        self.title = None

        # TODO: add support for tags
        self.unspported_tags = {"ref-list", "def-list", "verse-group", "array", 'inline-formula', 'email'}
        self.emphasis_elements = {'bold', 'italic', 'monospace', 'overline',
                                  'roman', 'sans-serif', 'sc', 'strike', 'underline', 'sup', 'sub'}

        self.html_classes = {
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
            "boxed-text": SeparatedContent,
            'named-content': SeparatedContent,
            'speech': SeparatedContent,
            'speaker': Name,
            "list": List,
            'xref': ReferencedContent,
            'ext-link': ReferencedContent,
            'inline-graphic': ReferencedContent,
            'disp-quotsing alle': NestedContainer,
            'statement': NestedContainer,
            'related-article': Front
        }

    def name(self):
        return self.__class__.__name__

    def set_descriptive_attributes(self, stub):
        label = stub.find("label")
        if label is not None:
            self.label = label.text
            stub.remove(label)

        caption = stub.find("caption")
        if caption is not None:
            self.caption = "".join(caption.itertext())
            stub.remove(caption)

        title = stub.find("title")
        if title is not None:
            self.title = "".join(title.itertext())
            stub.remove(title)

        if self.title is None:
            self.title = ""
        if self.label is not None:
            self.title += self.label
        if self.caption is not None:
            self.title += self.caption
        if not self.title:
            self.title = self.name()


class List(BaseBodyElement):
    def __init__(self, stub=None):
        super(List, self).__init__(stub)
        self.elements = None
        self.title = None

        if stub is not None:
            self.parse(stub)

    def __iter__(self):
        for e in self.elements:
            yield e

    def __repr__(self):
        return "List({})".format(self.elements)

    def parse(self, stub):
        self.set_descriptive_attributes(stub)

        self.elements = []
        for item in stub.iter(tag="list-item"):
            self.elements.append("".join(item.itertext()))

    def get_content(self, **kwargs):
        text = kwargs.get("text")
        flatten = kwargs.get('flatten')

        content = ';'.join(self.elements) if text is True else self
        return [content] if flatten is True else content


class Text(object):
    def __init__(self, text, title=None):
        self.text = text
        self.title = title if title is not None else self.name()

    def name(self):
        return self.__class__.__name__

    def __repr__(self):
        return 'Text({})'.format(self.text)

    def get_content(self, **kwargs):
        text = kwargs.get('text')
        flatten = kwargs.get('flatten')

        content = self.text if text is True else self
        return [content] if flatten is True else content


class NestedContainer(BaseBodyElement):
    def __init__(self, stub=None):
        super(NestedContainer, self).__init__(stub)
        self.content = None

        if stub is not None:
            self.parse(stub)

    def name(self):
        return self.__class__.__name__

    def __repr__(self):
        return 'NestedContainer({})'.format(', '.join(map(repr, self)))

    def __iter__(self):
        if self.content:
            for ele in self.content:
                yield ele

    def parse(self, stub):
        self.set_descriptive_attributes(stub)

        self.content = []
        if stub.text:
            self.content.append(Text(stub.text))

        for ele in list(stub):
            if ele.tag in self.emphasis_elements:
                self.content.append(Text(ele.text))
            elif ele.tag not in self.unspported_tags:
                self.content.append(self.html_classes[ele.tag](ele))
            else:
                # print(ele.tag, ElementTree.tostring(ele))
                warnings.warn('{} is not supported'.format(ele.tag))

            if ele.tail:
                self.content.append(Text(ele.tail))

    def get_content(self, flatten=False, text=False):
        content = []
        for ele in self.content:
            print(ele)
            if flatten is True:
                content.extend(ele.get_content(flatten=flatten, text=text))
            else:
                # title = ele.title if text is True else ele.name()
                # title = ele.title if ele.title else ele.name()
                content.append((ele.title, ele.get_content(flatten=flatten, text=text))
                               if isinstance(ele, NestedContainer) else ele.get_content(flatten=flatten, text=text))
        return content


class SeparatedContent(NestedContainer):
    def __init__(self, stub):
        super(SeparatedContent, self).__init__(stub)


class ReferencedContent(BaseBodyElement):
    def __init__(self, stub=None):
        super(ReferencedContent, self).__init__(stub)
        self.obj_id = None
        self.href = None
        self.text = None

        if stub is not None:
            self.parse(stub)

    def __repr__(self):
        return "ReferencedContent(href={}, text={})".format(self.href, self.text)

    def name(self):
        return self.__class__.__name__

    def parse(self, stub):
        self.set_descriptive_attributes(stub)
        self.text = stub.text if stub.text else ''
        self.href = stub.get("ns0:href")

    def get_content(self, **kwargs):
        text = kwargs.get("text")
        flatten = kwargs.get('flatten')

        content = self.text if text is True else self
        return [content] if flatten is True else content


class Figure(BaseBodyElement):
    """
    Figure should be a NestedContainer as it can contain any number of <p>.
    However in order to make it selectable by its type (Article._get_elements_by_type) it needs to
    be a leaf element. It is also common sense that, while in principle possible, a <fig> should
    not contain arbitrarily nested elements but only a caption.

    In order to cope with this the attribute Figure.text contains any text that exists
    outside of caption and label. This is however a sub-optimal solution because any potential
    structured element (e.g. <table>) inside <fig> would not be parsed correctly and its content
    would be reported de-structured.
    """
    def __init__(self, stub=None):
        super(Figure, self).__init__(stub)
        self.content = None
        self.namespace = None
        self.text = None

        if stub is not None:
            self.parse(stub)

    def __repr__(self):
        return "Figure(label={}, caption={}, text={})".format(self.content, self.caption, self.text)

    def parse(self, stub):
        self.set_descriptive_attributes(stub)
        text = ''.join(stub.itertext())
        self.text = text if text else ''

    def get_content(self, **kwargs):
        text = kwargs.get("text")
        flatten = kwargs.get('flatten')

        content = self.text if text is True else self
        return [content] if flatten is True else content


class TableGroup(NestedContainer):
    def __init__(self, stub=None):
        super(TableGroup, self).__init__(stub)
        self.content = None

        if stub is not None:
            self.parse(stub)

    def __repr__(self):
        return "TableGroup(title={}, caption={} content={})".format(self.title, self.caption, self.content)


class TableWrap(NestedContainer):
    def __init__(self, stub=None):
        super(TableWrap, self).__init__(stub)
        self.content = None
        self.footer = None

        if stub is not None:
            self.parse(stub)

    def __repr__(self):
        return "TableWrap(title={}, caption={} content={})".format(self.title, self.caption, self.content)

    def parse(self, stub):
        self.set_descriptive_attributes(stub)

        footer = stub.find("table-wrap-foot")
        self.footer = footer.text if footer else None

        self.content = []
        for table in stub.findall("table"):
            self.content.append(Table(table))


class Table(BaseElement):
    i = 1

    def __init__(self, stub=None):
        super(Table, self).__init__(stub)
        self.title = "Table{}".format(self.i)
        self.rows = None
        Table.i += 1

        if stub is not None:
            self.parse(stub)

    def __repr__(self):
        return "Table(shape=({}, {}))".format(len(self.rows), len(self.rows[0]))

    def name(self):
        return self.__class__.__name__

    def tabulate(self):
        rpr = []

        for row in self.rows:
            col_widths = map(lambda t: len(max(t, key=len)), zip(*self.rows))
            rpr.append("  ".join("{:<{r}}".format(cell, r=align) for cell, align in zip(row, col_widths)))
        return '\n'.join(rpr)

    def parse(self, stub):
        # parse caption
        # self.title = stub.get("id")

        # parse table
        self.rows = []
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
                try:
                    colspan = int(colspan) if colspan else 1
                except ValueError:
                    warnings.warn("html contained an error. Table {} will not be "
                                  "faithful to the original".format(self.title))
                    colspan = 1
                row.extend([''.join(cell_text)]*colspan)

                cell_index += colspan
            self.rows.append(row)

    def get_content(self, **kwargs):
        text = kwargs.get("text")
        return [self.tabulate()] if text is True else [self]


class Name(BaseElement):
    def __init__(self, stub=None):
        super(Name, self).__init__(stub)
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


class Author(BaseElement):
    def __init__(self, stub=None, affs=None):
        super(Author, self).__init__(stub)
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
        self.affiliations = self.affiliations if self.affiliations else list(affs.values())


class Metadata(BaseElement):
    def __init__(self, stub=None):
        super(Metadata, self).__init__(stub)
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

        author_tags = stub.findall("contrib-group/contrib[@contrib-type='author']")
        affils_tags = stub.findall("contrib-group/aff")

        if not affils_tags:
            affils_tags = stub.findall('aff')
            # if affils_tags:
            # # affils_tags = [affils_tags for _ in author_tags]

        self.authors = self._parse_authors(author_tags, affils_tags)

    @staticmethod
    def _parse_authors(contrib_group, aff):
        authors = []
        affiliations = {}

        for i, affil in enumerate(aff):
            aff = Affiliation(affil)
            if aff.aid is not None:
                affiliations[aff.aid] = aff
            else:
                affiliations[i] = aff

        for contrib in contrib_group:
            author = Author(contrib, affiliations)
            authors.append(author)

        return authors


class Affiliation(BaseElement):
    def __init__(self, stub=None):
        super(Affiliation, self).__init__(stub)
        self.institution = None
        self.aid = None

        if stub is not None:
            self.parse(stub)

    def __repr__(self):
        return "Affiliation(id='{}' institution='{}')".format(self.aid, ' '.join(self.institution))

    def parse(self, stub):
        self.aid = stub.get('id')

        inst_wrap = stub.find("institution-wrap")
        inst_wrap = inst_wrap if inst_wrap is not None else stub

        if inst_wrap is not None:
            institution = inst_wrap.findall("institution")
            self.institution = [e.text for e in institution if e is not None] if institution else [inst_wrap.text]

            geo = inst_wrap.tail
            if geo is not None:
                self.institution.append(geo)


class Journal(BaseElement):
    def __init__(self, stub=None):
        super(Journal, self).__init__(stub)
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


class Front(BaseElement):
    def __init__(self, stub=None):
        super(Front, self).__init__(stub)
        self.journal_meta = None
        self.article_meta = None

        if stub is not None:
            self.parse(stub)

    def __iter__(self):
        for ele in [self.journal_meta, self.article_meta]:
            yield ele

    def __repr__(self):
        return "Front({})".format(', '.join(map(repr, self)))

    def parse(self, stub):
        self.journal_meta = Journal(stub.find("journal-meta"))
        self.article_meta = Metadata(stub.find("article-meta"))


class Paragraph(NestedContainer):
    i = 1

    def __init__(self, stub=None):
        super(Paragraph, self).__init__(stub)
        self.title = "Paragraph{}".format(self.i)
        Paragraph.i += 1

    def __repr__(self):
        return "Paragraph(i={}, {})".format(self.i, ', '.join(map(repr, self)))


class Section(NestedContainer):
    def __init__(self, stub=None):
        super(Section, self).__init__(stub)
        self.title = None
        self.content = []

        if stub is not None:
            self.parse(stub)

    def __repr__(self):
        return "\nSection(title='{}', content={})".format(self.title, self.content)

    def __len__(self):
        return len(self.content)

    def get_titles(self):
        return [ele.title for ele in self.content if isinstance(ele, Section)]


class Body(BaseBodyElement):
    def __init__(self, stub=None):
        super(Body, self).__init__(stub)
        self.content = []

        if stub is not None:
            self.parse(stub)

    def __len__(self):
        return len(self.content)

    def __repr__(self):
        return "Body({})".format(', '.join(map(repr, self)))

    def __iter__(self):
        if self.content is not None:
            for ele in self.content:
                yield ele

    def parse(self, stub):
        for elem in list(stub):
            if elem.tag not in self.unspported_tags:
                self.content.append(self.html_classes[elem.tag](elem))

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
                # print(ele.get_content(flatten=True, text=True))
                bd.extend(ele.get_content(flatten=True, text=text))
        return bd

    def get_nested(self, main_sections=False, sections=None, text=False):
        if main_sections is True:
            if text is True:
                secs = [(ele.title, " ".join(ele.get_content(flatten=True, text=text))) for ele in self]
            else:
                secs = [(ele.title, ele.get_content(flatten=True, text=text)) for ele in self]

        else:
            secs = [(ele.title, ele.get_content(text=text)) for ele in self]

        if sections is not None:
            secs = [e for e in secs if e[0] in sections]

        return secs


class Article(BaseElement):
    def __init__(self, xml=None):
        super(Article, self).__init__(xml)
        self.type = None
        self.front = None
        self.body = None
        self.back = None
        self._dict = None
        self._list = None
        Paragraph.i = 1

        if xml is not None:
            self.parse(xml)

    def __repr__(self):
        return 'Article(journal={}, title={})'.format(
            self.front.article_meta.title,
            self.front.journal_meta
        )

    def parse(self, xml):
        if isinstance(xml, str):
            xml_tree = ElementTree.parse(xml)
        elif isinstance(xml, ElementTree.Element):
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
    def get_flat_text(self, sections=None):
        return self.body.get_flat(sections=sections, text=True) if self.body is not None else None

    def get_flat_content(self, sections=None):
        if self._list is None:
            self._list = self.body.get_flat(sections=sections) if self.body is not None else None
        return self._list

    def get_nested_text(self, main_sections=False, sections=None):
        return self.body.get_nested(main_sections=main_sections, sections=sections, text=True) \
            if self.body is not None else None

    def get_nested_content(self, main_sections=False, sections=None):
        return self.body.get_nested(main_sections=main_sections, sections=sections) \
            if self.body is not None else None

    def get_body_structure(self, main_sections=False):
        return self.body.get_structure(main_sections=main_sections) if self.body is not None else None

    def todict(self):
        if self._dict is None:
            self._dict = {ele.title: ele for ele in self.get_flat_content()}
        return self._dict

    def _get_object_by_id(self, obj_id):
        adict = self.todict()
        return adict.get(obj_id)

    # def _flatten(self, container):
    #     for i in container:
    #         if isinstance(i, (list, NestedContainer)):
    #             yield from self._flatten(i)
    #         else:
    #             yield i

    def _get_elements_by_type(self, etype):
        return [ele for ele in self.get_flat_content() if isinstance(ele, etype)]

    def get_tables(self):
        return self._get_elements_by_type(Table)

    def get_figures(self):
        return self._get_elements_by_type(Figure)

    # def get_paragraphs(self):
    #     return self._get_elements_by_type(Paragraph)

    def get_authors(self):
        return self.front.article_meta.authors

    def get_title(self):
        return self.front.article_meta.title

    def get_affiliations(self):
        return [aff for auth_aff in (a.affiliations for a in self.get_authors()) for aff in auth_aff if aff]

    def get_countries(self):
        c = []
        affils = self.get_affiliations()

        if affils:
            p = re.compile('(' + ')|('.join(countries) + ')')
            c = [p.search(' '.join(a.institution)) for a in self.get_affiliations()]
            c = [m.group() for m in c if m]
        return c