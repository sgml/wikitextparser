"""Test the tag module."""


import unittest

from regex import compile as regex_compile

import wikitextparser as wtp
from wikitextparser.tag import (
    TAG_FULLMATCH, START_TAG_FINDITER, END_TAG_PATTERN
)


class Tag(unittest.TestCase):

    """Test the Tag module."""

    def test_start_tag_patterns(self):
        self.assertEqual(
            start_tag_finder('<a>').groupdict(),
            {'name': 'a', 'attr': None, 'quote': None,
             'start': '<a>', 'attr_name': None,
             'self_closing': None, 'attr_value': None}
        )
        self.assertEqual(
            start_tag_finder('<a t>').groupdict(),
            {'name': 'a', 'attr': ' t', 'quote': None,
             'start': '<a t>', 'attr_name': 't', 'attr_value': '',
             'self_closing': None}
        )
        self.assertEqual(
            start_tag_finder('<input value=yes>').groupdict(),
            {'name': 'input', 'attr': ' value=yes', 'quote': None,
             'start': '<input value=yes>', 'attr_name': 'value',
             'attr_value': 'yes', 'self_closing': None}
        )
        self.assertEqual(
            start_tag_finder("<input type='checkbox'>").groupdict(),
            {'name': 'input', 'attr': " type='checkbox'", 'quote': "'",
             'start': "<input type='checkbox'>", 'attr_name': 'type',
             'attr_value': 'checkbox', 'self_closing': None}
        )
        # This is not standard HTML5, but could be useful to have.
        # self.assertEqual(
        #     START_TAG_MATCH('<s style=>').groupdict(),
        #     {'name': 's', 'attr': 'style=', 'quote': None,
        #      'start': '<s style=>', 'attr_name': 'style', 'attr_value': ''
        #      'self_closing': None}
        # )
        self.assertEqual(
            start_tag_finder("<t a1=v1 a2=v2>").capturesdict(),
            {'attr_name': ['a1', 'a2'], 'start': ['<t a1=v1 a2=v2>'],
             'attr': [' a1=v1', ' a2=v2'], 'quote': [],
             'attr_value': ['v1', 'v2'], 'self_closing': [], 'name': ['t']}
        )

    def test_end_tag_patterns(self):
        self.assertEqual(
            regex_compile(
                END_TAG_PATTERN % {'name': 'p'}
            ).search('</p>').groupdict(),
            {'end': '</p>'},
        )

    @unittest.expectedFailure
    def test_content_cannot_contain_another_start(self):
        """Checking for such situations is not currently required."""
        self.assertEqual(
            TAG_FULLMATCH.search('<a><a>c</a></a>')[0],
            '<a>c</a>'
        )

    def test_name(self):
        t = wtp.Tag('<t>c</t>')
        self.assertEqual(t.name, 't')
        t.name = 'a'
        self.assertEqual(repr(t), "Tag('<a>c</a>')")
        t = wtp.Tag('<t/>')
        self.assertEqual(t.name, 't')
        t.name = 'n'
        self.assertEqual(t.string, '<n/>')

    def test_contents(self):
        t = wtp.Tag('<t>\nc\n</t>')
        self.assertEqual(t.contents, '\nc\n')
        t.contents = 'n'
        self.assertEqual(t.string, '<t>n</t>')
        t = wtp.Tag('<t></t>')
        self.assertEqual(t.contents, '')
        t.contents = 'n'
        self.assertEqual(t.string, '<t>n</t>')
        t = wtp.Tag('<t/>')
        self.assertEqual(t.contents, '')
        t.contents = 'n'
        self.assertEqual(t.string, '<t>n</t>')

    def test_get_attr_value(self):
        t = wtp.Tag('<t n1=v1 n2=v2 n1=v3 n2=v4>c</t>')
        self.assertEqual(t.get('n1'), 'v3')
        self.assertEqual(t.get_attr('n2'), 'v4')
        t = wtp.Tag('<t a>c</t>')
        self.assertEqual(t.get_attr('a'), '')
        self.assertEqual(t.get_attr('z'), None)

    def test_set_attr_value(self):
        t = wtp.Tag('<t n1=v1 n2=v2 n1=\'v3\'>c</t>')
        t.set('n1', 'v4')
        t.set_attr('n2', 'v5')
        self.assertEqual(t.string, '<t n1=v1 n2="v5" n1="v4">c</t>')
        t.set_attr('id', '1')
        self.assertEqual(t.string, '<t n1=v1 n2="v5" n1="v4" id="1">c</t>')
        t = wtp.Tag('<t>c</t>')
        t.set_attr('n', '')
        self.assertEqual(t.string, '<t n>c</t>')

    def test_attr_deletion(self):
        t = wtp.Tag('<t n1=v1 n1=v333 n2=v22>c</t>')
        t.delete('n1')
        self.assertEqual(t.string, '<t n2=v22>c</t>')

    def test_has_attr(self):
        t = wtp.Tag('<t n1=v1>c</t>')
        self.assertTrue(t.has('n1'))
        self.assertFalse(t.has_attr('n2'))

    def test_parsed_contents(self):
        t = wtp.Tag('<t>c [[w]]</t>')
        c1 = t.parsed_contents
        self.assertEqual(repr(c1), "SubWikiText('c [[w]]')")
        self.assertEqual(c1.wikilinks[0].target, 'w')
        # The new contents object won't create a new span
        c2 = t.parsed_contents
        self.assertEqual(len(c2._type_to_spans['WikiLink']), 1)

    def test_attrs(self):
        t = wtp.Tag('<t n1=v1 n2="v2" n3>c</t>')
        self.assertEqual(t.attrs, {'n1': 'v1', 'n2': 'v2', 'n3': ''})

    def test_contents_contains_tl(self):
        t = wtp.Tag('<b>{{text|t}}</b>')
        self.assertEqual(t.contents, '{{text|t}}')


def start_tag_finder(string):
    """Return the first found match of START_TAG_FINDITER."""
    return next(START_TAG_FINDITER(string))
