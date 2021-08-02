# Copyright 2021 The KaiJIN Authors. All Rights Reserved.
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
# ==============================================================================
import os
import time
import logging
from datetime import datetime


class Logger():
  r"""Logger helper"""

  def __init__(self):
    self._initialized = False
    self._start_timer = time.time()
    self._logger = None

  @property
  def logger(self):
    if self._logger is None:
      temp = 'tw.{}.log'.format(datetime.strftime(datetime.now(), '%y%m%d%H%M%S'))
      self.init(temp, './')
      self.warn(f'Initialize a default logger <{temp}>.')
    return self._logger

  def is_init(self):
    return self._initialized

  def init(self, name, output_dir, stdout=True):
    if self._initialized:
      return

    r"""init the logger"""
    logging.root.handlers = []
    logging.basicConfig(format='%(message)s', level=logging.DEBUG, filename=os.path.join(output_dir, name))
    self._logger = logging.getLogger(name)
    if stdout:
      ch = logging.StreamHandler()
      ch.setLevel(logging.DEBUG)
      ch.setFormatter(logging.Formatter('%(message)s'))
      self._logger.addHandler(ch)
    self._initialized = True

  def _print(self, show_type, content):
    r"""Format print string"""
    str_date = '[' + datetime.strftime(datetime.now(), '%y.%m.%d %H:%M:%S') + '] '
    self.logger.info(str_date + show_type + ' ' + content)

  def sys(self, content):
    self._print('[SYS]', content)

  def warn(self, content):
    self._print('[WAN]', content)

  def info(self, content):
    self._print('[INF]', content)

  def cfg(self, content):
    self._print('[CFG]', content)

  def error(self, content):
    self._print('[ERR]', content)
    exit(-1)

  def server(self, content):
    self._print('[SERVER]', content)

  def client(self, content):
    self._print('[CLIENT]', content)

  def tic(self):
    self._start_timer = time.time()

  def toc(self):
    return (time.time() - self._start_timer) * 1000

  def tick(self):
    return time.time()

  def duration(self, start_time, end_time):
    return (end_time - start_time) * 1000


logger = Logger()
