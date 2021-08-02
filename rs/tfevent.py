# Copyright 2020 The KaiJIN Authors. All Rights Reserved.
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
import os  # nopep8
import warnings  # nopep8
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # nopep8
warnings.simplefilter("ignore", UserWarning)  # nopep8
warnings.simplefilter("ignore", FutureWarning)  # nopep8
import re
import glob
import pickle
import xml.etree.ElementTree as ET
from tensorboard.backend.event_processing import event_accumulator


class TFEventAccumulator():
  def __init__(self, root):
    # root
    if not os.path.exists(root):
      raise FileExistsError(root)
    self._root = root

    # store all info
    self._kv = {
        'images': [],
        'audio': [],
        'histograms': [],
        'scalars': {},
        'distributions': [],
        'tensors': [],
        'graph': False,
        'meta_graph': False,
        'run_metadata': []
    }

  def dump(self):
    with open('%s.pkl' % self._root, 'wb') as fw:
      pickle.dump(self._kv, fw)

  def load_scalars(self):
    # parse all info at root dir
    files = glob.glob('%s/*/events.out.tfevents.*' % self._root)
    for path in files:
      tag = path.split('/')[-2]
      ea = event_accumulator.EventAccumulator(path)
      ea.Reload()
      for key in ea.Tags()['scalars']:
        vals = [(int(scalar.step), scalar.value) for scalar in ea.Scalars(key)]
        self._kv['scalars'][tag + '/' + key] = [v for v in zip(*vals)]

  @property
  def epoch(self):
    models = glob.glob('%s/model.epoch-*' % self._root)
    epochs = [int(re.findall('model.epoch-(.*?).step', model)[0]) for model in models]
    return max(epochs) if len(epochs) else 0

  @property
  def kv(self):
    return self._kv

  @property
  def root(self):
    return self._root
