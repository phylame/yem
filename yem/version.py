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
"""Version message of Yem"""

import time

NAME = "Yem"
FULL_NAME = "Yet an E-book Management"
VERSION_TUPLE = (1, 0, 0)
VERSION = ".".join(str(x) for x in VERSION_TUPLE)
RELEASE = "unstable"
VERSION_MSG = "{0} {1}-{2}".format(NAME, VERSION, RELEASE)
AUTHOR = "Peng Wan"
AUTHOR_EMAIL = "phylame@163.com"
DESCRIPTION = "Python e-books processing toolkit"
VENDOR = "Peng Wan, PW"
LICENSE = "Apache License, Version 2.0"
SOURCE = "https://github.com/phylame/yem"
RIGHTS = "Copyright (C) 2012-{0} {1}".format(time.localtime().tm_year, VENDOR)
