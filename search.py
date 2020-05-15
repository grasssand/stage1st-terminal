#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from config import URL_SEARCH, PER_PAGE_THREADS, RE_OPT
from stage1st import Stage1stClient
from thread import Thread
from util import colored, cprint


class Search(Stage1stClient):
    def __init__(self, sid=0, page=1):
        super().__init__(sid, page)

        print("「1」帖子, 「2」用户")
        self.mod = "user" if input("搜索[1]: ") == "2" else "forum"
        self.srchtxt = input("关键词: ")
        self.data = {}

    def _build_url(self):
        return URL_SEARCH.format(self.mod, self.page)

    def threads(self):
        title = self.html.find("h2", first=True).text
        threads = self.parse_html(self.html)
        cprint(
            f"\n{'* ' * 20} {title} {' *' * 20}\n", "yellow", attrs=["bold"],
        )

    def parse_html(self, html):
        threads = html.find("#threadlist .pbw")
        for thread in threads:
            tid = thread.attrs["id"]
            subject = thread.find(".xs3", first=True).text
            ps = thread.find("p")
            replies_count, views = ps[0].search(">{} 个回复 - {} 次查看")
            message = ps[1].text
            dateline, author, forum = ps[2].find("span")
            fid = forum.search("forum-{}-1.html")[0]

            yield Thread(
                tid,
                author=author.text,
                subject=subject,
                dateline=dateline.text,
                views=views,
                replies_count=replies_count,
                message=message,
                fid=fid,
            )

    def terminal(self):
        self.threads()
        while True:
            ipt = input("论坛 $ ")
            if ipt:
                opt, args = RE_OPT.match(ipt).groups()
                if opt == "q":
                    break
                elif opt == "e" or opt == "exit":
                    sys.exit(0)
                elif opt == "h" or opt == "help":
                    self.help()
                elif opt == "" and args:
                    tid = self.data.get(args)
                    if tid:
                        t = Thread(tid)
                        t.termianl()

    def help(self):
        print(
            """
                <operate> [args]
                <q>                 返回上一级
                <e>                 退出
                <h>                 帮助信息
                <f>                 刷新
                [Forum Index]       进入相应论坛
                <s>                 搜索
            """
        )
