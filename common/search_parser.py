import pyparsing as pp


class SearchParser:
    __COLON, __EQUAL = map(pp.Literal, ":=")
    __word_strict = pp.Regex(r"[^\s'\":=]+")
    __sglQuotedString = pp.QuotedString("'", escChar="\\")
    __dblQuotedString = pp.QuotedString('"', escChar="\\")
    __word = __sglQuotedString | __dblQuotedString | __word_strict

    __filtr_name = __word_strict + __COLON | __word_strict + __EQUAL
    __filtr = pp.Group(__filtr_name + __word)
    __query_patt = pp.Dict(__filtr) | __word

    __expr = __query_patt() * (1,)

    def parse_query(self, query: str):
        parsed_query = self.__query_patt.parseString(query)
        terms = filter(lambda t: isinstance(t, str), parsed_query.asList())
        filters = parsed_query.asDict()

        return terms, filters


if __name__ == "__main__":
    tests = u"""\
hello world
"hello world"
hello world is:me
hello role:Editor world
hello title:"Malice in the Palice" world
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
