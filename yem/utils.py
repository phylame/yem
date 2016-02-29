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
"""Utilities for Yem"""

import os
import sys
import locale
import urllib.parse
import urllib.request
from . import version

__version__ = version.VERSION
__author__ = version.AUTHOR

# line separator of current system
_platform = sys.platform
if _platform.startswith("win"):
    LINE_SEPARATOR = "\r\n"
elif _platform.startswith("mac"):
    LINE_SEPARATOR = "\r"
else:
    LINE_SEPARATOR = "\n"
del _platform

# current platform encoding
ENCODING = locale.getpreferredencoding(False)

UNKNOWN_MIME = "application/octet-stream"

MIMES = {
    '.epub': 'application/epub+zip',
    '.zip': 'application/zip',
    '.txt': 'text/plain',
    '.pmab': 'application/pmab+zip',
    '.csv': 'text/csv',
    '.css': 'text/css',
    '.htm': 'text/html',
    '.html': 'text/html',
    '.xml': 'text/xml',
    '.svg': 'image/svg+xml',
    '.bmp': 'image/bmp',
    '.ico': 'image/x-icon',
    '.gif': 'image/gif',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpe': 'image/jpeg',
    '.jpeg': 'image/jpeg'
}


def get_mime(path):
    return MIMES.get(os.path.splitext(path)[1], "application/octet-stream")


def detect_mime(mime, name):
    return mime if mime else get_mime(name)


def require_non_none(o, name):
    if o is None:
        raise ValueError("'{0}' require not None".format(name))
    return o


def require_non_empty(s):
    if not isinstance(s, str):
        raise TypeError("'str' object required")
    if len(s) == 0:
        raise ValueError("unexpected empty string")
    return s


def get_class_name(clazz):
    return clazz.__module__ + "." + clazz.__name__


class File(object):
    def __init__(self, mime):
        self.__mime = require_non_empty(mime)

    @property
    def name(self):
        raise NotImplementedError("Implementation required")

    @property
    def mime(self):
        return self.__mime

    @property
    def content(self):
        raise NotImplementedError("Implementation required")

    def __repr__(self):
        return "{0};mime={1}".format(self.name, self.mime)

    # factory functions
    @staticmethod
    def for_path(path, mime=None):
        return _CommonFile(path, mime)

    @staticmethod
    def for_block(name, fp, offset, size, mime=None):
        return _BlockFile(name, fp, offset, size, mime)

    @staticmethod
    def for_url(url, mime=None):
        return _UrlFile(url, mime)

    @staticmethod
    def for_bytes(name, b, mime=None):
        return _ByteFile(name, b, mime)

    @staticmethod
    def empty_file(name="_empty_", mime=None):
        return _ByteFile(name, b"", detect_mime(mime, require_non_empty(name)))


class _CommonFile(File):
    def __init__(self, path, mime=None):
        super(_CommonFile, self).__init__(detect_mime(mime, require_non_empty(path)))
        self.__path = path

    @property
    def name(self):
        return self.__path

    @property
    def content(self):
        with open(self.__path, "rb") as fp:
            return fp.read()

    def __repr__(self):
        return "file://" + super(_CommonFile, self).__repr__()


class _BlockFile(File):
    def __init__(self, name, fp, offset, size, mime):
        super(_BlockFile, self).__init__(detect_mime(mime, require_non_empty(name)))
        if not hasattr(fp, "read"):
            raise TypeError("'fp' require file-like object")
        if fp.closed:
            raise ValueError("'fp' closed")
        if not fp.seekable():
            raise ValueError("'fp' is not seekable")
        self.__name = name
        self.__fp = fp
        self.__offset = offset
        self.__size = size

    @property
    def name(self):
        return self.__name

    @property
    def content(self):
        self.__fp.seek(self.__offset)
        return self.__fp.read(self.__size)

    def __repr__(self):
        return "block://{0};offset={1};size={2}".format(super(_BlockFile, self).__repr__(),
                                                        self.__offset, self.__size)


class _UrlFile(File):
    def __init__(self, url, mime=None):
        super(_UrlFile, self).__init__(detect_mime(mime, require_non_empty(url)))
        self.__url = url

    @property
    def name(self):
        return urllib.parse.urlsplit(self.__url).path.lstrip('/')

    @property
    def content(self):
        return urllib.request.urlopen(self.__url).read()


class _ByteFile(File):
    def __init__(self, name, b, mime):
        super(_ByteFile, self).__init__(detect_mime(mime, require_non_empty(name)))
        self._name_ = name
        if not isinstance(b, bytes):
            raise TypeError("'b' require 'bytes' object")
        self.__bytes = b

    @property
    def name(self):
        return self._name_

    @property
    def content(self):
        return self.__bytes

    def __repr__(self):
        return "bytes://" + super(_ByteFile, self).__repr__()


class Text(object):
    PLAIN = "plain"
    HTML = "html"

    def __init__(self, _type=PLAIN):
        self.__type = require_non_empty(_type)

    @property
    def type(self):
        return self.__type

    @property
    def text(self):
        raise NotImplementedError("Implementation required")

    @property
    def lines(self):
        return self.text.splitlines()

    def __repr__(self):
        return "{0}:{1}".format(self.__class__.__name__, self.type)

    def __str__(self):
        return self.text

    # factory functions
    @staticmethod
    def for_str(s, type=PLAIN):
        return _RawText(s, type)

    @staticmethod
    def for_file(file, encoding=ENCODING, type=PLAIN):
        return _FileText(file, encoding, type)

    @staticmethod
    def empty_text(type=PLAIN):
        return _RawText("", type)


class _RawText(Text):
    def __init__(self, _str, _type):
        super(_RawText, self).__init__(_type)
        self.__str = _str

    @property
    def text(self):
        return self.__str


class _FileText(Text):
    def __init__(self, file, encoding, _type):
        super(_FileText, self).__init__(_type)
        if not isinstance(file, File):
            raise TypeError("'file' expect '{0}' object".format(get_class_name(File)))
        self.__file = file
        self.__encoding = encoding if encoding else ENCODING

    @property
    def text(self):
        return self.__file.content.decode(self.__encoding)


__all__ = ["File", "Text", "LINE_SEPARATOR", "ENCODING", "MIMES", "UNKNOWN_MIME", "get_mime",
           "require_non_none", "require_non_empty", "get_class_name"]
