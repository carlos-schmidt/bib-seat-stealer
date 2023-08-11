from getpass import getpass
import requests
from bs4 import BeautifulSoup

base_url = 'https://raumbuchung.bibliothek.kit.edu/sitzplatzreservierung'
headers = {'User-Agent': 'Mozilla/5.0'}

debug = True


def debugprint(*args):
    if debug:
        print(args)


def login(secret: str = None):
    _url = base_url + '/admin.php?'
    if secret is not None:
        _username = secret.split('\n')[0]
        _password = secret.split('\n')[1]
        print("Logging in", _username)
    else:
        _username = input('username:')
        _password = getpass('password:')

    after_login_page = requests.post(_url, params={
        'NewUserName': _username, 'NewUserPassword': _password, 'Action': 'SetName'}, headers=headers)

    login_cookie = after_login_page.headers['Set-Cookie'].split(';')[
        0].split('=')[-1]
    souped = BeautifulSoup(after_login_page.text, 'html.parser')
    login_name = None
    for line in souped.find_all('a'):
        if 'creatormatch=' in str(line):
            login_name = str(line).split('creatormatch=')[-1].split('"')[0]

    if login_cookie is not None and login_name is not None:
        print('Login success!')
        debugprint('Cookie', login_cookie, 'login name', login_name)
        return login_cookie, login_name
    else:
        debugprint(after_login_page)
    return None
