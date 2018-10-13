import csv
import os
import time
from collections import namedtuple
from datetime import datetime

from icalendar import Calendar, Event

EXPORTS_FOLDER = 'exports'


def wait_for_file_to_exist(filepath, seconds=30):
    iteration = 0
    while iteration < seconds:
        iteration += 1
        try:
            with open(filepath, 'rb') as file:
                return file
        except IOError:
            time.sleep(1)  # try every second
            continue
    raise IOError('Could not access {filepath} after {seconds} seconds'.format(filepath=filepath, seconds=str(seconds)))


def load_sessions_from_csv(filename='import.csv'):
    with open(os.path.join(os.path.dirname(__file__), EXPORTS_FOLDER, filename), newline='', encoding='UTF-8') as input_file:
        reader = csv.reader(input_file, delimiter=',')
        headers = next(reader, None)
        return [convert_csv_row_to_session(headers, row) for row in reader]


def convert_csv_row_to_session(headers, row):
    session = namedtuple('Session', ['title', 'id', 'type', 'speakers', 'abstract', 'start', 'end', 'location', 'reserved'])
    session.title = row[headers.index("subject")]
    session.id = row[headers.index("uid")]
    session.type = row[headers.index("type")]
    session.speakers = row[headers.index("speakers")].lstrip('[').rstrip(']').replace("'", '').split(',')
    session.abstract = row[headers.index("description")]
    start = row[headers.index("start date")] + ' ' + row[headers.index("start time")]
    session.start = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
    end = row[headers.index("end date")] + ' ' + row[headers.index("end time")]
    session.end = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
    session.location = row[headers.index("location")]
    session.reserved = row[headers.index("reserved")] == 'True'
    return session


def save_sessions_to_csv(sessions, filename='export.csv'):
    with open(os.path.join(os.path.dirname(__file__), EXPORTS_FOLDER, filename), 'w') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(('subject', 'uid', 'type', 'speakers', 'description', 'start date', 'start time', 'end date', 'end time', 'location', 'reserved'))  # field header
        writer.writerows([(session.title, session.id, session.type, session.speakers, session.abstract,
                           datetime.strftime(session.start, '%Y-%m-%d'), datetime.strftime(session.start, '%H:%M:%S'),
                           datetime.strftime(session.end, '%Y-%m-%d'), datetime.strftime(session.end, '%H:%M:%S'),
                           session.location, session.reserved) for session in sessions])


def save_sessions_to_ical(sessions, filename='export.ics'):
    with open(os.path.join(os.path.dirname(__file__), EXPORTS_FOLDER, filename), 'wb') as output_file:
        cal = Calendar()
        for session in sessions:
            event = Event()
            event['uid'] = session.id
            event['summary'] = session.title
            event['dtstart'] = datetime.strftime(session.start, '%Y%m%dT%H%M%S')
            event['dtend'] = datetime.strftime(session.end, '%Y%m%dT%H%M%S')
            event['description'] = session.abstract
            event['location'] = session.location
            cal.add_component(event)
        output_file.write(cal.to_ical())
