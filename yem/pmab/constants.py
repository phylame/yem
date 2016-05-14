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

import yem
import zipfile

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
KEY_XML_ENCODING = "pmab.xml.encoding"
KEY_COMMENT = "pmab.comment"
DEFAULT_COMMENT = "generated by {0} v{1}".format(yem.version.NAME, yem.version.VERSION)

# make configurations
TEXT_DIR = "text"
IMAGE_DIR = "images"
EXTRA_DIR = "extras"
ZIP_COMPRESSION = zipfile.ZIP_DEFLATED
TEXT_ENCODING = yem.PLATFORM_ENCODING
XML_ENCODING = "UTF-8"