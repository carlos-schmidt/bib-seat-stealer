from datetime import datetime
from time import sleep

import requests
from bs4 import BeautifulSoup, ResultSet

from model.Floor import Floor
from getpass import getpass

floors = {'first_floor': '42',
          'second_floor': '34',
          'empore': '35',
          'third_floor': '44',
          'ground_floor': '40'
          }

periods = {0: 'vormittags', 1: 'nachmittags', 2: 'abends', 3: 'nachts'}

login_name: str
login_cookie: str

date = datetime.now()  # Tomorrow is for losers


def fetch(url, floor, date: datetime):
    return requests.get(url, params={'area': floor, 'year': date.year, 'month': date.month, 'day': date.day}, headers={'User-Agent': 'Mozilla/5.0'}).text


def login():
    _url = 'https://raumbuchung.bibliothek.kit.edu/sitzplatzreservierung/admin.php?'
    _username = input('username:')
    _password = getpass('password:')

    return requests.post(_url, params={'NewUserName': _username, 'NewUserPassword': _password, 'Action': 'SetName'}, headers={'User-Agent': 'Mozilla/5.0'})


def _reserve(period, floor, day_offset):
    _fetchurl = 'https://raumbuchung.bibliothek.kit.edu/sitzplatzreservierung/day.php'

    page = fetch(_fetchurl, floors[floor], date)
    souped = BeautifulSoup(page, 'html.parser')

    daytimes = [x for x in souped.find_all(
        'tr', {'class': ['even_row', 'odd_row']})]
    actualDaytimeTable = ''
    daytimes = [daytimes[0], daytimes[2], daytimes[1],
                daytimes[3]]  # Vormittags <-> Nachmittags
    for daytime in daytimes:
        if periods[period] in str(daytime):
            actualDaytimeTable = daytime

    roomNumbers = []
    for line in str(actualDaytimeTable).split('\n'):
        if 'edit_entry.php' in str(line):
            roomNumbers.append(line.split('room=')[1].split('&')[0])
    desc = periods[period] + "+"

    response = None

    day = date.day + int(day_offset)
    if (str(actualDaytimeTable).find('new') > 0):

        while (len(roomNumbers) > 0 and (response is None or response.status_code != 302 or response.status_code != 200)):
            _url = 'https://raumbuchung.bibliothek.kit.edu/sitzplatzreservierung/edit_entry_handler.php'
            roomNo = str(roomNumbers.pop(0))
            response = requests.post(_url, headers={'User-Agent': 'Mozilla/5.0'},
                                     params={
                'name': login_name,
                'description': desc,
                'start_day': day,
                'start_month': date.month,
                'start_year': date.year,
                'start_seconds': '43320',
                'end_day': day,
                'end_month': date.month,
                'end_year': date.year,
                'end_seconds': '43320',
                'area': floors[floor],
                'rooms[]': roomNo,
                'type': 'K',
                'confirmed': 1,
                'confirmed': 1,
                'create_by': login_name,
                'rep_id': 0,
                'edit_type': 'series'
            },
                cookies={"PHPSESSID": login_cookie})
        print("Reserved a spot for you at",
              floor, "time of reservation:", periods[period], ", day of reservation: ", date.date(), "+", day_offset, "days",  "at", periods[period])
        return True
    else:
        print("no free seats in", floor, "for day", day, "at", periods[period])
        return False


def snatch(period, floor, day_offset):
    if floor != "":
        _reserve(period, floor, day_offset)
    else:
        for floor in floors:
            if _reserve(period, floor, day_offset):
                return


def continueBooking():
    daytime = input(
        'When to book? (v)ormittags, (n)achmittags, (a)bends, (nacht)s: ')
    floor = input(
        'Which Floor? (default: best to worst, else: choice of ["first_floor", "empore", "first_floor", "third_floor", "ground_floor"]: ') or ""
    day_offset = input(
        "Finally: How many days in advance? (default: today = 0, max = 3): ") or 0
    if 'v' in daytime:
        snatch(0, floor, day_offset)
    elif 'nacht' in daytime:
        snatch(3, floor, day_offset)
    elif 'n' in daytime:
        snatch(1, floor, day_offset)
    elif 'a' in daytime:
        snatch(2, floor, day_offset)
    else:
        print('No useful input detected...')


'''
Scrape a certain website for free seats
'''
if __name__ == '__main__':
    _url = 'https://raumbuchung.bibliothek.kit.edu/sitzplatzreservierung/day.php' or input(
        'Tell me the site to look at')

    pages = {}

    # Get all pages first (maybe parallelize?)
    for floor in floors:
        pages[floor] = fetch(_url, floors[floor], date)

    # for page in pages:
    #     souped = BeautifulSoup(pages[page], 'html.parser')

    #     daytimes = [x for x in souped.find_all(
    #         'tr', {'class': ['even_row', 'odd_row']})]
    #     actualDaytimeTable = ''
    #     for daytime in daytimes:
    #         if periods[3] in str(daytime):
    #             actualDaytimeTable = daytime

    #     #print(actualDaytimeTable)
    #     vormittags, abends, nachmittags, nachts = [str(x) for x in souped.find_all(
    #         'tr', {'class': ['even_row', 'odd_row']})]

    #     vormittags = Floor(vormittags.count(
    #         'new'), vormittags.count('private'), page)
    #     nachmittags = Floor(nachmittags.count(
    #         'new'), nachmittags.count('private'), page)
    #     abends = Floor(abends.count(
    #         'new'), abends.count('private'), page)
    #     nachts = Floor(nachts.count(
    #         'new'), nachts.count('private'), page)

    #     # print(vormittags)
    #     # print(nachmittags)
    #     # print(abends)
    #     # print(nachts)

    if (input('book seat?')):
        after_login_page = login()
        login_cookie = after_login_page.headers['Set-Cookie'].split(';')[
            0].split('=')[-1]
        souped = BeautifulSoup(after_login_page.text, 'html.parser')

        for line in souped.find_all('a'):
            if 'creatormatch=' in str(line):
                login_name = str(line).split('creatormatch=')[-1].split('"')[0]

    print('Your user number:', login_name,
          ', your login cookie:', login_cookie)

    continueBooking()
