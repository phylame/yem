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
"""Core components of Yem"""

import os
import decimal
import datetime
import traceback
from .utils import *
from . import values
from . import version

__version__ = version.VERSION
__author__ = version.AUTHOR
del version


class YemError(Exception):
    pass


class Chapter(object):
    # predefined attributes
    attributes = {
        "date": (datetime.datetime, values.date),
        "pubdate": (datetime.datetime, values.pubdate),
        "cover": (File, values.cover),
        "binding": (str, values.binding),
        "keywords": ((str, list, tuple), values.keywords),
        "vendor": (str, values.vendor),
        "words": (int, values.words),
        "genre": (str, values.genre),
        "state": (str, values.state),
        "publisher": (str, values.pubdate),
        "intro": ((Text, str), values.intro),
        "isbn": (str, values.isbn),
        "author": ((str, list, tuple), values.author),
        "title": (str, values.title),
        "language": (str, values.language),
        "rights": (str, values.rights),
        "protagonist": ((str, list, tuple), values.protagonist),
        "pages": (int, values.pages),
        "translator": ((str, list, tuple), values.translator),
        "price": ((float, decimal.Decimal), values.price),
        "series": (str, values.series)
    }

    def __init__(self, text=None, **kwargs):
        self.__attributes = {}
        self.__text = None
        self.__children = []
        self.__cleanups = set()
        self.text = text
        self.update_attributes(**kwargs)
        if isinstance(self, Book):
            values.reset(self)

    def set_attribute(self, name, value):
        # if has attribute setting
        attr = Chapter.attributes.get(non_empty(name, "name"))
        self.__attributes[name] = with_type(non_none(value, name), attr[0], name) if attr else non_none(value, name)

    def update_attributes(self, obj=None, **kwargs):
        if isinstance(obj, Chapter):
            self.__attributes.update(obj.__attributes)
        elif isinstance(obj, dict):
            self.__attributes.update(obj)
        elif obj is not None:
            raise TypeError("'obj' require 'None', '{0}' or 'dict'.".format(class_name(Chapter)))
        self.__attributes.update(**kwargs)

    def has_attribute(self, name):
        return name in self.__attributes

    def get_attribute(self, name, default=None):
        # if has attribute setting
        attr = Chapter.attributes.get(non_empty(name, "name"))
        return self.__attributes.get(name, attr[1] if default is None and attr else default)

    def remove_attribute(self, name):
        return self.__attributes.pop(name)

    def clear_attributes(self):
        self.__attributes.clear()

    @property
    def attribute_count(self):
        return len(self.__attributes)

    @property
    def attribute_names(self):
        return self.__attributes.keys()

    @property
    def attribute_items(self):
        return self.__attributes.items()

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, text):
        if text is None:
            self.__text = text
        else:
            self.__text = with_type(text, (Text, str), "text")

    @staticmethod
    def _check_chapter_(chapter):
        return with_type(chapter, Chapter, "chapter")

    def append(self, chapter):
        self.__children.append(Chapter._check_chapter_(chapter))

    def insert(self, index, chapter):
        self.__children.insert(index, Chapter._check_chapter_(chapter))

    def remove(self, obj):
        if isinstance(obj, int):
            return self.__children.pop(obj)
        elif isinstance(obj, Chapter):
            self.__children.remove(obj)
        else:
            raise TypeError("index or '{0}' expected".format(class_name(Chapter)))

    def index(self, chapter):
        return self.__children.index(Chapter._check_chapter_(chapter))

    def chapter(self, index):
        return self.__children[index]

    def replace(self, index, chapter):
        self.__children[index] = Chapter._check_chapter_(chapter)

    def clear(self):
        self.__children.clear()

    @property
    def size(self):
        return len(self)

    @property
    def section(self):
        return self.size > 0

    def add_cleanup(self, work):
        self.__cleanups.add(work)

    def remove_cleanup(self, work):
        self.__cleanups.pop(work)

    def cleanup(self):
        """Invokes all registered cleanup works."""

        for sub in self:
            sub.cleanup()

        for work in self.__cleanups:
            work()

    def __repr__(self):
        return "{0}@{1}:attributes={2}".format(class_name(self.__class__), id(self), self.__attributes)

    def __len__(self):
        return len(self.__children)

    def __iter__(self):
        return iter(self.__children)

    def __getattribute__(self, item):
        # a registered attribute
        if item in Chapter.attributes:
            return self.get_attribute(item)
        else:
            return super(Chapter, self).__getattribute__(item)

    def __setattr__(self, key, value):
        # a registered attribute
        if key in Chapter.attributes:
            self.set_attribute(key, value)
        else:
            super(Chapter, self).__setattr__(key, value)

    def __getitem__(self, index):
        if isinstance(index, int):
            # get sub chapter
            return self.chapter(index)
        elif isinstance(index, str):
            # get attribute
            return self.get_attribute(index)
        else:
            raise TypeError("chapter index or attribute key required")

    def __setitem__(self, index, value):
        if isinstance(index, int):
            # replace sub chapter
            self.replace(index, value)
        elif isinstance(index, str):
            # set attribute
            self.set_attribute(index, value)
        else:
            raise TypeError("chapter index or attribute key required")


class Book(Chapter):
    def __init__(self, **kwargs):
        super(Book, self).__init__(**kwargs)
        self.__extensions = {}

    def set_extension(self, key, value):
        self.__extensions[key] = value

    def has_extension(self, key):
        return key in self.__extensions

    def get_extension(self, key, default=None):
        return self.__extensions.get(key, default)

    def remove_extension(self, key):
        return self.__extensions.pop(key)

    def clear_extensions(self):
        self.__extensions.clear()

    @property
    def extension_count(self):
        return len(self.__extensions)

    @property
    def extension_names(self):
        return self.__extensions.keys()

    @property
    def extension_items(self):
        return self.__extensions.items()

    def __repr__(self):
        return super(Book, self).__repr__() + ",extensions={0}".format(self.__extensions)


book_workers = {}


def get_worker(name, load_builtins=True):
    worker = book_workers.get(name)
    if worker is None:
        if load_builtins:
            worker = _load_builtin_worker(name)
        if worker is None:
            raise YemError("unsupported format: " + name)
    return worker


def set_worker(name, worker):
    book_workers[name] = worker


def _load_builtin_worker(name):
    mn = "".join(Book.__module__.rpartition(".")[:-1]) + name
    try:
        mod = __import__(mn, fromlist=[name])
    except ImportError:
        traceback.print_exc()
        return None
    worker = dict(name=name, parser=mod.parse, maker=mod.make, extensions=mod.extensions)
    set_worker(name, worker)
    return worker


def parse_book(path, format=None, **kwargs):
    worker = get_worker(os.path.splitext(path)[-1][1:] if not format else format)
    fp = open(path, "rb")
    book = None
    try:
        book = worker["parser"](fp, **kwargs)
        book.fp = fp
    except:
        traceback.print_exc()
        fp.close()
    return book


def make_book(book, path, format="pmab", **kwargs):
    worker = get_worker(format)
    if os.path.isdir(path):
        path = os.path.join(path, book.title + "." + worker["extensions"][0])
    with open(path, "wb") as fp:
        worker["maker"](book, fp, **kwargs)
    return path


__all__ = ["YemError", "Chapter", "Book", "parse_book", "make_book"]
