#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import getpass
import json
import os
import re
from abc import abstractmethod
from xml.etree import ElementTree

from requests_html import HTMLSession

from config import COOKIES_FILE, HEADERS, URL_LOGIN
from exception import LoginError, ResourceError


class Stage1stClient:
    def __init__(self, sid, page):
        self._id = sid
        self._page = page
        self._content = None
        self._uid = None
        self._formhash = None

        self._session = HTMLSession()
        self._session.headers.update(HEADERS)

        if os.path.isfile(COOKIES_FILE):
            self.login_with_cookies(COOKIES_FILE)
        else:
            self.login_with_password()

    def login_with_cookies(self, cookies_file):
        with open(cookies_file, "r") as f:
            cookies = f.read()
        ck = json.loads(cookies)
        self._session.cookies.update(ck)

    def login_with_password(self):
        username = input("用户名: ")
        password = getpass.getpass("密码: ")
        message = self.login(username, password)
        print(message)

    def login(self, username, password):
        data = {
            "cookietime": 2592000,
            "fastloginfield": "username",
            "username": username,
            "password": password,
        }
        resp = self.post(URL_LOGIN, data=data)
        content = ElementTree.fromstring(resp.content).text
        status, message = re.match(
            r".+(errorhandle_loginform|succeedhandle_loginform)\((.+)\,\s?\{.+", content
        ).groups()
        if status == "errorhandle_loginform":
            raise LoginError(message)

        cookies = json.dumps(self._session.cookies.get_dict())
        with open(COOKIES_FILE, "w") as f:
            f.write(cookies)

        return message

    @property
    def id(self):
        return self._id

    @property
    def page(self):
        return self._page

    @page.setter
    def page(self, val):
        if isinstance(val, int):
            self._page = val
            self.refresh()

    @abstractmethod
    def _build_url(self):
        return ""

    @property
    def content(self):
        if self._content is None:
            self._content = self._get_content()
        return self._content

    @property
    def uid(self):
        if self._uid is None:
            self._uid = self.content["member_uid"]
        return self._uid

    @property
    def formhash(self):
        if self._formhash is None:
            self._formhash = self.content["formhash"]
        return self._formhash

    def _get_content(self):
        url = self._build_url()
        resp = self.get(url, to_json=True)
        if not resp["Variables"]["member_username"]:
            print("登陆过期")
            self.login_with_password()

        return resp["Variables"]

    def get(self, url, to_json=True):
        resp = self._session.get(url)
        try:
            resp.raise_for_status()
            return resp.json() if to_json else resp.html
        except:
            raise ResourceError("请求失败")

    def post(self, url, data, to_json=True):
        resp = self._session.post(url, data)
        try:
            resp.raise_for_status()
            return resp.json() if to_json else resp.html
        except:
            raise ResourceError("请求失败")

    def refresh(self):
        self._content = None
