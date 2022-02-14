#!/usr/bin/env python3
import sys
import os
import operator
import copy
import re
import datetime
from functools import singledispatchmethod
from webencodings import ascii_lower


import tinycss2, cssselect2
import inflect
import dmark

# TODO: handle better than just global state?
content = matcher = None
SORT_KEY = operator.itemgetter(0, 1)
ORDERLY = operator.attrgetter("style_order", "content_order")
p = inflect.engine()


class StyleMatcher(cssselect2.Matcher):
    """
    Override to implement our own ~css

    TODO:
    - sure, but say more :)
    - I'm having a general problem with finding/remembering to set up closures that
      properly hold durable references to these other lists/objects. Would be nice
      to either ensure this is done with rigor, or design around the need...
    """

    @classmethod
    def build_value_evaluator(cls, tokens, join=True):
        values = [value for value in cls.token_to_values(tokens)]

        evaluator = None
        if join:

            def evaluator(element, values=values):
                return "".join([str(val(element)) for val in values])

        else:

            def evaluator(element, values=values):
                return [val(element) for val in values]

        return evaluator

    def match(self, element):
        """Match selectors against the given element.
        :param element:
            An :class:`ElementWrapper`.
        :returns:
            A list of the payload objects associated to selectors that match
            element, in order of lowest to highest
            :attr:`compiler.CompiledSelector` specificity and in order of
            addition with :meth:`add_selector` among selectors of equal
            specificity.
        """
        relevant_selectors = []

        if element.id is not None:
            relevant_selectors.append(self.id_selectors.get(element.id, []))

        for class_name in element.classes:
            relevant_selectors.append(self.class_selectors.get(class_name, []))

        relevant_selectors.append(
            self.lower_local_name_selectors.get(ascii_lower(element.local_name), [])
        )
        relevant_selectors.append(
            self.namespace_selectors.get(element.namespace_url, [])
        )

        if "lang" in element.etree_element.attrib:
            relevant_selectors.append(self.lang_attr_selectors)

        relevant_selectors.append(self.other_selectors)

        results = [
            (specificity, order, pseudo, payload)
            for selector_list in relevant_selectors
            for test, specificity, order, pseudo, payload in selector_list
            if not isinstance(element, str) and test(element)
        ]

        results.sort(key=SORT_KEY)
        return results

    @classmethod
    def token_to_values(cls, tokens):
        """
        TODO: sniff for a refactor that makes these all easier to add and less noisy
        """
        for token in tokens:
            if isinstance(token, tinycss2.ast.NumberToken):
                out = token.int_value if token.int_value is not None else token.value

                def numeric(el, sigh=str(out)):
                    return sigh

                yield numeric
            elif isinstance(
                token, (tinycss2.ast.WhitespaceToken, tinycss2.ast.LiteralToken)
            ):
                pass
            elif isinstance(token, tinycss2.ast.FunctionBlock):
                tok = token
                evaluators = cls.build_value_evaluator(tok.arguments, join=False)
                if token.name == "attr":

                    def fetch_attr(el, tok=token):
                        lookfor = " ".join([x.serialize() for x in tok.arguments])
                        out = getattr(el, lookfor, el.attributes.get(lookfor, "")) or ""
                        return out

                    yield fetch_attr
                elif token.name == "uppercase":
                    tok = token  # TODO: not yet, but AFAIK all but the first of these are droppable

                    def case_the_joint(el, callables=evaluators):
                        return str.upper("".join(callables(el)))

                    yield case_the_joint
                elif token.name == "lowercase":
                    tok = token

                    def case_the_joint(el, callables=evaluators):
                        return str.lower("".join(callables(el)))

                    yield case_the_joint
                elif token.name == "titlecase":
                    tok = token

                    def case_the_joint(el, callables=evaluators):
                        return str.title("".join(callables(el)))

                    yield case_the_joint
                elif token.name == "sentencecase":
                    tok = token

                    def case_the_joint(el, callables=evaluators):
                        return str.capitalize("".join(callables(el)))

                    yield case_the_joint
                # TODO: any other case ops?
                elif token.name == "slice":
                    tok = token

                    def snip_snip(el, callables=evaluators):
                        start = 0
                        stop = None
                        try:
                            text, _start, _stop = callables(el)
                            start = int(_start)
                            stop = int(_stop)
                        except Exception as e:
                            # TODO this obviously won't bite me :P
                            pass
                        return text[start:stop]

                    yield snip_snip
                elif token.name == "nl":
                    # TODO: I think maybe I backed off of this idea; kill if so
                    tok = token

                    def newline(el):
                        return "\n"

                    yield newline
                elif token.name == "children":
                    tok = token

                    def number_of_children(el):
                        return len(el.children) if el.children else 0

                    yield number_of_children
                elif token.name == "content":
                    tok = token

                    def content_string(el):
                        # TODO: I don't really know what the correct format
                        # for this will be. space-sep is JUST a wild guess
                        return "".join(
                            space_cadet(
                                WordsWurst.handle_children(el, dict({}, depth=11))
                            )
                        )
                        return " ".join(el.children) if el.children else ""

                    yield content_string
                elif token.name == "inflect":
                    """
                    TODO: ponder/doc: we may have to escape some parts
                    of these format strings in dmark. They're fine in the CSS...

                    not loving it:
                    %inflect{Hair plural('is', {0%}) {0%} directive plural('form', {0%})}:
                    """

                    def processor(el, callables=evaluators):
                        args = callables(el)

                        return p.inflect(args[0].format(*args[1:]))

                    yield processor
                elif token.name == "today":
                    """
                    TODO: at some point there's a line where these get too idiomatic
                    I think now() and today() are on the right side of it, but idk...
                    """

                    def today(el, callables=evaluators):
                        return datetime.date.today().strftime("".join(callables(el)))

                    yield today
                elif token.name == "shortform":
                    # TODO: verify this is in use and can't be written out? it's obviously
                    # hardcoding format; else, look at pulling it out into an extension
                    # layer on top of wordswurst
                    tok = token

                    def content_string(el):
                        # TODO: I don't really know what the correct format
                        # for this will be. space-sep is JUST a wild guess
                        out = " ".join(el.children) if el.children else ""
                        return ".Ar {:} Ns {:}".format(out[0], out[1:])

                    yield content_string
                else:
                    raise Exception(
                        "unhandled css function '{:}' at line {:}:{:}".format(
                            token.name,
                            token.source_line,
                            token.source_column,
                        ),
                        token,
                    )
            elif isinstance(token, tinycss2.ast.ParseError):
                raise Exception(
                    "{:} at {:}:{:}: {:}".format(
                        token.kind,
                        token.source_line,
                        token.source_column,
                        token.message,
                    )
                )
            else:

                def mystery_meat(element, tok=token):
                    return tok.value

                yield mystery_meat

    def __init__(self, css):
        cssselect2.Matcher.__init__(self)
        rules = tinycss2.parse_stylesheet_bytes(
            css,
            skip_whitespace=True,
            skip_comments=True,
        )[0]

        for rule in rules:
            for selector in cssselect2.compile_selector_list(rule.prelude):
                self.add_selector(
                    selector,
                    {
                        obj.name: self.build_value_evaluator(obj.value)
                        for obj in tinycss2.parse_declaration_list(
                            rule.content, skip_whitespace=True
                        )
                        if obj.type == "declaration"
                    },
                )


def space_camp(nodes):
    for i, node in enumerate(nodes):
        if node:
            node.content_order = i
            yield node


def space_cadet(nodes):
    """
    Lay out a sequence of nodes as a sequence of strings.

    Yield trimmed node text and appropriate boundary
    whitespace strings.
    """
    nodes = sorted(space_camp(nodes), key=ORDERLY)
    if len(nodes):
        prev = cur = None
        cur = nodes.pop(0)
        yield cur.left(None)

        while len(nodes):
            prev = cur
            cur = nodes.pop(0)
            bound = prev.right(cur)
            yield prev.text
            yield bound

        bound = cur.right(None)
        yield cur.text
        yield bound


class OutputForm(object):
    text = style = depth = None
    space = strippable = lstrippable = rstrippable = None
    content_order = None
    style_order = 0

    def __init__(self, style, text, depth):
        self.text = text
        self.style = style
        if "strippable" in style:
            self.strippable = style["strippable"]
        if "lstrippable" in style:
            self.lstrippable = style["lstrippable"]
        if "rstrippable" in style:
            self.rstrippable = style["rstrippable"]
        if "space" in style:
            self.space = style["space"] * style.get("spacen", 1)
        if "order" in style:
            self.style_order = int(style["order"])
        self.depth = depth

    def __repr__(self):
        return "<{:} == {:}>".format(self.__class__.__name__, repr(self.text))

    def rstrip(self):
        self.text = self.text.rstrip(self.rstrippable or self.strippable)

    def rstrip_other(self, other):
        if other and hasattr(other, "rstrip"):
            return other.rstrip()

    def lstrip(self):
        self.text = self.text.lstrip(self.lstrippable or self.strippable)

    def lstrip_other(self, other):
        if other and hasattr(other, "lstrip"):
            return other.lstrip()

    # singledispatched per class later
    def left(self, other):
        raise NotImplementedError("I don't know this", type(other))

    def _left(self, other):
        self.lstrip()
        self.rstrip_other(other)
        return self.space

    def right(self, other):
        raise NotImplementedError("I don't know this", type(other))

    def _right_dominated(self, other):
        # defer to the higher-order unit
        return other.left(self)

    def _right_dominating(self, other):
        self.lstrip_other(other)
        self.rstrip()
        return self.space


class Char(OutputForm):
    space = ""

    def _right_dominating(self, other):
        # override; I think only strip char when dominated
        return self.space

    def __bool__(self):
        # filterable if all-space
        try:
            return len(self.text.strip(" ")) > 0
        except:
            raise ValueError(self, self.text)


class Word(OutputForm):
    space = " "


class Line(OutputForm):
    space = "\n"


class Block(OutputForm):
    space = "\n\n"


OUTPUT_FORMS = {
    "char": Char,
    "word": Word,
    "line": Line,
    "block": Block,
}


def form_from_style(style, content, depth):
    try:
        form = OUTPUT_FORMS[style.get("display", "block")]
        return form(style, content, depth)
    except KeyError as e:
        raise Exception(
            "I only recognize the following display values: %s"
            % ", ".join(OUTPUT_FORMS.keys())
        ) from e


"""
Set up single-dispatch methods on all of these OutputForm classes for
all of the other OutputForm classes.
"""
for form in OUTPUT_FORMS.values():
    dominating = True
    form.left = singledispatchmethod(form.left)
    form.right = singledispatchmethod(form.right)
    for typ in (type(None), str, Char, Word, Line, Block):
        if dominating:
            form.left.register(typ, form._left)
            form.right.register(typ, form._right_dominating)
        else:
            form.right.register(typ, form._right_dominated)

        if typ == form:
            dominating = False


class WordsWurst(dmark.Translator):
    @classmethod
    def handle_string(cls, string, context):
        depth = context.get("depth", 1)
        return Char({}, string, depth)

    @classmethod
    def handle_styled(cls, element, context, depth):
        output = []
        style = {}
        content = ""
        matches = matcher.match(element)

        if matches:
            for match in matches:
                """
                specificity is a 3-tuple of unknown values
                    0 = number of ID selectors
                    1 = number of class selectors, attributes selectors, and pseudo-classes
                    2 = number of type selectors and pseudo-elements
                order probably reflects add_selector order
                sort should be 0 > 1 > 2 > order
                """
                specificity, order, pseudo, declarations = match

                declarations = {k: v(element) for k, v in declarations.items()}
                if pseudo:
                    if pseudo not in style:
                        style[pseudo] = declarations.copy()
                    else:
                        style[pseudo].update(declarations)
                else:
                    style.update(declarations)

        if "display" in style and style["display"] == "none":
            return Char({}, "", depth)

        if "before" in element.attributes or (
            "before" in style and "content" in style["before"]
        ):
            output.append(
                form_from_style(
                    style["before"],
                    element.attributes["before"]
                    if "before" in element.attributes
                    else style["before"]["content"],
                    depth,
                )
            )

        content = (
            style["content"]
            if "content" in style
            else "".join(
                space_cadet(
                    cls.handle_children(element, dict(context, depth=depth + 1))
                )
            )
        )

        output.append(Char({}, content, depth))

        if "after" in element.attributes or (
            "after" in style and "content" in style["after"]
        ):
            output.append(
                form_from_style(
                    style["after"],
                    element.attributes["after"]
                    if "after" in element.attributes
                    else style["after"]["content"],
                    depth,
                )
            )

        return form_from_style(style, "".join(space_cadet(output)), depth)

    @classmethod
    def handle_compose(cls, element, context, depth):
        global content, matcher
        content_path, style_path = element.children.pop(0).split()
        with open(content_path, "r") as cd, open(style_path, "rb") as sd:
            content_file = cd.read()
            style_file = sd.read()

        content = Parser(content_file).parse()
        for item in content:
            item.associate()

        matcher = StyleMatcher(style_file)
        return "".join(
            space_cadet(cls.handle_children(element, dict(context, depth=depth + 1)))
        )

    @classmethod
    def handle_insert(cls, element, context, depth):
        content_path = element.children.pop(0)
        with open(content_path, "r") as cd:
            element.children = cd.readlines()
            return cls.handle_styled(element, context, depth=depth + 1)

    @classmethod
    def handle_select(cls, element, context, depth):
        global content, matcher
        selected = []
        query = element.children.pop(0)
        for part in content:
            results = part.query_all(query)
            for result in results:
                result = copy.deepcopy(result)
                # TODO: do id, too? or only if it doesn't clash?
                result.classes.update(element.classes)

                selected.append(
                    cls.handle_element(result, dict(context, depth=depth + 1))
                )
        if selected:
            # strip to keep selected nodes in the ~envelope
            # of the original select directive.
            return Char({}, "".join(space_cadet(selected)).strip(), depth)
        else:
            raise Exception("[[bad select: {:}]]".format(query), element)

    @classmethod
    def handle_element(cls, element, context):
        depth = context.get("depth", 1)
        if element.name == "compose":
            return cls.handle_compose(element, context, depth)
        elif element.name == "select":
            return cls.handle_select(element, context, depth)
        elif element.name == "insert":
            return cls.handle_insert(element, context, depth)
        else:
            return cls.handle_styled(element, context, depth)


class Element(dmark.Element, cssselect2.ElementWrapper):
    # TODO: better document where these all come from
    # and who they are for
    id = classes = None
    tag = local_name = parent = index = in_html_document = None
    etree_element = etree_siblings = transport_content_language = None
    _id_regex = re.compile(r"(?=[.#])")

    @classmethod
    def parse_name(cls, text):
        identifiers = cls._id_regex.split(text)
        element = identifiers.pop(0)
        if not len(identifiers):
            return element, None, set()
        else:
            identifier = None
            classes = set()
            for each in identifiers:
                if each.startswith("."):
                    classes.add(each[1:])
                elif identifier is None and each.startswith("#"):
                    identifier = each[1:]
            return element, identifier, classes

    def __init__(self, name, attributes, children):
        el_name, self.id, self.classes = self.parse_name(name)
        self.tag = self.local_name = self.name = el_name
        self.local_name = el_name
        self.attrib = self.attributes = attributes
        self.children = children
        self.etree_element = self
        self.in_html_document = False
        self.etree_siblings = []

    def __repr__(self):
        return "Element([{index}]{name}{id}{classes}, {attributes}{children})".format(
            index=self.index,
            id="#" + self.id if self.id else "",
            classes="." + ".".join(self.classes) if len(self.classes) else "",
            name=self.name,
            attributes=self._repr_attributes(),
            children=repr(self.children),
        )

    def get(self, key):
        return self.attributes.get(key, None)

    def associate(self):
        """
        TODO: Would prefer to do this without our own full tree visit,
        whether that's at __init__, or via an add_child hook, or
        via a children-added callback (but d-mark's parsing
        process means this info isn't available at init, and the
        latter mechanisms don't exist yet)
        """
        elements_only_dot_com = [x for x in self.children if isinstance(x, Element)]
        for i, child in enumerate(self.children):
            if not isinstance(child, Element):
                continue
            if i > 0:
                child.previous = self.children[i - 1]

            child.parent = self
            child.etree_siblings = elements_only_dot_com
            child.index = i
            child.associate()

    def iter_children(self):
        """
        override ElementWrapper.iter_children
        to use d-mark Element.children
        """
        for child in self.children:
            yield child

    def iter_subtree(self):
        """
        override ElementWrapper.iter_subtree
        to handle non-Elements such as str
        """
        stack = [iter([self])]
        while stack:
            element = next(stack[-1], None)
            if element is None:
                stack.pop()
            elif not isinstance(element, Element):
                continue
            else:
                yield element
                stack.append(element.iter_children())

    def etree_children(self):
        """
        override ElementWrapper.etree_children
        to use d-mark Element.children
        """
        return self.children


class Str(str):
    index = tag = None

    def __new__(cls, text):
        self = str.__new__(cls, text)
        return self

    def __init__(self, text):
        pass


class Parser(dmark.Parser):
    IDENTIFIER_CHARS = dmark.Parser.IDENTIFIER_CHARS + ".#"

    def read_string(self):
        res = super(Parser, self).read_string()
        # return res
        return Str(res)


dmark.Element = Element  # monkeypatch


def main():
    for arg in sys.argv[1:]:
        with open(arg, "r") as fd:
            # treat paths as source-relative
            os.chdir(os.path.dirname(os.path.abspath(fd.name)))
            idkmybffjill = fd.read()
        tree = Parser(idkmybffjill).parse()
        for item in tree:
            item.associate()
        # print(tree)
        # TODO: not certain about lstrip here
        print(WordsWurst.translate(tree).lstrip())
