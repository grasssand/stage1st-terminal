#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from config import (
    REPLY_LIST_KEY,
    THREAD_KEY,
    URL_REPLY_LIST,
    URL_REPLY,
    URL_FAVOURITE,
    BROWSER_URL_THREAD,
    PER_PAGE_REPLIES,
    RE_OPT,
)
from reply import Reply
from stage1st import Stage1stClient
from util import check_attr, colored, cprint


class Thread(Stage1stClient):
    def __init__(
        self,
        tid,
        page=1,
        author=None,
        subject=None,
        dateline=None,
        views=None,
        replies_count=None,
        message=None,
        fid=None,
    ):
        super().__init__(sid=tid, page=page)
        self._author = author
        self._subject = subject
        self._dateline = dateline
        self._views = views
        self._replies_count = replies_count
        self._message = message
        self._fid = fid
        self.data = {}

    def __str__(self):
        return (
            f"{colored(self.dateline, 'green')}\t"
            f"{colored(self.author, 'cyan')} "
            f"({colored(self.replies_count, 'blue')} / {colored(self.views, 'magenta')})\n"
            f"{colored(self.subject, 'yellow')}\n"
            f"{'-' * 50}\n"
            f"{colored(self.message)}\n"
        )

    def _build_url(self):
        return URL_REPLY_LIST.format(self.id, self.page)

    def refresh(self):
        super().refresh()
        self._author = None
        self._subject = None
        self._dateline = None
        self._views = None
        self._replies_count = None
        self._message = None
        self.data = {}

        self.replies()

    @property
    @check_attr("_author")
    def author(self):
        return self.content[THREAD_KEY]["author"]

    @property
    @check_attr("_subject")
    def subject(self):
        return self.content[THREAD_KEY]["subject"]

    @property
    @check_attr("_dateline")
    def dateline(self):
        return self.content[THREAD_KEY]["dateline"]

    @property
    @check_attr("_views")
    def views(self):
        return self.content[THREAD_KEY]["views"]

    @property
    @check_attr("_replies_count")
    def replies_count(self):
        return int(self.content[THREAD_KEY]["replies"])

    @property
    @check_attr("_message")
    def message(self):
        replies_list = self.replies_list()
        try:
            message = replies_list["postlist"][0]["message"]
        except KeyError:
            message = ""
        return message

    @property
    def max_page(self):
        return self.replies_count // PER_PAGE_REPLIES + 1

    def replies_list(self):
        return self.content.get(REPLY_LIST_KEY)

    def browser_url(self):
        return BROWSER_URL_THREAD.format(self.id, self.page)

    def replies(self):
        cprint(
            f"\n{'* ' * 10} {self.subject} {self.page} {' *' * 10}\n",
            "yellow",
            attrs=["bold"],
        )

        replies_list = self.replies_list()
        while replies_list:
            i = str(len(replies_list))
            reply = replies_list.pop()
            self.data[i] = reply["pid"]
            robj = Reply(
                author=reply["author"],
                dateline=reply["dateline"],
                message=reply["message"],
                pid=reply["pid"],
                tid=self.id,
                subject=self.subject,
                fid=self._fid,
            )
            print(
                f"「{colored(i, 'red', attrs=['bold'])}」 {colored('=' * 50, 'yellow')}\n{robj}"
            )

        cprint(
            f"\n{'* ' * 10} {self.subject} {self.page} {' *' * 10}\n",
            "yellow",
            attrs=["bold"],
        )

    def next_page(self):
        if self.page < self.max_page:
            self.page += 1

    def prev_page(self):
        if self.page > 1:
            self.page -= 1

    def jump_to(self, page):
        if page > 0 and page != self.page:
            self.page = min(page, self.max_page)

    def new_reply(self):
        print("-- 请输入内容，2次Enter发送 --")
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        message = "\n".join(lines)

        url = URL_REPLY.format(self.id)
        data = {
            "formhash": self.formhash,
            "message": message,
        }

        resp = self.post(url=url, data=data)
        print(resp["Message"]["messagestr"])

        self.refresh()

    def collect(self):
        url = URL_FAVOURITE
        data = {"formhash": self.formhash, "id": self.id, "description": ""}
        resp = self.post(url=url, data=data)
        print(resp["Message"]["messagestr"])

    def termianl(self):
        self.replies()
        while True:
            ipt = input(f"Thread {self.id} {self.page}/{self.max_page} $ ")
            if ipt:
                opt, args = RE_OPT.match(ipt).groups()

                if opt == "q":
                    break
                elif opt == "f":
                    self.refresh()
                elif opt == "e" or opt == "exit":
                    sys.exit(0)
                elif opt == "h" or opt == "help":
                    self.help()
                elif opt == "n":
                    self.next_page()
                elif opt == "p":
                    self.prev_page()
                elif opt == "j":
                    if args:
                        self.jump_to(int(args))
                elif opt == "a":
                    print(self.browser_url())
                elif opt == "r":
                    self.new_reply()
                elif opt == "c":
                    self.collect()

    def help(self):
        print(
            """
                <operate> [args]
                <e>                 退出
                <q>                 返回上一级
                <h>                 帮助信息
                <f>                 刷新
                <r>                 回复
                <c>                 收藏
                <n>                 下一页
                <p>                 上一页
                <j> [page]          跳转到
                <a>                 显示网页地址
            """
        )
