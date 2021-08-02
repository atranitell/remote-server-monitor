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
import argparse
import socket
import json

from .tfevent import TFEventAccumulator
from .logger import logger


class DaemonClient():

  def __init__(self):
    logger.init('daemon.client.log', './')
    logger.info('start client daemon.')

  def start(self, ip, port, mode='all', verbose=True):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))

    # recv data
    bufs = bytes()
    while True:
      buf = s.recv(1024)
      if len(buf) == 0:
        break
      bufs += buf
    data = json.loads(bufs.decode())

    # print mode
    if verbose and mode == 'all':
      logger.info(json.dumps(data, indent=2))
    elif verbose and mode == 'cpu':
      logger.info(json.dumps(data['cpu'], indent=2))
    elif verbose and mode == 'gpu':
      logger.info(json.dumps(data['gpu'], indent=2))

    return data

  def start_file(self, file, mode='all'):
    machines = []
    with open(file) as fp:
      for line in fp:
        ip, port = line.replace('\n', '').split(':')
        machines.append((ip, int(port), mode, False))

    results = []
    for m in machines:
      results.append((m, self.start(*m)))

    def sep(length=200):
      return '\n' + '-' * length

    s = sep(200)

    if mode in ['all', 'cpu']:
      s += '\n{:^20}{:^20}{:^20}{:^20}{:^20}{:^20}{:^20}{:^20}{:^20}{:^20}'.format(
          'ip', 'port', 'cpu_count', 'cpu_current_freq', 'cpu_percent',
          'memory_total(GB)', 'memory_used(GB)', 'memory_free(GB)', 'memory_percent(GB)', 'memory_shared(GB)')
      s += sep(200)
      for res in results:
        m, data = res[0], res[1]
        s += '\n{:^20}{:^20}{:^20}{:^20}{:^20}{:^20}{:^20}{:^20}{:^20}{:^20}'.format(
            m[0], m[1],
            data['cpu']['cpu_count'],
            data['cpu']['cpu_current_freq'],
            data['cpu']['cpu_percent'],
            data['cpu']['memory_total'],
            data['cpu']['memory_used'],
            data['cpu']['memory_free'],
            data['cpu']['memory_percent'],
            data['cpu']['memory_shared'],
        )
      s += sep(200) + '\n'

    if mode in ['all', 'gpu']:
      s += sep(200)
      s += '\n{:^20}{:^20}{:^20}{:^20}{:^20}{:^20}{:^20}{:^20}{:^20}{:^20}'.format(
          'ip', 'port', 'driver_version', 'cuda_version', 'product_name',
          'fan_speed', 'total_memory', 'used_memory', 'memory_percent', 'utilization')
      s += sep(200)
      for res in results:
        m, data = res[0], res[1]
        for gpu in data['gpu']['gpus']:
          s += '\n{:^20}{:^20}{:^20}{:^20}{:^20}{:^20}{:^20}{:^20}{:^20}{:^20}'.format(
              m[0], m[1],
              data['gpu']['driver_version'],
              data['gpu']['cuda_version'],
              gpu['product_name'],
              gpu['fan_speed'],
              gpu['total_memory'],
              gpu['used_memory'],
              '{:.2f} %'.format(float(gpu['used_memory'].split(' ')[0]) *
                                100 / float(gpu['total_memory'].split(' ')[0])),
              gpu['utilization'],
          )
      s += sep(200)

    if mode in ['all', 'event']:
      s += sep(200)
      s += '\n{:^20}{:^20}{:^100}{:^40}{:^20}'.format('ip', 'port', 'expr', 'update', 'epoch')
      s += sep(200)
      for res in results:
        m, data = res[0], res[1]
        for k, v in data['event'].items():
          s += '\n{:^20}{:^20}{:^100}{:^40}{:^20}'.format(
              m[0], m[1],
              k,
              data['event'][k]['modify'],
              data['event'][k]['epoch'],
          )
      s += sep(200)

    print(s)


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--ip', type=str, help='local ipv4 addr.')
  parser.add_argument('--port', type=int, help='bind or listen port.')
  parser.add_argument('--mode', type=str, default='all', choices=['cpu', 'gpu', 'event', 'all'])
  parser.add_argument('--file', type=str, default=None)
  args, _ = parser.parse_known_args()
  print(args)

  daemon = DaemonClient()
  if args.file is None:
    daemon.start(ip=args.ip, port=args.port, mode=args.mode)
  else:
    daemon.start_file(file=args.file, mode=args.mode)
