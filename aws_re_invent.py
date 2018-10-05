import datetime
import re
import sys
import time
from collections import namedtuple
from itertools import groupby

from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException

from bash_color import BashColor
from browser_handler import BrowserHandler
from file_impex import load_sessions_from_csv, save_sessions_to_csv


class AWSreInvent:
    def __init__(self, args):
        self.args = args

        self.aws_re_invent_catalog_favorites = "https://www.portal.reinvent.awsevents.com/connect/interests.ww"
        login_form_selector = "//form[@id='loginForm']"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@id='loginUsername']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@id='loginPassword']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//input[@type='submit']"

        if self.args.file is None:
            self._init_browser()

            self.html_tag_regex = re.compile(r"<[^<]*>", re.IGNORECASE)
            self.html_tag_with_content_regex = re.compile(r"<[^<]*>[^<]*</[^<]*>", re.IGNORECASE)

    def _init_browser(self):
        self.browser_handler = BrowserHandler(self.args)
        self.browser = self.browser_handler.browser
        self.login()

    def login(self):
        self.browser.get(self.aws_re_invent_catalog_favorites)
        time.sleep(1)

        self._handle_cookie_agreement_banner()

        iteration = 0
        while self._user_is_not_logged_in():
            iteration += 1
            try:
                self._insert_login_credentials()
                self._click_login_button()
            except NoSuchElementException as e:
                if iteration > 10:
                    raise e
                time.sleep(iteration * 1)
                continue
            if iteration > 2:
                self._handle_login_unsuccessful()

    def _handle_cookie_agreement_banner(self):
        if len(self.browser.find_elements_by_xpath("//div[@id='cookieAgreementDisplayText']")) > 0:
            cookie_agreement_button = self.browser.find_element_by_xpath("//input[@id='cookieAgreementAcceptButton']")
            cookie_agreement_button.click()

    def _user_is_not_logged_in(self):
        return 'logout' not in self.browser.page_source

    def _insert_login_credentials(self):
        login_field_user = self.browser.find_element_by_xpath(self.LOGIN_USERNAME_SELECTOR)
        login_field_user.clear()
        login_field_user.send_keys(self.args.username)
        login_field_password = self.browser.find_element_by_xpath(self.LOGIN_PASSWORD_SELECTOR)
        login_field_password.clear()
        login_field_password.send_keys(self.args.password)

    def _click_login_button(self):
        login_button = self.browser.find_element_by_xpath(self.LOGIN_BUTTON_SELECTOR)
        login_button.click()
        time.sleep(2)  # wait for page to load

    def _handle_login_unsuccessful(self):
        time.sleep(1)
        if self._user_is_not_logged_in():
            sys.stderr.write("Login to AWS re:Invent page failed.")
            sys.stdout.flush()
            self.browser_handler.kill()
            sys.exit(1)

    def handle_sessions(self):
        if self.args.file:
            sessions = load_sessions_from_csv(self.args.file)
        else:
            sessions = self.parse_sessions()
            save_sessions_to_csv(sessions)

        sessions.sort(key=lambda session: session.start)
        grouped_sessions = groupby(sessions, lambda session: datetime.datetime.strftime(session.start, '%A, %Y-%m-%d'))
        for key, group in grouped_sessions:
            sessions = list(group)
            group_size = len(sessions)
            sessions = self.filter_sessions_by_arguments(sessions)
            if self.args.day is None or self.args.day.lower() in key.lower():
                print()
                print(
                    BashColor.BOLD +
                    '### {day}   [showing {filtered_size} of {day_size} total items] #################################################'.format(
                        day=key,
                        filtered_size=len(sessions),
                        day_size=group_size
                    ) + BashColor.END)
                print()
                self.print_sessions(sessions)

    def filter_sessions_by_arguments(self, sessions):
        if self.args.type:
            sessions = [session for session in sessions if self.args.type.strip().lower() == session.type.lower()]
        if self.args.speaker:
            sessions = [session for session in sessions if self.args.speaker.strip().lower() in session.speaker.lower()]
        if self.args.location:
            sessions = [session for session in sessions if self.args.location.strip().lower() in session.location.lower()]
        if self.args.abstract:
            sessions = [session for session in sessions if self.args.abstract.strip().lower() in session.abstract.lower()]
        return sessions

    def parse_sessions(self):
        self.browser.get(self.aws_re_invent_catalog_favorites)
        time.sleep(1)

        self._open_all_session_details()

        sessions_page = BeautifulSoup(self.browser.page_source, 'html.parser')
        sessions_tab = sessions_page.find('div', id='sessionsTab')
        sessions_rows = sessions_tab.find_all('div', class_='resultRow')

        sessions = []

        for session_row in sessions_rows:
            session = self._parse_session(session_row)
            sessions.append(session)

        return sessions

    def _open_all_session_details(self):
        session_schedule_details_buttons = self.browser.find_elements_by_xpath(
            "//div[@class='sessionTimes']/a[@class='expandSessionImg']"
        )
        for session_schedule_details_button in session_schedule_details_buttons:
            session_schedule_details_button.click()

        session_abstract_details_buttons = self.browser.find_elements_by_xpath(
            "//a[contains(@class, 'moreLink')]"
        )
        for session_abstract_details_button in session_abstract_details_buttons:
            session_abstract_details_button.click()

    def _parse_session(self, session_row):
        session = namedtuple('Session', ['title', 'id', 'type', 'speakers', 'abstract', 'start', 'end', 'location'])
        session.title = session_row.find('span', class_='title').get_text()
        session.id = session_row.find('span', class_='abbreviation').get_text().rstrip(' - ')
        session.type = session_row.find('small', class_='type').get_text()
        html_element_id = session_row['id']

        session.speakers = self._parse_session_speakers(session_row)

        session.abstract = session_row.find('span', class_='abstract').get_text().strip().rstrip(' View Less')
        session_details = self.browser.find_element_by_xpath(
            "//div[@id='{element_id}']//ul".format(element_id=html_element_id)
        ).get_attribute('innerHTML')
        session.start, session.end = self._parse_session_datetime(session_details)
        session.location = self.browser.find_element_by_xpath(
            "//div[@id='{element_id}']//span[contains(@class, 'sessionRoom')]".format(element_id=html_element_id)
        ).text.lstrip('– ')

        return session

    def _parse_session_datetime(self, session_details):
        session_start, session_end_time = self.html_tag_with_content_regex.sub('', session_details).split(' - ')
        session_start_time = str(datetime.datetime.now().year) + ' ' + session_start
        session_start_datetime = datetime.datetime.strptime(session_start_time, '%Y %A, %b %d, %I:%M %p')
        session_end_hour, session_end_minute = session_end_time.split(' ')[0].split(':')
        session_end_am_pm = session_end_time.split(' ')[1]
        if session_end_am_pm.upper() == 'PM':
            session_end_hour = (int(session_end_hour) % 12) + 12
        session_end_datetime = session_start_datetime.replace(
            hour=int(session_end_hour),
            minute=int(session_end_minute)
        )
        return session_start_datetime, session_end_datetime

    def _parse_session_speakers(self, session_row):
        session_speakers = []
        parsed_speakers = str(session_row.find('small', class_='speakers')).strip().split('<br/>')[:-1]
        for parsed_speaker in parsed_speakers:
            parsed_speaker = parsed_speaker.replace('\t', '')
            parsed_speaker = parsed_speaker.replace('\n', '')
            parsed_speaker = self.html_tag_regex.sub('', parsed_speaker)
            session_speakers.append(parsed_speaker)
        return session_speakers

    def print_sessions(self, sessions):
        for session in sessions:
            self.print_session(session)

    def print_session(self, session):
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

        if self.args.show_abstract:
            print(BashColor.DIM + '{abstract}'.format(abstract=session.abstract) + BashColor.END)
        print()
