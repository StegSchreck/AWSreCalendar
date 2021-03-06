#!/usr/bin/env python
import argparse

from aws_re_invent import AWSreInvent


def main():
    args = parse_args()
    aws_re_invent = AWSreInvent(args)
    aws_re_invent.handle_sessions()
    if args.file is None:
        aws_re_invent.browser_handler.kill()


def parse_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-u", "--username", help="Username for AWS re:Invent page login", required=True)
    argparser.add_argument("-p", "--password", help="Password for AWS re:Invent page login", required=True)
    argparser.add_argument("-d", "--day",
                           help="Filter output to only include this day. "
                                "Possible values include e.g. '2018-11-26', 'Tuesday', 'fr'. "
                                "This is not case sensitive.",
                           required=False)
    argparser.add_argument("-s", "--speaker",
                           help="Filter output to only include speakers with this name. "
                                "Possible values include e.g. 'Werner Vogels', 'Vogels'. "
                                "This is not case sensitive.",
                           required=False)
    argparser.add_argument("-t", "--type",
                           help="Filter output to only include this type of sessions. "
                                "Possible values include e.g. 'Session', 'Workshop'. "
                                "Filtering for 'Session' will not show items of type 'Builders Session'. "
                                "This is not case sensitive.",
                           required=False)
    argparser.add_argument("-l", "--location",
                           help="Filter output to only include this location. "
                                "Possible values include e.g. 'Venetian', 'Grand Ballroom B'. "
                                "This is not case sensitive.",
                           required=False)
    argparser.add_argument("-n", "--name",
                           help="Filter output to only include sessions containing this text in title. "
                                "Possible values include e.g. 'Infrastructure', 'how to'. "
                                "This is not case sensitive.",
                           required=False)
    argparser.add_argument("-a", "--abstract",
                           help="Filter output to only include sessions containing this text in abstract. "
                                "Possible values include e.g. 'containers', 'will present'. "
                                "This is not case sensitive.",
                           required=False)
    argparser.add_argument("-r", "--reserved", help="Only show reserved sessions.", action="store_true", required=False)
    argparser.add_argument("-f", "--file", help="Use this file instead of parsing", required=False)
    argparser.add_argument("--ical", help="Export schedule to iCal file", action="store_true", required=False)
    argparser.add_argument("-q", "--quiet", help="Do not print session schedule to console output. "
                                                 "This overrules the verbosity argument.",
                           action="store_true", required=False)
    argparser.add_argument("-v", "--verbose", help="Increase output verbosity", action="count", required=False)
    argparser.add_argument("-x", "--show_browser", help="Show the browser doing his work",
                           action="store_true", required=False)
    args = argparser.parse_args()
    return args


if __name__ == "__main__":
    main()
