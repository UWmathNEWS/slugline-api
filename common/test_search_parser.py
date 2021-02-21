from django.test import TestCase

from common.search_parser import SearchParser
from datetime import date


class SearchParserTestCase(TestCase):
    def setUp(self):
        self.tests = [
            ("hello world", (["hello", "world"], {})),
            ('"hello world"', (["hello world"], {})),
            ("hello world is:me", (["hello", "world"], {"is": [":", "me"]})),
            (
                "hello role:Editor world",
                (["hello", "world"], {"role": [":", "Editor"]}),
            ),
            (
                """hello title_strict="Malice in the Palice" world""",
                (["hello", "world"], {"title_strict": ["=", "Malice in the Palice"]}),
            ),
            (
                u"""hello title:"Malice\\" in the \U0001F600Palice" world is:false""",
                (
                    ["hello", "world"],
                    {
                        "title": [":", u'Malice" in the \U0001F600Palice'],
                        "is": [":", "false"],
                    },
                ),
            ),
            ("is:true", ([], {"is": [":", "true"]})),
            ("me:''", ([], {"me": [":", ""]})),
            ("shiver 'me:' timbers", (["shiver", "me:", "timbers"], {})),
            (u"    \U0001F603    ", ([u"\U0001F603"], {})),
            ("''", ([""], {})),
            (
                "query (2020-01-01,2020-06-01)",
                (["query", "(2020-01-01,2020-06-01)"], {}),
            ),
            (
                "date:(2020-01-01,2020-06-01)",
                ([], {"date": [date(2020, 1, 1), date(2020, 6, 1)]}),
            ),
            ("date:(,2020-06-01)", ([], {"date": [",", date(2020, 6, 1)]})),
            ("date:(2020-01-01,)", ([], {"date": [date(2020, 1, 1), ","]})),
        ]
        self.parser = SearchParser()

    def test_things(self):
        for test in self.tests:
            self.assertEqual(self.parser.parse_query(test[0]), test[1])
