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
import time
import argparse
import socket
import json
import subprocess
import xml.etree.ElementTree as ET
import psutil
import os

from .tfevent import TFEventAccumulator
from .logger import logger


GB = 1024 * 1024 * 1024  # Byte to GB


class DaemonServer():

  def __init__(self):
    logger.init('rs.server.log', './')

  def send(self, conn, data):
    conn.send(json.dumps(data).encode())

  def _gpu(self):
    results = {'gpu': {}}
    try:
      res = subprocess.check_output('nvidia-smi -q -x', shell=True)
      if res is not None:
        res = ET.fromstring(res)
        results['gpu']['driver_version'] = res.find('driver_version').text
        results['gpu']['cuda_version'] = res.find('cuda_version').text
        results['gpu']['gpus'] = []
        for g in res.findall('gpu'):
          results['gpu']['gpus'].append({
              'product_name': g.find('product_name').text,
              'fan_speed': g.find('fan_speed').text,
              'total_memory': g.find('fb_memory_usage').find('total').text,
              'used_memory': g.find('fb_memory_usage').find('used').text,
              'utilization': g.find('utilization').find('gpu_util').text,
          })
    except Exception as e:
      logger.warn(str(e))
    return results

  def _cpu(self):
    results = {'cpu': {}}
    try:
      results['cpu']['cpu_count'] = psutil.cpu_count()
      results['cpu']['cpu_current_freq'] = psutil.cpu_freq().current
      results['cpu']['cpu_percent'] = psutil.cpu_percent()
      mem = psutil.virtual_memory()
      results['cpu']['memory_total'] = '{:.4f}'.format(mem.total / GB)
      results['cpu']['memory_used'] = '{:.4f}'.format(mem.used / GB)
      results['cpu']['memory_free'] = '{:.4f}'.format(mem.free / GB)
      results['cpu']['memory_percent'] = '{:.4f}'.format(mem.percent / GB)
      results['cpu']['memory_shared'] = '{:.4f}'.format(mem.shared / GB)
    except Exception as e:
      logger.warn(str(e))
    return results

  def _event(self, event_dir):
    results = {'event': {}}
    if event_dir is None:
      return results
    try:
      for fold in os.listdir(event_dir):
        fold_path = os.path.join(event_dir, fold)
        if not os.path.isdir(fold_path):
          continue
        event = TFEventAccumulator(fold_path)
        if event.epoch <= 0:
          continue
        # event.load_scalars()
        # event.kv['scalars'] is too large
        results['event'][fold] = {
            'modify':  time.ctime(os.path.getmtime(fold_path)),
            'epoch': event.epoch
        }
    except Exception as e:
      logger.warn(str(e))
    return results

  def start(self, ip, port, event_dir=None):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip, port))
    s.listen(5)
    logger.info(f'start daemon at ip:{ip}:{port}')
    while True:
      conn, addr = s.accept()
      logger.info(f'connection from {addr}.')

      results = {}
      results.update(self._cpu())
      results.update(self._gpu())
      results.update(self._event(event_dir))

      conn.send(json.dumps(results).encode())
      conn.close()
      logger.info(f'successfully send message to {addr}.')


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--ip', type=str, help='bind a local ipv4 addr.')
  parser.add_argument('--port', type=int, help='bind a port to listen.')
  parser.add_argument('--event-dir', type=str, default=None, help='monitor tensorboard events.')
  args, _ = parser.parse_known_args()
  print(args)

  daemon = DaemonServer()
  daemon.start(ip=args.ip, port=args.port, event_dir=args.event_dir)
