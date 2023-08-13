import json
import random
import sys
from configparser import ConfigParser
from datetime import datetime, timedelta
from time import sleep, time

from bs4 import BeautifulSoup
from requests import get, post

from logger_inner import login

base_url = 'https://raumbuchung.bibliothek.kit.edu/sitzplatzreservierung'
headers = {'User-Agent': 'Mozilla/5.0'}
floors: dict = json.load(open('resources/floors.json'))
periods: dict = json.load(open('resources/periods.json'))
periods_inv = dict((v, k) for k, v in periods.items())
cfg_pars = ConfigParser()
login_name: str
login_cookie: str
date = datetime.now()  # Tomorrow is for losers
debug = True


def debugprint(*args):
    if debug:
        print(args)


def fetch(url, floor, date: datetime):
    return get(url, params={'area': floor, 'year': date.year, 'month': date.month, 'day': date.day},
               headers=headers)


def get_desc_from_period(period):
    return periods[str(period)] + "+"


def get_free_seat_numbers(actual_daytime_table) -> []:
    lines = [line for line in str(actual_daytime_table).split('\n') if "edit_entry.php" in line]
    return [line.split('room=')[1].split('&')[0] for line in lines]


def actually_reserve(desc, day, seconds, floorno, seat_number, month=date.month, year=date.year):
    return post(base_url + '/edit_entry_handler.php',
                headers={'User-Agent': 'Mozilla/5.0'},
                params={
                    'name': login_name, 'description': desc,
                    'start_day': day, 'start_month': month, 'start_year': year,
                    'start_seconds': seconds,
                    'end_day': day, 'end_month': year, 'end_year': year,
                    'end_seconds': seconds,
                    'area': floorno, 'rooms[]': seat_number, 'type': 'K', 'confirmed': 1,
                    'confirmed': 1,
                    'create_by': login_name, 'rep_id': 0, 'edit_type': 'series'
                },
                cookies={"PHPSESSID": login_cookie})


def calc_date(_day_offset, period):
    t = datetime.now() + timedelta(int(_day_offset))
    seconds = str(43200 + 60 * period)  # wtf
    return t.year, t.month, t.day, seconds


def _reserve(period, _floor, _day_offset=0):
    floorno = floors[_floor]

    page = fetch(base_url + '/day.php', floorno, date)
    souped = BeautifulSoup(page.text, 'html.parser')

    daytimes = [x for x in souped.find_all('tr', {'class': ['even_row', 'odd_row']})]
    # Assume daytimes is sorted (somehow)
    relevant_row = daytimes[period]
    seat_numbers = get_free_seat_numbers(relevant_row)

    if len(seat_numbers) == 0:
        debugprint(f"No seat in {_floor}")
        return False

    desc = get_desc_from_period(period)

    year, month, day, seconds = calc_date(_day_offset, period)

    random.shuffle(seat_numbers)
    for seat_number in seat_numbers:
        response = actually_reserve(desc, day, seconds, floorno, seat_number, date.month, date.year)
        if response.status_code == 200:
            print(f"Reserved: {desc}{_floor} at {year}.{month}.{day}\ngoodbye")
            return True
    return False


def get_period(daytime) -> int:
    return int(periods_inv.get(daytime))


def continue_booking(daytime='vormittags', day_offset=0, floor=None, tries=1, multiple_tries_period=1000):
    period = get_period(daytime)
    print(period)

    _tries = int(tries)

    while _tries > 0 or _tries == -1:
        x = time()
        if floor is None:
            for floorno in floors.keys():
                if _reserve(period, floorno, day_offset):
                    return  # Found seat
            print("no free seats found for your query...")
        else:
            if not _reserve(period, floor, day_offset):
                print("no free seats found for your query...")
            else:
                return # Found seat
        print(f"trying {_tries} more times...")

        sleep((time() - x + int(multiple_tries_period))/1000)
        _tries -= 1
    print("nothing found. goodbye")


'''
Scrape a certain website for free seats and then grab one
'''
if __name__ == '__main__':
    cfg_path = sys.argv[1] or 'resources/config_morning.cfg'
    debugprint("config path: ", cfg_path)
    cfg_pars.read(cfg_path)

    daytime = None
    floor = None
    day_offset = 0
    tries = 1
    multiple_tries_period = 1000  # ms
    try:
        daytime = cfg_pars['bib']['daytime']
        floor = cfg_pars['bib']['preferredFloor']
        day_offset = cfg_pars['bib']['daysOffset']
        debug = cfg_pars['bib']['debug']
        tries = cfg_pars['bib']['tries']
        multiple_tries_period = cfg_pars['bib']['multipleTriesPeriod']
    except KeyError as keyError:
        debugprint("KeyError", keyError)
        yn = input('Failed at reading above key... go on? [*/n]')
        if 'n' in yn:
            print("goodbye")
            exit(0)

    if len(sys.argv) > 2:
        secret = open(sys.argv[2], 'r').read()
    else:
        secret = None
    login_cookie, login_name = login(secret)
    if login_cookie is not None:
        continue_booking(daytime, day_offset, floor, tries, multiple_tries_period)
    else:
        print("Login failed... goodbye")
