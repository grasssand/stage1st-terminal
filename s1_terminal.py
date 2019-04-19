#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import getpass
import json
import os
import re
from xml.etree import ElementTree

from requests_html import HTMLSession

from config import *
from exception import LoginException


class Stage1stClient:
    def __init__(self, cookies=None):
        self._session = HTMLSession()
        self._session.headers.update(HEADERS)

        if os.path.isfile(COOKIES_FILE):
            self.login_with_cookies(COOKIES_FILE)
        else:
            self.login_with_password()

    def login_with_password(self):
        username = input("userame: ")
        password = getpass.getpass("password: ")
        message, cookies = self.login(username, password)
        return cookies

    def login_with_cookies(self, cookies):
        if os.path.isfile(cookies):
            with open(cookies) as f:
                cookies = f.read()
        ck = json.loads(cookies)
        self._session.cookies.update(ck)

    def login(self, username, password):
        data = {
            "cookietime": 2592000,
            "fastloginfield": "username",
            "username": username,
            "password": password,
        }
        resp = self._session.post(URL_LOGIN, data=data)
        content = ElementTree.fromstring(resp.content).text
        re_content = re.match(
            r".+(errorhandle_loginform|succeedhandle_loginform)\((.+)\,\s?\{.+", content
        )
        state, message = re_content.group(1), re_content.group(2)
        if state == "errorhandle_loginform":
            raise LoginException(message)
        cookies = json.dumps(self._session.cookies.get_dict())
        self.create_cookies_file(cookies)

        return message, cookies

    def create_cookies_file(self, cookies):
        if cookies:
            with open(COOKIES_FILE, "w") as f:
                f.write(cookies)

    def test(self):
        r = self._session.get("")


if __name__ == "__main__":
    s = Stage1stClient()
    r = s.login_with_password()
    print(r)
