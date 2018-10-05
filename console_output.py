import datetime
import sys

from bash_color import BashColor


def print_day_schedule(sessions):
    earliest_start = sessions[0].start

    sys.stdout.write(BashColor.BOLD + ' {id:<{width}}'.format(id='ID', width=9) + BashColor.DARKGREY + ' # ' + BashColor.END)
    sys.stdout.write(BashColor.BOLD + '{title:<{width}}'.format(title='TITLE', width=60) + BashColor.DARKGREY + ' # ' + BashColor.END)
    sys.stdout.write(BashColor.BOLD + BashColor.VIOLET + '{type:<{width}}'.format(type='TYPE', width=10) + BashColor.DARKGREY + ' # ' + BashColor.END)
    sys.stdout.write(BashColor.BOLD + BashColor.RED + '{location:<{width}}'.format(location='LOCATION', width=9) +
                     BashColor.DARKGREY + ' # ' + BashColor.END)
    sys.stdout.write(BashColor.BOLD + BashColor.YELLOW + '{start} '.format(start='SCHEDULE') + BashColor.END)
    sys.stdout.write('\n')
    sys.stdout.write(BashColor.BOLD + BashColor.DARKGREY + '{id}'.format(id='-' * 11) + '+')
    sys.stdout.write('{title}'.format(title='-' * 60) + '--+')
    sys.stdout.write('{type}'.format(type='-' * 10) + '--+')
    sys.stdout.write('{location}'.format(location='-' * 9) + '--+')
    sys.stdout.write('{start} '.format(start='-' * 30) + BashColor.END)
    sys.stdout.write('\n')
    sys.stdout.flush()

    for session in sessions:
        _print_session_for_day_schedule(earliest_start, session)
    sys.stdout.flush()
    sys.stdout.write('\n')


def _print_session_for_day_schedule(earliest_start, session):
    duration = (session.end - session.start).seconds // 60 // 15
    start_offset = (session.start - earliest_start).seconds // 60 // 15
    sys.stdout.write(
        BashColor.BOLD + ' {id:<{width}}'.format(id=session.id, width=9) + BashColor.DARKGREY + ' | ' + BashColor.END)
    sys.stdout.write('{title:<{width}}'.format(title=session.title[:60], width=60) + BashColor.DARKGREY + ' | ' + BashColor.END)
    sys.stdout.write(BashColor.VIOLET + '{type:<{width}}'.format(type=session.type[:10], width=10) + BashColor.DARKGREY + ' | ' + BashColor.END)
    sys.stdout.write(BashColor.RED + '{location:<{width}}'.format(location=session.location.split(',')[0][:9], width=9) + BashColor.DARKGREY + ' | ' + BashColor.END)
    sys.stdout.write(' ' * start_offset)
    sys.stdout.write(BashColor.YELLOW + '{start} '.format(start=datetime.datetime.strftime(session.start, '%H:%M')))
    sys.stdout.write('#' * duration)
    sys.stdout.write(' {end}'.format(end=datetime.datetime.strftime(session.end, '%H:%M')) + BashColor.END)
    sys.stdout.write('\n')


def print_sessions(sessions, args):
    for session in sessions:
        print_session(session, args)


def print_session(session, args):
    print(BashColor.UNDERLINE + '{id} - {title}'.format(id=session.id, title=session.title) + BashColor.END)
    print(BashColor.VIOLET + '{type}'.format(type=session.type) + BashColor.END + '  by ' +
          BashColor.BLUE + ', '.join(session.speakers) + BashColor.END)
    print(
        BashColor.YELLOW + '{start} -> {end}'.format(
            start=datetime.datetime.strftime(session.start, '%a (%b %d) %H:%M'),
            end=datetime.datetime.strftime(session.end, '%H:%M')
        ) + BashColor.END +
        '  @ ' + BashColor.RED + '{location}'.format(location=session.location) + BashColor.END
    )

    if args.show_abstract:
        print(BashColor.DIM + '{abstract}'.format(abstract=session.abstract) + BashColor.END)
    print()
