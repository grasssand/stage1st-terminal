#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys

from config import (
    FORUM_KEY,
    THREAD_LIST_KEY,
    URL_REPLY_LIST,
    URL_THREAD_LIST,
    URL_THREAD,
    PER_PAGE_THREADS,
    BROWSER_URL_FORUM,
)
from stage1st import Stage1stClient
from thread import Thread
from util import check_attr, colored


class Forum(Stage1stClient):
    def __init__(
        self,
        fid,
        url=None,
        name=None,
        description=None,
        threads_count=None,
        posts=None,
        todayposts=None,
        thread_types=None,
        page=1,
    ):
        super().__init__()
        self._key = FORUM_KEY
        self._child = THREAD_LIST_KEY
        self._fid = fid
        self._url = url
        self._name = name
        self._description = description
        self._threads_count = threads_count
        self._posts = posts
        self._todayposts = todayposts
        self._thread_types = thread_types
        self._cur_page = page
        self._index = {}

    @property
    def fid(self):
        return self._fid

    @property
    def cur_page(self):
        return self._cur_page

    @property
    def url(self):
        return self._url or URL_THREAD_LIST.format(self._fid, self._cur_page)

    @property
    def browser_url(self):
        return BROWSER_URL_FORUM.format(self._fid, self._cur_page)

    @property
    @check_attr("_name")
    def name(self):
        return self.content[self._key]["name"]

    @property
    @check_attr("_description")
    def description(self):
        return self.content[self._key].get("description", "")

    @property
    @check_attr("_threads_count")
    def threads_count(self):
        return int(self.content[self._key]["threads"])

    @property
    @check_attr("_posts")
    def posts(self):
        return self.content[self._key]["posts"]

    @property
    @check_attr("_thread_types")
    def thread_types(self):
        return self.content["threadtypes"]["types"]

    @property
    def todayposts(self):
        return self._todayposts

    @property
    def max_page(self):
        return self.threads_count // PER_PAGE_THREADS + 1

    @property
    def threads(self):
        print(f"{colored('*' * 80, 'yellow', attrs=['bold'])}\n")

        if self.content is None:
            self._get_content()
        threads_list = self.content[self._child]
        for i, thread in enumerate(threads_list):
            self._index[str(i)] = thread["tid"]
            try:
                message = thread["reply"][0]["message"]
            except KeyError:
                message = ""
            t = Thread(
                thread["tid"],
                URL_REPLY_LIST.format(thread["tid"], 1),
                self._fid,
                thread["author"],
                thread["authorid"],
                thread["subject"],
                thread["dateline"],
                thread["lastpost"],
                thread["lastposter"],
                thread["views"],
                thread["replies"],
                message,
            )
            print(self._info(i, t))

    def thread(self, tid):
        return Thread(tid)

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

    def new_thread(self):
        default_type_id, default_type_name = next(iter(self.thread_types.items()))

        print(self.thread_types)
        typeid = input(f"选择类别[{default_type_id}]: ")
        subject = input("主题: ")
        print("-- 请输入内容，2次Enter发送 --")
        lines = []
        enter = 0
        while enter < 2:
            line = input()
            if not line:
                enter += 1
            else:
                enter = 0
            lines.append(line)
        message = "\n".join(lines[:-1])

        try:
            typeid = int(typeid)
        except:
            typeid = int(default_type_id)

        url = URL_THREAD.format(self.fid)
        data = {
            "formhash": self.formhash,
            "typeid": typeid,
            "subject": subject,
            "message": message,
        }

        resp = self.post(url=url, data=data)
        print(resp["Message"]["messagestr"])

        self.refresh()

    def refresh(self):
        super().refresh()
        self._name = None
        self._description = None
        self._threads = None
        self._posts = None

    def termianl(self):
        self.threads
        while True:
            ipt = input(f"{self.name} {self._cur_page}/{self.max_page} $ ")
            if ipt:
                opt, args = re.match(r"\s*([a-z]*)\s*(\d*)", ipt).groups()
                if opt == "q":
                    break
                elif opt == "t":
                    t = self.thread(args)
                    t.termianl()
                elif opt == "n":
                    self.next_page()
                    self.threads
                elif opt == "p":
                    self.prev_page()
                    self.threads
                elif opt == "j":
                    self.jump_to(args)
                    self.threads
                elif opt == "f":
                    self.refresh()
                    self.threads
                elif opt == "a":
                    print(self.browser_url)
                elif opt == "r":
                    self.new_thread()
                elif opt == "e":
                    sys.exit(0)
                elif opt == "h" or opt == "help":
                    self.help()
                elif opt == "" and args:
                    tid = self._index.get(args)
                    if tid is not None:
                        t = self.thread(tid)
                        t.termianl()
                else:
                    pass

    def help(self):
        print(
            """
                <operate> [args]
                [Thread Index]      进入相应主题
                <r>                 发帖
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

    def _info(self, idx, thread_cls):
        return (
            f"「{colored(idx, 'red', attrs=['bold'])}」 {'=' * 50}\n"
            f"{colored(thread_cls.dateline, 'green')}\t"
            f"{colored(thread_cls.author, 'cyan')} "
            f"({colored(thread_cls.replies_count, 'blue')} / {colored(thread_cls.views, 'magenta')})\n"
            f"{colored(thread_cls.subject, 'yellow')}\n"
            f"{'-' * 50}\n"
            f"{colored(thread_cls.message)}\n"
        )
