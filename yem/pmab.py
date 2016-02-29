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

import os
import sys
import zipfile
from . import utils
from datetime import date
from xml.dom.minidom import Document

# MIME type for PMAB
MIME_FILE = "mimetype"
MT_PMAB = b"application/pmab+zip"

# PBM(PMAB Book Metadata)
PBM_FILE = "book.xml"
PBM_XML_NS = "http:#phylame.pw/format/pmab/pbm"

# PBC(PMAB Book Content)
PBC_FILE = "content.xml"
PBC_XML_NS = "http:#phylame.pw/format/pmab/pbc"

# keys of maker configurations
KEY_TEXT_ENCODING = "pmab.text.encoding"
KEY_COMMENT = "pmab.comment"

# make configurations
TEXT_DIR = "text"
IMAGE_DIR = "images"
EXTRA_DIR = "extra"
ZIP_COMPRESSION = zipfile.ZIP_DEFLATED
TEXT_ENCODING = sys.getdefaultencoding()
XML_ENCODING = "UTF-8"


def make(book, path, args=None):
    if os.path.isdir(path):
        file = os.path.join(path, book.title + ".pmab")
    else:
        ext = os.path.splitext(path)[-1]
        if not ext:
            file = path + ".pmab"
        else:
            file = path

    if args is None:
        args = {}

    with zipfile.ZipFile(file, "w", zipfile.ZIP_DEFLATED) as zf:
        comment = args.get(KEY_COMMENT, None)
        # comment
        if comment:
            zf.comment = comment.encode(TEXT_ENCODING)

        # MANIFEST
        zf.writestr(MIME_FILE, MT_PMAB)

        encoding = args.get(KEY_TEXT_ENCODING, TEXT_ENCODING)

        # pbm
        write_pbm(zf, book, encoding)

        # pbc
        write_pbc(zf, book, encoding)


def write_pbm(zf, book, encoding):
    doc = Document()
    pbm = doc.createElement('pbm')
    doc.appendChild(pbm)
    pbm.setAttribute('version', '3.0')
    pbm.setAttribute('xmlns', PBM_XML_NS)
    write_items(zf, doc, pbm, 'attributes', book.attribute_items, encoding, '')
    write_items(zf, doc, pbm, 'extensions', book.extension_items, encoding, '')
    zf.writestr(PBM_FILE,
                doc.toprettyxml(indent='  ', encoding=XML_ENCODING))


def _extension_of_type(type):
    if type == utils.Text.PLAIN:
        return ".txt"
    elif type == utils.Text.HTML:
        return ".html"
    else:
        return ".txt"


def write_text(zf, text, name, encoding):
    path = TEXT_DIR + '/' + name + _extension_of_type(text.type)
    zf.writestr(path, text.text.encode(encoding))
    return path


def write_file(zf, file, name):
    if file.mime.startswith("image/"):
        path = IMAGE_DIR
    else:
        path = EXTRA_DIR
    path += '/' + name + os.path.splitext(file.name)[1]
    zf.writestr(path, file.text)
    return path


def write_items(zf, doc, parent, name, items, encoding, prefix):
    elem = doc.createElement(name)
    parent.appendChild(elem)
    for k, v in items:
        if isinstance(v, str):
            type = 'str'
            text = v
        elif isinstance(v, utils.Text):
            type = 'text/' + v.type + ';encoding=' + encoding
            text = write_text(zf, v, prefix + k, encoding)
        elif isinstance(v, utils.File):
            type = v.mime
            text = write_file(zf, v, prefix + k)
        elif isinstance(v, date):
            type = 'datetime;format=yyyy-M-d'
            text = '{0}-{1}-{2}'.format(v.year, v.month, v.day)
        elif isinstance(v, bool):
            type = 'bool'
            text = str(v).lower()
        elif isinstance(v, int):
            type = 'int'
            text = str(v)
        elif isinstance(v, float):
            type = 'real'
            text = str(v)
        else:
            type = 'str'
            text = str(v)
        item = doc.createElement('item')
        item.setAttribute('name', k)
        item.setAttribute('type', type)
        item.appendChild(doc.createTextNode(text))
        elem.appendChild(item)


def write_chapter(ch, zf, doc, parent, encoding, suffix):
    base = 'chapter-' + suffix
    elem = doc.createElement('chapter')
    parent.appendChild(elem)
    write_items(zf, doc, elem, 'attributes', ch.attribute_items, encoding,
                base + '-')

    content = ch.text
    if isinstance(content, utils.Text):
        ct = doc.createElement("content")
        elem.appendChild(ct)
        ct.setAttribute('type',
                        'text/' + content.type + ';encoding=' + encoding)
        ct.appendChild(
                doc.createTextNode(write_text(zf, content, base, encoding)))

    for i, sub in enumerate(ch):
        write_chapter(sub, zf, doc, elem, encoding, suffix + '-' + str(i + 1))


def write_pbc(zf, book, encoding):
    doc = Document()
    pbc = doc.createElement('pbc')
    doc.appendChild(pbc)
    pbc.setAttribute('version', '3.0')
    pbc.setAttribute('xmlns', PBC_XML_NS)

    toc = doc.createElement('toc')
    pbc.appendChild(toc)

    for i, sub in enumerate(book):
        write_chapter(sub, zf, doc, toc, encoding, str(i + 1))

    zf.writestr(PBC_FILE,
                doc.toprettyxml(indent='  ', encoding=XML_ENCODING))
