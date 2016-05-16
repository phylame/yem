#
# Copyright 2014-2016 Peng Wan <phylame@163.com>
#
# This file is part of Yem.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Constants and value for Yem"""

import locale
import datetime
from . import version

__version__ = version.VERSION
__author__ = version.AUTHOR

GENRES = (
    "都市", "言情", "职场", "玄幻", "奇幻", "武侠", "仙侠",
    "悬疑", "推理", "历史", "军事", "科幻", "灵异", "游戏",
    "竞技", "体育", "穿越", "修真", "网游", "文学")

STATES = ("全本", "连载", "未完")

# default attribute values
date = datetime.datetime.now()
pubdate = None
cover = None
binding = None
keywords = None
genre = GENRES[0]
state = STATES[0]
publisher = None
intro = None
isbn = None
author = None
protagonist = None
series = None
translator = None
title = ""
pages = 0
words = 0
price = 0.0
language = locale.getdefaultlocale()[0]
rights = "(C) {0} {1}".format(date.year, version.VENDOR)
vendor = "{0} v{1}".format(version.NAME, version.VERSION)

del version


def reset(book):
    book.date = date
    book.genre = genre
    book.state = state
    book.language = language
    book.rights = rights
    book.vendor = vendor
