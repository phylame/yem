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
"""Core of Yem"""

import datetime
from . import utils
from . import version

__version__ = version.VERSION
__author__ = version.AUTHOR

# keys of chapter attributes
TITLE = "title"
AUTHOR = "author"
COVER = "cover"
INTRO = "intro"
GENRE = "genre"
DATE = "date"
SUBJECT = "subject"
KEYWORD = "keyword"
PUBLISHER = "publisher"
RIGHTS = "rights"
LANGUAGE = "language"
ISBN = "isbn"
WORDS = "words"
VENDOR = "vendor"
BOOKBINDING = "bookbinding"

__all__ = ["TITLE", "AUTHOR", "COVER", "INTRO", "GENRE", "DATE", "SUBJECT", "KEYWORD", "PUBLISHER",
           "RIGHTS", "LANGUAGE", "ISBN", "WORDS", "VENDOR", "BOOKBINDING"]


class Chapter(object):
    def __init__(self, text=None, **kwargs):
        self.__attributes = {}
        self.__text = None
        self.__children = []
        self.__cleanups = set()
        if text is not None:
            self.text = text
        self.update_attributes(**kwargs)

    def set_attribute(self, name, value):
        self.__attributes[name] = utils.require_non_none(value, "value")

    def has_attribute(self, name):
        return name in self.__attributes

    def get_attribute(self, name, default=None):
        return self.__attributes.get(name, default)

    def string_attribute(self, name, default=""):
        value = self.get_attribute(name)
        if value is not None:
            return str(value)
        else:
            return default

    def remove_attribute(self, name):
        return self.__attributes.pop(name)

    def update_attributes(self, obj=None, **kwargs):
        if isinstance(obj, Chapter):
            self.__attributes.update(obj.__attributes)
        elif isinstance(obj, dict):
            self.__attributes.update(obj)
        elif obj is not None:
            raise TypeError(
                "'obj' expect 'None', '{0}' or 'dict.".format(utils.get_class_name(Chapter)))
        self.__attributes.update(**kwargs)

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
    def title(self):
        return self.string_attribute(TITLE, "")

    @title.setter
    def title(self, title):
        self.set_attribute(TITLE, title)

    @property
    def cover(self):
        return self.get_attribute(COVER, None)

    @cover.setter
    def cover(self, cover):
        if not isinstance(cover, utils.File):
            raise TypeError("'cover' require '{0}' object".format(utils.get_class_name(utils.File)))
        self.set_attribute(COVER, cover)

    @property
    def intro(self):
        return self.get_attribute(INTRO, None)

    @intro.setter
    def intro(self, intro):
        if not isinstance(intro, utils.Text):
            raise TypeError("'intro' require '{0}' object".format(utils.get_class_name(utils.Text)))
        self.set_attribute(INTRO, intro)

    @property
    def words(self):
        return self.get_attribute(WORDS, 0)

    @words.setter
    def words(self, words):
        if not isinstance(words, int):
            raise TypeError("'words' require 'int' value")
        self.set_attribute(WORDS, words)

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, text):
        if not isinstance(text, utils.Text):
            raise TypeError("'text' require '{0}' object".format(utils.get_class_name(utils.Text)))
        self.__text = text

    @staticmethod
    def _check_chapter_(chapter):
        if not isinstance(chapter, Chapter):
            raise TypeError("'{0}' object expected".format(utils.get_class_name(Chapter)))
        return chapter

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
            raise TypeError("index or '{0}' expected".format(utils.get_class_name(Chapter)))

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
        return "{0}@{1}:attributes={2}".format(
            utils.get_class_name(self.__class__), id(self), self.__attributes)

    def __len__(self):
        return len(self.__children)

    def __iter__(self):
        return iter(self.__children)

    def __getitem__(self, index):
        if isinstance(index, int):
            return self.chapter(index)
        elif isinstance(index, str):
            return self.get_attribute(index)
        else:
            raise TypeError("chapter index or attribute key required")

    def __setitem__(self, index, value):
        if isinstance(index, int):
            self.replace(index, value)
        elif isinstance(index, str):
            self.set_attribute(index, value)
        else:
            raise TypeError("chapter index or attribute key required")


class Book(Chapter):
    def __init__(self, **kwargs):
        super(Book, self).__init__(**kwargs)
        self.__extensions = {}

    @property
    def author(self):
        return str(self.get_attribute(AUTHOR, ""))

    @author.setter
    def author(self, author):
        self.set_attribute(AUTHOR, author)

    @property
    def genre(self):
        return str(self.get_attribute(GENRE, ""))

    @genre.setter
    def genre(self, genre):
        self.set_attribute(GENRE, genre)

    @property
    def date(self):
        return str(self.get_attribute(DATE, None))

    @date.setter
    def date(self, date):
        if not isinstance(date, datetime.date):
            raise TypeError(
                "'date' require '{0}' object".format(utils.get_class_name(datetime.date)))
        self.set_attribute(DATE, date)

    @property
    def subject(self):
        return str(self.get_attribute(SUBJECT, ""))

    @subject.setter
    def subject(self, subject):
        self.set_attribute(SUBJECT, subject)

    @property
    def publisher(self):
        return str(self.get_attribute(PUBLISHER, ""))

    @publisher.setter
    def publisher(self, publisher):
        self.set_attribute(PUBLISHER, publisher)

    @property
    def rights(self):
        return str(self.get_attribute(RIGHTS, ""))

    @rights.setter
    def rights(self, rights):
        self.set_attribute(RIGHTS, rights)

    @property
    def language(self):
        return str(self.get_attribute(LANGUAGE, ""))

    @language.setter
    def language(self, language):
        self.set_attribute(LANGUAGE, language)

    @property
    def vendor(self):
        return str(self.get_attribute(VENDOR, ""))

    @vendor.setter
    def vendor(self, vendor):
        self.set_attribute(VENDOR, vendor)

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


def read_book(path, format, arguments):
    pass


def write_book(book, path, format, argument):
    pass


__all__ += ["Chapter", "Book"]
