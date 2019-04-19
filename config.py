#!/usr/bin/env python3
# -*- coding: utf-8 -*-

COOKIES_FILE = "cookies.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0"
}

BASE_HOST = "bbs.saraba1st.com"
BASE_URL = "https://" + BASE_HOST + "/2b/"
BASE_API_URL = BASE_URL + "api/mobile/"
URL_FORUM = BASE_URL + "forum.php"
URL_LOGIN = (
    BASE_URL
    + "member.php?mod=logging&action=login&loginsubmit=yes&&handlekey=loginform&inajax=1"
)
URL_MEMBER = BASE_URL + "home.php?mod=space&do=profile&from=space"
