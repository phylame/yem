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

import datetime
import os
from xml.dom import minidom

from .constants import *


def make(book, file, **kwargs):
    text_encoding = kwargs.get(KEY_TEXT_ENCODING, TEXT_ENCODING)
    xml_encoding = kwargs.get(KEY_XML_ENCODING, XML_ENCODING)
    with zipfile.ZipFile(file, "w") as zf:
        zf.comment = kwargs.get(KEY_COMMENT, DEFAULT_COMMENT).encode(yem.PLATFORM_ENCODING)
        zf.writestr(MIME_FILE, MT_PMAB)
        # pbm
        write_pbm(zf, book, text_encoding, xml_encoding)
        # pbc
        write_pbc(zf, book, text_encoding, xml_encoding)


def pretty_xml(doc, encoding):
    return doc.toprettyxml(indent="\t", newl=yem.LINE_SEPARATOR, encoding=encoding)


def write_pbm(zf, book, text_encoding, xml_encoding):
    doc = minidom.Document()
    pbm = doc.createElement('pbm')
    doc.appendChild(pbm)
    pbm.setAttribute('version', '3.0')
    pbm.setAttribute('xmlns', PBM_XML_NS)
    write_items(zf, doc, pbm, 'attributes', book.attribute_items, text_encoding, "")
    write_items(zf, doc, pbm, 'extensions', book.extension_items, text_encoding, "")
    zf.writestr(PBM_FILE, pretty_xml(doc, xml_encoding))


def write_pbc(zf, book, text_encoding, xml_encoding):
    doc = minidom.Document()
    pbc = doc.createElement('pbc')
    doc.appendChild(pbc)
    pbc.setAttribute('version', '3.0')
    pbc.setAttribute('xmlns', PBC_XML_NS)

    toc = doc.createElement('toc')
    pbc.appendChild(toc)

    for index, chapter in enumerate(book):
        write_chapter(chapter, zf, doc, toc, text_encoding, str(index + 1))

    zf.writestr(PBC_FILE, pretty_xml(doc, xml_encoding))


def write_items(zf, doc, parent, name, items, encoding, prefix):
    group = doc.createElement(name)
    parent.appendChild(group)
    for k, v in items:
        if isinstance(v, str):
            type = 'str'
            text = v
        elif isinstance(v, yem.Text):
            type = 'text/' + v.type + ';encoding=' + encoding
            text = write_text(zf, v, prefix + k, encoding)
        elif isinstance(v, yem.File):
            type = v.mime
            text = write_file(zf, v, prefix + k)
        elif isinstance(v, datetime.datetime):
            type = 'datetime;format=yyyy-M-d H:m:S'
            text = v.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(v, datetime.date):
            type = 'datetime;format=yyyy-M-d'
            text = v.strftime("%Y-%m-%d")
        elif isinstance(v, datetime.time):
            type = 'datetime;format=H:m:S'
            text = v.strftime("%H:%M:%S")
        elif isinstance(v, bool):
            type = 'bool'
            text = str(v).lower()
        elif isinstance(v, int):
            type = 'int'
            text = str(v)
        elif isinstance(v, float):
            type = 'real'
            text = str(v)
        elif isinstance(v, (list, tuple, set)):
            type = "str"
            text = ";".join(v)
        else:
            type = 'str'
            text = str(v)
        item = doc.createElement('item')
        item.setAttribute('name', k)
        item.setAttribute('type', type)
        item.appendChild(doc.createTextNode(text))
        group.appendChild(item)


def write_text(zf, text, name, encoding):
    path = TEXT_DIR + '/' + name + extension_for_text(text)
    zf.writestr(path, text.text.encode(encoding))
    return path


def write_file(zf, file, name):
    if file.mime.startswith("image/"):
        path = IMAGE_DIR
    else:
        path = EXTRA_DIR
    path += '/' + name + os.path.splitext(file.name)[1]
    zf.writestr(path, file.data)
    return path


def extension_for_text(text):
    if text.type == yem.Text.HTML:
        return ".html"
    else:
        return ".txt"


def write_chapter(chapter, zf, doc, parent, encoding, suffix):
    base = 'chapter-' + suffix
    elem = doc.createElement('chapter')
    parent.appendChild(elem)
    write_items(zf, doc, elem, 'attributes', chapter.attribute_items, encoding, base + '-')

    content = chapter.text
    if isinstance(content, yem.Text):
        ct = doc.createElement("content")
        elem.appendChild(ct)
        ct.setAttribute('type', 'text/' + content.type + ';encoding=' + encoding)
        ct.appendChild(doc.createTextNode(write_text(zf, content, base, encoding)))

    for index, sub in enumerate(chapter):
        write_chapter(sub, zf, doc, elem, encoding, suffix + '-' + str(index + 1))
