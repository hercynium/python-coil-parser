#!/usr/bin/env python

import sys;
import re;

class CoilParseError(Exception): pass

#    def __init__( self, msg, text_pos ):
#        self.msg = msg
#        self.pos = text_pos
#
#    def __str__( self ):
#        return repr("Error: " + self.msg + " at char %s", self.pos )


class CoilParser:

    def __init__( self, coil_text ):
        self.coil_text = coil_text
        self.text_pos = 0


    # this regex and method will move the text_pos past 
    # any whitespace or comments
    skip_re = re.compile(
        r'''(?: \s | [#][^\n]* )*''',
        re.S | re.M | re.X
    )
    def skip_ws_and_comments( self ):
        match = self.skip_re.match( self.coil_text, self.text_pos )
        if match:
            self.text_pos = match.end()
        return {}


    # The regexes and method below demonstrate a matching function that 
    # commits when the text begins to match and therefore raises an 
    # exception if the rest of the match ultimately fails.
    # NOTE: now it does *two* commits - I don't know if that's good or bad
    # NOTE: I'm sure this would all be cleaner as a generic solution, 
    # generating the match method dynamically... but how best to do it?
    name_begin_re = re.compile( 
        r'''
            ( [@a-zA-Z] ) # an element name begins with...
        ''', 
        re.X 
    )
    name_end_re = re.compile(
        r'''
            \s* [:] # an element name should always be followed by a colon
        ''',
        re.X
    )
    name_rest_re = re.compile(
        r'''                         # the rest of an element name...
        (
            (?: 
                [a-zA-Z0-9]          # can contain letters and numbers
              |                      # OR
                (?:                  # can contain other these other
                    ([_.-]) (?!\2)   # chrarcters, but never two in a row.
                )
                [a-zA-Z0-9]          # and always followed by a letter or num
            )*                       # match as much as possible...
        )                            # capture as $1
        (?! [a-zA-Z0-9_.-] )         # make sure it's the end of the word
        ''',
        re.X
    )
    def match_name( self ):
        begin_match = self.name_begin_re.match( self.coil_text, self.text_pos )
        if not begin_match:
            return {}

        rest_match = self.name_rest_re.match( self.coil_text, begin_match.end() )
        if not rest_match:
            raise CoilParseError ({
                'message': 'Badly-formed element name', 
                'pos': self.text_pos 
            })

        self.text_pos = rest_match.end()
        name = begin_match.group(1) + rest_match.group(1)

        end_match = self.name_end_re.match( self.coil_text, rest_match.end() )
        if not end_match:
            err_msg = \
                'Could not find the required ":" after element name [%s]' \
                % name
            raise CoilParseError ({ 'message': err_msg, 'pos': self.text_pos })

        self.text_pos = end_match.end()
        return { 'name': name }


    def current_pos( self ):
        return self.text_pos


if __name__ == '__main__':
    filename = sys.argv[1]
    coil_text = open( filename ).read()

    parser = CoilParser( coil_text )

    text_pos = 0

    parser.skip_ws_and_comments()

    match = parser.match_name()

    if match:
        name = match['name']
        print "element name matched: %s" % name

    text_pos = parser.current_pos()
    print "current pos: %s" % text_pos
    print "next text: %s" % coil_text[text_pos:]


