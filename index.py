#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys

from config import FORUM_LIST_KEY, URL_FORUM_LIST, URL_THREAD_LIST, RE_OPT
from forum import Forum
from stage1st import Stage1stClient
from util import colored


class Index(Stage1stClient):
    def __init__(self, sid=0, page=1):
        super().__init__(sid, page)
        self.data = {}

    def _build_url(self):
        return URL_FORUM_LIST

    def forums_list(self):
        return self.content.get(FORUM_LIST_KEY, [])

    def forums(self):
        forums_list = sorted(self.forums_list(), key=lambda x: -int(x["todayposts"]))
        for i, forum in enumerate(forums_list, start=1):
            self.data[str(i)] = forum["fid"]
            fobj = Forum(
                forum["fid"],
                name=forum["name"],
                description=forum.get("description", ""),
                threads_count=forum["threads"],
                posts=forum["posts"],
                todayposts=forum["todayposts"],
            )
            print(f"「{colored(i, 'red', attrs=['bold'])}」\t{fobj}")

    def terminal(self):
        self.forums()
        while True:
            ipt = input("论坛 $ ")
            if ipt:
                opt, args = RE_OPT.match(ipt).groups()
                if opt == "q":
                    break
                elif opt == "f":
                    self.refresh()
                    self.forums()
                elif opt == "e" or opt == "exit":
                    sys.exit(0)
                elif opt == "h" or opt == "help":
                    self.help()
                elif opt == "" and args:
                    fid = self.data.get(args)
                    if fid:
                        f = Forum(fid)
                        f.termianl()

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


if __name__ == "__main__":
    s = Index()
    s.terminal()
