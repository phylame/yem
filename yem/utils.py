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
del version

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


def get_mime(name):
    return MIMES.get(os.path.splitext(name)[1], "application/octet-stream")


def detect_mime(mime, name):
    return mime if mime else get_mime(name)


def non_none(obj, name):
    if obj is None:
        raise ValueError("'{0}' require non-none value".format(name))
    return obj


def non_empty(str, name):
    if not isinstance(str, __builtins__.str):
        raise TypeError("'{0}' require 'str' object".format(name))
    if len(str) == 0:
        raise ValueError("'{0}' require non-empty string")
    return str


def class_name(clazz):
    return clazz.__module__ + "." + clazz.__name__


def valid_type(obj, clazz, name):
    if not isinstance(obj, clazz):
        raise TypeError("'{0}' require '{1}' object".format(name, class_name(clazz)))
    return obj


class File(object):
    def __init__(self, mime):
        self.__mime = non_empty(mime, "mime")

    @property
    def name(self):
        raise NotImplementedError("Implementation required")

    @property
    def mime(self):
        return self.__mime

    @property
    def data(self):
        raise NotImplementedError("Implementation required")

    def __repr__(self):
        return "{0};mime={1}".format(self.name, self.mime)

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
    def for_bytes(name, bytes, mime=None):
        return _ByteFile(name, bytes, mime)

    @staticmethod
    def empty_file(name="_empty_", mime=None):
        return _ByteFile(name, b"", mime)


class _CommonFile(File):
    def __init__(self, path, mime=None):
        super(_CommonFile, self).__init__(detect_mime(mime, non_empty(path, "path")))
        self.__path = path

    @property
    def name(self):
        return self.__path

    @property
    def data(self):
        with open(self.__path, "rb") as fp:
            return fp.read()

    def __repr__(self):
        return "file://" + super(_CommonFile, self).__repr__()


class _BlockFile(File):
    def __init__(self, name, fp, offset, size, mime):
        super(_BlockFile, self).__init__(detect_mime(mime, non_empty(name, "name")))
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
    def data(self):
        self.__fp.seek(self.__offset)
        return self.__fp.read(self.__size)

    def __repr__(self):
        return "block://{0};offset={1};size={2}".format(super(_BlockFile, self).__repr__(), self.__offset, self.__size)


class _UrlFile(File):
    def __init__(self, url, mime=None):
        super(_UrlFile, self).__init__(detect_mime(mime, non_empty(url, "url")))
        self.__url = url

    @property
    def name(self):
        return urllib.parse.urlsplit(self.__url).path.lstrip("/")

    @property
    def data(self):
        return urllib.request.urlopen(self.__url).read()


class _ByteFile(File):
    def __init__(self, name, bytes, mime):
        super(_ByteFile, self).__init__(detect_mime(mime, non_empty(name, "name")))
        self._name_ = name
        self.__bytes = valid_type(bytes, __builtins__.bytes, "bytes")

    @property
    def name(self):
        return self._name_

    @property
    def data(self):
        return self.__bytes

    def __repr__(self):
        return "bytes://" + super(_ByteFile, self).__repr__()


class Text(object):
    PLAIN = "plain"
    HTML = "html"

    def __init__(self, type=PLAIN):
        self.__type = non_empty(type, "type")

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
    def for_string(str, type=PLAIN):
        return _RawText(str, type)

    @staticmethod
    def for_file(file, encoding=ENCODING, type=PLAIN):
        return _FileText(file, encoding, type)

    @staticmethod
    def empty_text(type=PLAIN):
        return _RawText("", type)


class _RawText(Text):
    def __init__(self, str, type):
        super(_RawText, self).__init__(type)
        self.__str = non_none(str, "str")

    @property
    def text(self):
        return self.__str


class _FileText(Text):
    def __init__(self, file, encoding, type):
        super(_FileText, self).__init__(type)
        self.__file = valid_type(file, File, "file")
        self.__encoding = encoding if encoding else ENCODING

    @property
    def text(self):
        return self.__file.data.decode(self.__encoding)


__all__ = ["File", "Text", "LINE_SEPARATOR", "ENCODING", "MIMES", "UNKNOWN_MIME", "get_mime", "non_none",
           "non_empty", "class_name", "valid_type"]
