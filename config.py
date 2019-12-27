#!/usr/bin/env python3
# -*- coding: utf-8 -*-

PER_PAGE_THREADS = 20
PER_PAGE_REPLIES = 20

COOKIES_FILE = "cookies.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0"
}

BASE_HOST = "bbs.saraba1st.com"
BASE_URL = "https://" + BASE_HOST + "/2b/"
BASE_API_URL = BASE_URL + "api/mobile/"
URL_LOGIN = (
    BASE_URL
    + "member.php?mod=logging&action=login&loginsubmit=yes&&handlekey=loginform&inajax=1"
)
URL_MEMBER = BASE_URL + "home.php?mod=space&do=profile&from=space"
URL_FORUM_LIST = BASE_API_URL + "index.php?module=forumindex"
URL_THREAD_LIST = (
    BASE_API_URL
    + "index.php?module=forumdisplay&version=4&filter=typeid&tpp="
    + str(PER_PAGE_THREADS)
    + "&fid={}&page={}"
)
URL_THREAD = BASE_API_URL + "index.php?module=newthread&extra=&topicsubmit=yes&fid={}"
URL_REPLY_LIST = (
    BASE_API_URL
    + "index.php?module=viewthread&version=1&ppp="
    + str(PER_PAGE_REPLIES)
    + "&tid={}&page={}"
)
URL_REPLY = BASE_API_URL + "index.php?module=sendreply&replysubmit=yes&tid={}"
URL_FAVOURITE = BASE_API_URL + "index.php?module=favthread&favoritesubmit=yes"

BROWSER_URL_FORUM = "https://bbs.saraba1st.com/2b/forum-{}-{}.html"
BROWSER_URL_THREAD = "https://bbs.saraba1st.com/2b/thread-{}-{}-1.html"

FORUM_LIST_KEY = "forumlist"
FORUM_KEY = "forum"
THREAD_LIST_KEY = "forum_threadlist"
THREAD_KEY = "thread"
REPLY_LIST_KEY = "postlist"
