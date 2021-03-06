#!/usr/bin/env python

import sys;
import re;

# The CoilParseError exception should be initalized
# with a dict containing the following elements:
# message: the error message
# pos: the character position at which the error occurred
class CoilParseError(Exception): pass
# TODO: figure out how best to enforce the desired parameters
# while still keeping standard Python exception semantics


class CoilParser:

    def __init__( self, coil_text ):
        self.coil_text = coil_text
        self.text_pos  = 0


    def current_pos( self ):
        return self.text_pos

    
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
        (?! [a-zA-Z0-9_.-] )         # make sure it is the end of the word
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

    ### An attempt at a generic matching method.
    # Description:
    #   Construct a method that combines several provided regular expressions
    #     to match a desired pattern for parsing text.
    # Returns and Raises:
    #   If this match will not work at the current text_pos, because
    #     the begin regex does not match, return {}.
    #   If this match does not work after the begin regex matches, raise
    #     a CoulParseError exception.
    #   If this match succeeds, return the text matched by both begin
    #     and remain concatenated, as the value of {matched: 'matched text'}.
    # Args:
    #   begin is a compiled regex that if matched, signals that
    #     we have the type of data we're looking for.
    #   remain is an re that must match after begin.
    #   remain_err is an error message to include in the CoilParseError
    #     exception that is thrown if remain does not match.
    #   trail is an re that eats up trailing characters that must be
    #     present for the match to be valid but are not part of the
    #     return value.
    def make_matcher( self, begin, remain, remain_err, trail, trail_err ):
        # build a method as a closure and return the method
        def generic_matcher():
            begin_match = begin.match( self.coil_text, self.text_pos )
            if not begin_match:
                return {}

            remain_match = remain.match( self.coil_text, begin_match.end() )
            if not remain_match:
                raise CoilParseError ({
                    'message': remain_err,
                    'pos': self.text_pos 
                })

            self.text_pos = remain_match.end()
            matched_text = begin_match.group(1) + remain_match.group(1)

            trail_match = trail.match( self.coil_text, remain_match.end() )
            if not trail_match:
                err_msg = trail_err + ' after "%s"' % matched_text
                raise CoilParseError ({ 'message': err_msg, 'pos': self.text_pos })

            self.text_pos = trail_match.end()
            return matched_text
        return generic_matcher

    def make_name_matcher( self ):
        return self.make_matcher(
            self.name_begin_re,
            self.name_rest_re,
            'Badly-formed element name',
            self.name_end_re,
            'Could not find the required ":"'
        )

if __name__ == '__main__':
    filename = sys.argv[1]
    coil_text = open( filename ).read()

    parser = CoilParser( coil_text )

    text_pos = 0

    parser.skip_ws_and_comments()
    match_name = parser.make_name_matcher()
    matched_text = match_name()

    if matched_text:
        name = matched_text
        print "element name matched: %s" % name

    text_pos = parser.current_pos()
    print "current pos: %s" % text_pos
    print "next text: %s" % coil_text[text_pos:]


