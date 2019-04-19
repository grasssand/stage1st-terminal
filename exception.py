#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class LoginException(Exception):
    def __init__(self, error):
        self.error = error

    def __repr__(self):
        return f"Login Fail: {self.error}"

    __str__ = __repr__
