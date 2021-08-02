# Copyright 2017 The KaiJIN Authors. All Rights Reserved.
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
from setuptools import setup
from setuptools import find_packages


with open('README.md') as f:
  long_description = f.read()


setup(
    name="rs",
    version="0.0.3",
    author="Kai Jin",
    author_email="atranitell@gmail.com",
    description="A Simple Remote Server and Training Manager.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/atranitell/TQ",
    license="Apache 2.0 Licence",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    install_requires=[
        "tensorboard",
        "psutil"
    ],
)
