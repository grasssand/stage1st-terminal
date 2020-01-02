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
    RE_OPT,
)
from stage1st import Stage1stClient
from thread import Thread
from util import check_attr, colored, cprint


class Forum(Stage1stClient):
    def __init__(
        self,
        fid,
        page=1,
        name=None,
        description=None,
        threads_count=None,
        posts=None,
        todayposts=None,
    ):
        super().__init__(fid, page)
        self._name = name
        self._description = description
        self._threads_count = threads_count
        self._posts = posts
        self.todayposts = todayposts if todayposts else 0
        self.data = {}

    def __str__(self):
        return (
            f"{self.name} ({colored(self.todayposts, 'green')})\t"
            f"{colored(self.description, 'yellow')}\r"
        )

    def _build_url(self):
        return URL_THREAD_LIST.format(self.id, self._page)

    def refresh(self):
        super().refresh()
        self._name = None
        self._description = None
        self._threads_count = None
        self._posts = None
        self.data = {}
        self.threads()

    @property
    @check_attr("_name")
    def name(self):
        return self.content[FORUM_KEY]["name"]

    @property
    @check_attr("_description")
    def description(self):
        return self.content[FORUM_KEY].get("description", "")

    @property
    @check_attr("_threads_count")
    def threads_count(self):
        return int(self.content[FORUM_KEY]["threads"])

    @property
    @check_attr("_posts")
    def posts(self):
        return self.content[FORUM_KEY]["posts"]

    @property
    def max_page(self):
        return self.threads_count // PER_PAGE_THREADS + 1

    def threads_list(self):
        return self.content.get(THREAD_LIST_KEY, [])

    def thread_types(self):
        return self.content["threadtypes"]["types"]

    def browser_url(self):
        return BROWSER_URL_FORUM.format(self.id, self.page)

    def threads(self):
        cprint(
            f"\n{'* ' * 20} {self.name} {self.page} {' *' * 20}\n",
            "yellow",
            attrs=["bold"],
        )
        threads_list = self.threads_list()
        for i, thread in enumerate(threads_list):
            self.data[str(i)] = thread["tid"]
            try:
                message = thread["reply"][0]["message"]
            except KeyError:
                message = ""
            tobj = Thread(
                thread["tid"],
                author=thread["author"],
                subject=thread["subject"],
                dateline=thread["dateline"],
                views=thread["views"],
                replies_count=thread["replies"],
                message=message,
                fid=self.id,
            )
            print(f"「{colored(i, 'red', attrs=['bold'])}」 {'=' * 50}\n{tobj}")

    def next_page(self):
        if self.page < self.max_page:
            self.page += 1
            self.threads()

    def prev_page(self):
        if self.page > 1:
            self.page -= 1
            self.threads()

    def jump_to(self, page):
        if page > 0 and page != self.page:
            self.page = min(page, self.max_page)
            self.threads()

    def new_thread(self):
        thread_types = self.thread_types()
        default_type_id, default_type_name = next(iter(thread_types.items()))

        print(self.thread_types())
        typeid = input(f"选择类别[{default_type_id}]: ")
        subject = input("主题: ")
        print("-- 请输入内容，2次Enter发送 --")
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        message = "\n".join(lines)

        try:
            typeid = int(typeid)
        except ValueError:
            typeid = int(default_type_id)

        url = URL_THREAD.format(self.id)
        data = {
            "formhash": self.formhash,
            "typeid": typeid,
            "subject": subject,
            "message": message,
        }

        resp = self.post(url=url, data=data)
        print(resp["Message"]["messagestr"])

        self.refresh()

    def termianl(self):
        self.threads()
        while True:
            ipt = input(f"{self.name} {self.page}/{self.max_page} $ ")
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
                    self.new_thread()
                elif opt == "" and args:
                    tid = self.data.get(args)
                    if tid:
                        t = Thread(tid)
                        t.termianl()

    def help(self):
        print(
            """
                <operate> [args]
                <e>                 退出
                <q>                 返回上一级
                <h>                 帮助信息
                <f>                 刷新
                [Thread Index]      进入相应主题
                <r>                 发帖
                <n>                 下一页
                <p>                 上一页
                <j> [page]          跳转到
                <a>                 显示网页地址
            """
        )
