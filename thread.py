#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys

from config import (
    REPLY_LIST_KEY,
    THREAD_KEY,
    URL_REPLY_LIST,
    URL_REPLY,
    BROWSER_URL_THREAD,
    PER_PAGE_REPLIES,
)
from reply import Reply
from stage1st import Stage1stClient
from util import check_attr, colored, cprint


class Thread(Stage1stClient):
    def __init__(
        self,
        tid,
        url=None,
        fid=None,
        author=None,
        authorid=None,
        subject=None,
        dateline=None,
        lastpost=None,
        lastposter=None,
        views=None,
        replies_count=None,
        message=None,
        page=1,
    ):
        super().__init__()
        self._key = THREAD_KEY
        self._child = REPLY_LIST_KEY
        self._tid = tid
        self._url = url
        self._fid = fid
        self._author = author
        self._authorid = authorid
        self._subject = subject
        self._dateline = dateline
        self._lastpost = lastpost
        self._lastposter = lastposter
        self._views = views
        self._replies_count = replies_count
        self._message = message
        self._cur_page = page
        self._index = {}

    @property
    def tid(self):
        return self._tid

    @property
    def cur_page(self):
        return self._cur_page

    @property
    def url(self):
        return self._url or URL_REPLY_LIST.format(self._tid, self._cur_page)

    @property
    def browser_url(self):
        return BROWSER_URL_THREAD.format(self._tid, self._cur_page)

    @property
    @check_attr("_fid")
    def fid(self):
        return self.content[self._key]["fid"]

    @property
    @check_attr("_author")
    def author(self):
        return self.content[self._key]["author"]

    @property
    @check_attr("_authorid")
    def authorid(self):
        return self.content[self._key]["authorid"]

    @property
    @check_attr("_subject")
    def subject(self):
        return self.content[self._key]["subject"]

    @property
    @check_attr("_dateline")
    def dateline(self):
        return self.content[self._key]["dateline"]

    @property
    @check_attr("_lastpost")
    def lastpost(self):
        return self.content[self._key]["lastpost"]

    @property
    @check_attr("_lastposter")
    def lastposter(self):
        return self.content[self._key]["lastposter"]

    @property
    @check_attr("_views")
    def views(self):
        return self.content[self._key]["views"]

    @property
    @check_attr("_replies_count")
    def replies_count(self):
        return int(self.content[self._key]["replies"])

    @property
    @check_attr("_message")
    def message(self):
        try:
            message = self.content[self._child]["postlist"][0]["message"]
        except KeyError:
            message = ""
        return message

    @property
    def max_page(self):
        return self.replies_count // PER_PAGE_REPLIES + 1

    @property
    def replies(self):
        if self.content is None:
            self._get_content()
        replies_list = self.content[self._child]
        cprint(f"\n{'* ' * 5} {self.subject} {' *' * 5}\n", "yellow", attrs=["bold"])
        for i, reply in enumerate(replies_list):
            self._index[str(i)] = reply["pid"]
            r = Reply(
                reply["pid"],
                reply["tid"],
                reply["author"],
                reply["authorid"],
                reply["dateline"],
                reply["message"],
                self.subject,
            )
            print(self._info(i, r))

    @property
    def all_replies(self):
        max_page = self.max_page
        for p in range(1, max_page + 1):
            if p == self._cur_page:
                content = self.content
            else:
                url = URL_REPLY_LIST.format(self._tid, p)
                resp = self._session.get(url)
                resp = resp.json()
                content = resp["Variables"]
            replies_list = content[self._child]
            for reply in replies_list:
                yield Reply(
                    reply["pid"],
                    reply["tid"],
                    reply["author"],
                    reply["authorid"],
                    reply["dateline"],
                    reply["message"],
                    self.subject,
                )

    def next_page(self):
        if self._cur_page < self.max_page:
            self._cur_page += 1
            self.refresh()

    def prev_page(self):
        if self._cur_page > 1:
            self._cur_page -= 1
            self.refresh()

    def jump_to(self, page):
        try:
            page = int(page)
        except ValueError:
            page = -1
        if page > 0:
            self._cur_page = min(page, self.max_page)
            self.refresh()

    def new_reply(self):
        print('请输入内容，2次Enter发送')
        lines = []
        enter = 0
        while enter < 2:
            line = input()
            if not line:
                enter += 1
            else:
                enter = 0
            lines.append(line)
        message = '\n'.join(lines[:-1])

        url = URL_REPLY.format(self.tid)
        data = {
            'formhash': self.formhash,
            'message': message,
        }

        resp = self.post(url=url, data=data)
        print(resp['Message']['messagestr'])

        self.refresh()

    def refresh(self):
        super().refresh()
        self._fid = None
        self._subject = None
        self._dateline = None
        self._lastpost = None
        self._lastposter = None
        self._views = None
        self._replies_count = None

    def termianl(self):
        self.replies
        while True:
            ipt = input(f"Thread {self._tid} {self._cur_page}/{self.max_page} $ ")
            if ipt:
                opt, args = re.match(r"\s*([a-z]*)\s*(\d*)", ipt).groups()
                if opt == "q":
                    break
                elif opt == "n":
                    self.next_page()
                    self.replies
                elif opt == "p":
                    self.prev_page()
                    self.replies
                elif opt == "j":
                    self.jump_to(args)
                    self.replies
                elif opt == "f":
                    self.refresh()
                    self.replies
                elif opt == "a":
                    print(self.browser_url)
                elif opt == "r":
                    self.new_reply()
                elif opt == "e":
                    sys.exit(0)
                elif opt == "h" or opt == "help":
                    self.help()
                else:
                    pass

    def help(self):
        print(
            """
                <operate> [args]
                <f>                 刷新
                <n>                 下一页
                <p>                 上一页
                <j> [page]          跳转到
                <a>                 显示网页地址
                <q>                 离开返回上一级
                <e>                 退出
                <h>                 显示帮助信息
            """
        )

    def _info(self, idx, reply_cls):
        return (
            f"「{colored(idx, 'red', attrs=['bold'])}」 {colored('=' * 50, 'yellow')}\n"
            f"{colored(reply_cls.dateline, 'green')}\t"
            f"{colored(reply_cls.author, 'cyan')}\n"
            f"{colored(reply_cls.message)}"
        )
