#!/usr/bin/env python

"""
Converts PDF text content (though not images containing text) to plain text, html, xml or "tags".
"""
import argparse
import logging
import sys
from pdfmajor.converters import convert_file

def make_argparser():
    parser = argparse.ArgumentParser(description=__doc__, add_help=True)
    parser.add_argument("files", type=str, default=None, nargs="+", help="File to process.")
    parser.add_argument("-d", "--debug", default=False, action="store_true", help="Debug output.")
    parser.add_argument("-p", "--pagenos", type=str, help="Comma-separated list of page numbers to parse. Included for legacy applications, use --page-numbers for more idiomatic argument entry.")
    parser.add_argument("-m", "--maxpages", type=int, default=0, help="Maximum pages to parse")
    parser.add_argument("-P", "--password", type=str, default=None, help="Decryption password for PDF")
    parser.add_argument("-c", "--codec", type=str, default="utf-8", help="Text encoding")
    parser.add_argument("-t", "--output-type", type=str, default="text", help="Output type: text|html|xml|tag (default is text)")
    parser.add_argument("-o", "--output-file", type=str, default="-", help="Output file (default \"-\" is stdout)")
    parser.add_argument("-O", "--output-dir", default=None, help="Output directory for images")
    parser.add_argument("-C", "--disable-caching", default=False, action="store_true", help="Disable caching")
    return parser


# main


def main(args=None):

    argparser = make_argparser()
    parsed_args = argparser.parse_args(args=args)

    func_args = {
        'maxpages': parsed_args.maxpages, 
        'password': parsed_args.password, 
        'codec': parsed_args.codec, 
        'caching': not parsed_args.disable_caching,
    }

    if parsed_args.pagenos:
        func_args['pagenos'] = set([int(x)-1 for x in parsed_args.pagenos.split(",")])

    if parsed_args.output_type == "text" and parsed_args.output_file != "-":
        for override, alttype in (  (".htm",  "html"),
                                    (".html", "html"),
                                    (".xml",  "xml" ),
                                    (".tag",  "tag" ) ):
            if parsed_args.output_file.endswith(override):
                func_args['out_type'] = alttype

    if len(parsed_args.files) == 1:
        if parsed_args.output_file != "-":
            func_args['output_file'] = open(parsed_args.output_file, "wb")
        with open(parsed_args.files[0], 'rb') as input_file:
            convert_file(
                input_file,
                **func_args
            )
    else:
        print("Multiple files not supported yet.")
        return 1
    return 0


if __name__ == '__main__': 
    sys.exit(main())
