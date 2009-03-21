#!/usr/bin/python

foo = may_match(r'regex')
if foo:
    bar = must_match(r'regex','error message')
    baz = must_match(r'regex','error message')
    data = foo + bar # baz is thrown away

