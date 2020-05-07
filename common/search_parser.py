import pyparsing as pp


class SearchParser:
    def __init__(self):
        COLON, EQUAL = map(pp.Literal, ":=")
        word_strict = pp.Regex(r"[^\s'\":=]+")
        sglQuotedString = pp.QuotedString("'", escChar="\\")
        dblQuotedString = pp.QuotedString('"', escChar="\\")
        word = sglQuotedString | dblQuotedString | word_strict

        filtr_name = word_strict + COLON | word_strict + EQUAL
        filtr = pp.Group(filtr_name + word)
        query_patt = pp.Dict(filtr) | word

        self.__expr = query_patt() * (1,)

    def parse_query(self, query: str):
        parsed_query = self.__expr.parseString(query)
        terms = list(filter(lambda t: isinstance(t, str), parsed_query.asList()))
        filters = parsed_query.asDict()

        return terms, filters


if __name__ == "__main__":
    tests = u"""\
hello world
"hello world"
hello world is:me
hello role:Editor world
hello title_strict:"Malice in the Palice" world
hello title:"Malice\\" in the \U0001F600Palice" world is:false
is:true
me:""
shiver "me:" timbers
    \U0001F603
""
"""
    parser = SearchParser()

    for test in tests.splitlines():
        print(test)
        print(parser.parse_query(test))
        print()
