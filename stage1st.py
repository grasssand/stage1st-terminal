#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import getpass
import json
import os
import re
from xml.etree import ElementTree

from requests_html import HTMLSession

from config import HEADERS, URL_LOGIN, COOKIES_FILE
from exception import LoginError, ResourceError


class Stage1stClient:
    def __init__(self, cookies=None):
        self._session = HTMLSession()
        self._session.headers.update(HEADERS)
        self.content = None

        if os.path.isfile(COOKIES_FILE):
            self.login_with_cookies(COOKIES_FILE)
        else:
            self.login_with_password()

    def login_with_password(self):
        username = input("userame: ")
        password = getpass.getpass("password: ")
        message = self.login(username, password)
        print(message)

    def login_with_cookies(self, cookies_file):
        with open(cookies_file) as f:
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
        state, message = re.match(
            r".+(errorhandle_loginform|succeedhandle_loginform)\((.+)\,\s?\{.+", content
        ).groups()
        if state == "errorhandle_loginform":
            raise LoginError(message)

        cookies = json.dumps(self._session.cookies.get_dict())
        self.create_cookies_file(cookies)

        return message

    def create_cookies_file(self, cookies):
        if cookies:
            with open(COOKIES_FILE, "w") as f:
                f.write(cookies)

    def _get_content(self):
        url = self._url if getattr(self, "_url", None) else self.url
        resp = self._session.get(url)
        resp = resp.json()
        if not resp["Variables"]["member_username"]:
            print("登陆过期")
            self.login_with_password()
        self.content = resp["Variables"]

    def refresh(self):
        self._get_content()
