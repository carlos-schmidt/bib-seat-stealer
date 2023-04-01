import json
from configparser import ConfigParser
from datetime import datetime
from getpass import getpass
from io import FileIO
from os import path, write

import requests
from bs4 import BeautifulSoup

base_url = 'https://raumbuchung.bibliothek.kit.edu/sitzplatzreservierung'
headers = {'User-Agent': 'Mozilla/5.0'} # Yes I am a Mozilla/5.0, why do you ask?
floors: dict = json.load(open('resources/floors.json'))
periods: dict = json.load(open('resources/periods.json'))

cfgpars = ConfigParser()
debug: bool = True
login_name: str
login_cookie: str
save_login: bool = True

date = datetime.now()  # Tomorrow is for losers


def debugprint(*args):
    global debug
    if debug:
        print(args)


def fetch(url, floor, date: datetime):
    return requests.get(url, params={'area': floor, 'year': date.year, 'month': date.month, 'day': date.day}, headers=headers)


def write_cookie(content):
    with open('COOKIE', 'w+') as cookiefile:
        cookiefile.write(json.dumps(content).replace('\'', '\"'))


def login():
    global login_cookie
    global login_name
    _url = base_url + '/admin.php?'
    _username = input('username:')
    _password = getpass('password:')

    after_login_page = requests.post(_url, params={
        'NewUserName': _username, 'NewUserPassword': _password, 'Action': 'SetName'}, headers=headers)

    login_cookie = after_login_page.headers['Set-Cookie'].split(';')[
        0].split('=')[-1]
    souped = BeautifulSoup(after_login_page.text, 'html.parser')

    for line in souped.find_all('a'):
        if 'creatormatch=' in str(line):
            login_name = str(line).split('creatormatch=')[-1].split('"')[0]

    if login_cookie is not None and login_name is not None:
        print('Login success!')
        debugprint('Cookie', login_cookie, 'login name', login_name)
        if save_login:
            write_cookie({'login_cookie': login_cookie,
                         'login_name': login_name})
        return True
    else:
        debugprint(after_login_page)
    return False


def _reserve(period, floor, day_offset):
    global floors
    _fetchurl = base_url + '/day.php'
    floorno = floors[floor]
    page = fetch(_fetchurl, floorno, date)
    souped = BeautifulSoup(page.text, 'html.parser')

    daytimes = [x for x in souped.find_all(
        'tr', {'class': ['even_row', 'odd_row']})]
    actual_daytime_table = ''
    daytimes = [daytimes[0], daytimes[2], daytimes[1],
                daytimes[3]]  # Vormittags <-> Nachmittags
    for daytime in daytimes:
        if periods[str(period)] in str(daytime):
            actual_daytime_table = daytime

    room_numbers = []
    for line in str(actual_daytime_table).split('\n'):
        if 'edit_entry.php' in str(line):
            room_numbers.append(line.split('room=')[1].split('&')[0])
    desc = periods[str(period)] + "+"

    day = date.day + int(day_offset)

    if (str(actual_daytime_table).find('new') > 0):
        _url = base_url + '/edit_entry_handler.php'
        room_no = str(room_numbers.pop(0))
        response = requests.post(_url,
                                 headers={'User-Agent': 'Mozilla/5.0'},
                                 params={
                                     'name': login_name, 'description': desc,
                                     'start_day': day, 'start_month': date.month, 'start_year': date.year, 'start_seconds': 43200 + 60 * period,
                                     'end_day': day, 'end_month': date.month, 'end_year': date.year, 'end_seconds': 43200 + 60 * period,
                                     'area': floorno, 'rooms[]': room_no, 'type': 'K', 'confirmed': 1,
                                     'create_by': login_name, 'rep_id': 0, 'edit_type': 'series'
                                 },
                                 cookies={"PHPSESSID": login_cookie})
        if 'Sie haben keine Berechtigung, diesen Eintrag zu ändern' in response.text:
            print('Login cookie not working... deleting cookie. Log in again')
            write_cookie('')
            return
        print("Reserved a spot for you at",
              floor, "time of reservation:", periods[str(period)], ", day of reservation: ", date.date(), "+", day_offset, "days",  "at", periods[str(period)])
        return True
    else:
        print("no free seats in", floor, "for day",
              day, "at", periods[str(period)])
        return False


def snatch(period, floor, day_offset):
    if floor is None or floor != "":
        for floor in floors.keys():
            if _reserve(period, floor, day_offset):
                return
    else:
        print(floor)
        _reserve(period, floor, day_offset)


def continue_booking(daytime, day_offset, floor):
    if 'vormittags' in daytime:
        snatch(0, floor, day_offset)
    elif 'nachmittags' in daytime:
        snatch(1, floor, day_offset)
    elif 'abends' in daytime:
        snatch(2, floor, day_offset)
    elif 'nachts' in daytime:
        snatch(3, floor, day_offset)


'''
Scrape a certain website for free seats and then grab one
'''
if __name__ == '__main__':
    cfgpars.read('config.cfg')
    floor = None
    daytime = 'vormittags'
    day_offset = 0
    try:
        daytime = cfgpars['bib']['daytime']
        day_offset = cfgpars['bib']['daysOffset']
        debug = cfgpars['bib']['debug']
        save_login = cfgpars['bib']['saveLogin']
        floor = cfgpars['bib']['preferredFloor']
    except KeyError as keyError:
        debugprint("KeyError", keyError)
        yn = input('Failed at reading config file... continue? [*/n]')
        if 'n' in yn:
            exit(0)

    if save_login:
        if not path.exists('COOKIE'):
            with open('COOKIE', 'w'):
                print('Created COOKIE file')
        with open('COOKIE', 'r') as cookie:
            try:
                cookie_json = json.load(cookie)
                if str(cookie_json) != '':
                    login_cookie = cookie_json['login_cookie']
                    login_name = cookie_json['login_name']
                    continue_booking(daytime, day_offset, floor)
            except json.JSONDecodeError:
                print('Corrupt cookie or something... log in')
                if login():
                    continue_booking(daytime, day_offset, floor)
    elif login():
        continue_booking(daytime, day_offset, floor)
    else:
        print("Login failed... try again")
