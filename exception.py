#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys


class APIError(Exception):
    def __init__(self, message):
        self.args = (f"{type(self).__name__}: {message}",)
        sys.exit(self)


class LoginError(APIError):
    pass


class ResourceError(APIError):
    pass
