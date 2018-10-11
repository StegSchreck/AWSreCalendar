import csv
import datetime
import os
import time
from collections import namedtuple


def load_sessions_from_csv(filename='import.csv'):
    with open(os.path.join(os.path.dirname(__file__), filename), newline='', encoding='UTF-8') as input_file:
        reader = csv.reader(input_file, delimiter=',')
        headers = next(reader, None)
        return [convert_csv_row_to_session(headers, row) for row in reader]


def convert_csv_row_to_session(headers, row):
    session = namedtuple('Session', ['title', 'id', 'type', 'speakers', 'abstract', 'start', 'end', 'location', 'reserved'])
    session.title = row[headers.index("title")]
    session.id = row[headers.index("id")]
    session.type = row[headers.index("type")]
    session.speakers = row[headers.index("speakers")].lstrip('[').rstrip(']').replace("'", '').split(',')
    session.abstract = row[headers.index("abstract")]
    session.start = datetime.datetime.strptime(row[headers.index("start")], '%Y-%m-%d %H:%M:%S')
    session.end = datetime.datetime.strptime(row[headers.index("end")], '%Y-%m-%d %H:%M:%S')
    session.location = row[headers.index("location")]
    session.reserved = row[headers.index("reserved")] == 'True'
    return session


def save_sessions_to_csv(sessions, filename='export.csv'):
    with open(os.path.join(os.path.dirname(__file__), filename), 'w') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(('title', 'id', 'type', 'speakers', 'abstract', 'start', 'end', 'location', 'reserved'))  # field header
        writer.writerows([(session.title, session.id, session.type, session.speakers, session.abstract, session.start, session.end, session.location, session.reserved) for session in sessions])


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
