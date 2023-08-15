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
debug = False


def salute(till):
    msg = f"""\n
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⠒⠒⠒⠒⠒⠒⠒⠲⠦⠤⢄⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣠⣤⠀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⢷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡤⠀⠀⣀⡠⠤⠔⠚⠛⠋⠉⠀⠀⠀⠀⠀⠈⠉⠙⠛⠒⠦⢤⡀⠀⠀⠀⠀⣸⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢷⢠⠞⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢼⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣽⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡇⠀⠀⠀⢀⣀⣤⣦⣶⣤⣤⣤⣤⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡄⣠⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠲⢦⡀⠀⠀⠀⠀⢠⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣻⣿⣿⣿⣿⣿⣿⣿⠿⣿⣿⣿⣿⣿⣭⣭⠉⠉⠙⠛⡶⢦⡄⢴⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⣿⣿⣿⣿⣿⡿⠿⠟⠿⡉⠙⠻⣄⠀⠀⠀⠀⠀⢠⣿⣿⣍⡉⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⡿⠛⠋⠁⠀⠀⢀⣠⢼⣲⠶⠛⡆⢠⣤⣶⡖⠿⠿⣿⠛⢻⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣠⠿⠟⣻⠇⠀⢀⣠⢶⡯⠿⢺⡉⢰⡆⣰⣿⡿⠛⠁⠀⠀⠛⠚⠀⠀⠘⢢⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠞⠉⠁⠀⢀⣴⣯⠖⣤⠼⠓⠋⠀⠀⠀⢹⠎⣱⠟⠁⠀⠀⠀⠀⠀⠀⠀⢛⡆⠀⣀⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⢶⡞⠁⠀⢀⡤⠶⣫⠽⠚⠁⠀⢤⣀⡠⣄⡀⣀⣿⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠙⣏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⡼⠁⠀⣠⡴⣚⡭⠞⠋⠀⠀⠀⠀⠀⠀⠀⠙⢳⣽⡟⠋⢃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⡿⢿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⣠⡶⠏⢀⡠⣖⠿⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠏⠁⠀⠀⠘⢆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣯⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⢀⣴⠃⣠⣶⠿⠖⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⢀⡀⣰⣧⡀⠀⠀⠀⠀⠈⢷⣦⣤⣤⣀⣀⣀⣀⣀⣀⣀⣀⣼⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⣶⣿⣠⡾⠏⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢐⣚⣛⣛⡿⣿⣇⠉⠳⢤⣀⠀⠀⠀⠈⠻⠿⣿⣿⣿⣿⣿⣿⡿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⣼⣧⣾⠟⠀⠀⠀⠀⠀⠀⠴⣛⡉⢉⣉⣉⣭⡭⠾⠛⠋⠁⣠⣧⠟⠀⠀⠀⠈⠓⢦⡀⠀⠀⠀⠀⣼⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⣿⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⣰⠃⠀⠀⠀⠀⠀⠀⠀⠹⣄⠀⠀⡸⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠛⣯⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣀⠀⠀⠀⠀⠀⣠⠴⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢦⡀⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠘⢧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠲⢿⣛⡋⢙⣶⡶⠾⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⢦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠘⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠓⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠈⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢯⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠈⠳⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠦⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡸⣿⠦⣄⡀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⢳⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡇⣿⡇⠈⠉⠻⣄⠀⠀⠀⠀⠀⣸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⢳⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⣿⣹⡄⠀⠀⠈⠁⠀⠀⠀⠀⣽⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⠀⠀⢧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⡇⣯⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠿⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢧⣀⣨⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣇⢹⢿⣿⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣯⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠈⢿⢿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⠆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣥⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣥⣤⣤⣤⣤⣤⣤
        Current time is {datetime.now().strftime('%H:%M')}. Waking up in {':'.join(str(till).split(':')[:2])}h, soldier!
    """
    print(msg)


def goodbye():
    msg = """\n
                          .______.                 
   ____   ____   ____   __| _/\_ |__ ___.__. ____  
  / ___\ /  _ \ /  _ \ / __ |  | __ <   |  |/ __ \ 
 / /_/  >  <_> |  <_> ) /_/ |  | \_\ \___  \  ___/ 
 \___  / \____/ \____/\____ |  |___  / ____|\___  >
/_____/                    \/      \/\/         \/
          """
    print(msg)


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
        return False

    desc = get_desc_from_period(period)

    year, month, day, seconds = calc_date(_day_offset, period)

    random.shuffle(seat_numbers)
    for seat_number in seat_numbers:
        response = actually_reserve(desc, day, seconds, floorno, seat_number, date.month, date.year)
        if response.status_code == 200:
            print(f"Reserved: {desc}{_floor} at {year}.{month}.{day}")
            goodbye()
            return True
    return False


def get_period(daytime) -> int:
    return int(periods_inv.get(daytime))


def compute_initial_timeout(_snatch_time):
    _zero_timeout = datetime.combine(date.today(), datetime.strptime('0:0:0', '%H:%M:%S').time())
    if _snatch_time is None:
        return _zero_timeout - _zero_timeout
    # combine builds a datetime, that can be subtracted.
    snatch_time_obj = datetime.combine(date.today(), datetime.strptime(_snatch_time, '%H:%M:%S').time())
    initial_timeout = (snatch_time_obj - datetime.now())
    if initial_timeout.total_seconds() < 0:
        return _zero_timeout - _zero_timeout
    return initial_timeout


def continue_booking(daytime, day_offset, floor, tries, multiple_tries_period):
    period = get_period(daytime)
    print(period)

    _tries = 0
    try:
        while _tries < int(tries) or int(tries) == -1:
            x = time()
            if floor is None:
                for floor_no in floors.keys():
                    if _reserve(period, floor_no, day_offset):
                        return  # Found seat
            elif _reserve(period, floor, day_offset):
                return  # Found seat
            print(f'tried {_tries}/{tries} times...', end='\r')

            sleep((time() - x + int(multiple_tries_period)) / 1000)
            _tries += 1
        print("nothing found.")
        goodbye()
    except KeyboardInterrupt as _:
        print("\nSnatcher was interrupted.")
        goodbye()


'''
Scrape a certain website for free seats and then grab one
'''
if __name__ == '__main__':
    cfg_path = sys.argv[1] if len(sys.argv) > 1 else 'config_morning.cfg'
    cfg_pars.read(cfg_path)

    daytime = None
    floor = None
    day_offset = 0
    tries = 1
    multiple_tries_period = 1000  # ms
    snatch_time = None
    try:
        daytime = cfg_pars['bib']['daytime']
        floor = cfg_pars['bib']['preferredFloor']
        day_offset = cfg_pars['bib']['daysOffset']
        debug = cfg_pars['bib']['debug']
        tries = cfg_pars['bib']['tries']
        multiple_tries_period = cfg_pars['bib']['multipleTriesPeriod']
        snatch_time = cfg_pars['bib']['snatchTime']
    except KeyError as keyError:
        yn = input('Failed at reading above key... go on? [*/n]')
        if 'n' in yn:
            goodbye()
            exit(0)

    if len(sys.argv) > 2:
        secret = open(sys.argv[2], 'r').read()
    else:
        secret = None

    _initial_timeout = compute_initial_timeout(snatch_time)

    if _initial_timeout.total_seconds() > 3:
        salute(_initial_timeout)
    sleep(_initial_timeout.total_seconds())

    login_cookie, login_name = login(secret)
    if login_cookie is not None:
        continue_booking(daytime, day_offset, floor, tries, multiple_tries_period)
    else:
        print("Login failed...")
        goodbye()
