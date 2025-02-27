# Copyright 2019 ZTE corporation. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os
import shutil
import subprocess
from os import path
from tempfile import TemporaryDirectory
from urllib import request

import setuptools
from setuptools.command.build_py import build_py


_TYPES_PROTO_URL = 'https://github.com/tensorflow/tensorflow/raw/v2.4.0/tensorflow/core/framework/types.proto'
_PROJECT_PATH = path.dirname(path.abspath(__file__))


def _generate_protos():
    with TemporaryDirectory() as external_dir:
        types_proto_dir = path.join(external_dir, 'tensorflow', 'core', 'framework')
        types_proto_file = path.join(types_proto_dir, 'types.proto')
        protos_dir = path.join(_PROJECT_PATH, 'src', 'model_compiler', 'protos')
        protos_src_dir = path.join(protos_dir, 'src')
        protos_generated_dir = path.join(protos_dir, 'generated')

        os.makedirs(types_proto_dir, exist_ok=True)
        os.makedirs(protos_generated_dir, exist_ok=True)

        with request.urlopen(_TYPES_PROTO_URL) as response, open(types_proto_file, 'wb') as proto_file:
            shutil.copyfileobj(response, proto_file)

        subprocess.run(args=['protoc',
                             '-I', protos_src_dir,
                             '-I', external_dir,
                             '--python_out', protos_generated_dir,
                             path.join(protos_src_dir, 'model_config.proto')],
                       check=True)


class _BuildPy(build_py):
    def run(self):
        _generate_protos()

        super().run()


setuptools.setup(
    name='model_compiler',
    packages=setuptools.find_namespace_packages('src'),
    cmdclass={'build_py': _BuildPy},
    package_dir={'': 'src'},
    package_data={'model_compiler': ['protos/src/*.proto']},
    install_requires=[
        'defusedxml',
        'future',
        'networkx',
        'tensorflow==2.4.0',
        'torch',
        'onnx-tf',
        'onnx-caffe2',
        'paddlepaddle',
        'paddle2onnx',
        'tensorflow_addons',
        'test-generator==0.1.1',
        'tf2onnx',
        'mxnet'
    ],
    entry_points={'console_scripts': ['model-compiler=model_compiler.main:main']},
    extras_require={
        'test': [
            'bandit',
            'flake8',
            'mypy',
            'pylint==2.6.2',
            'pytest-cov',
            'pytest-xdist'
        ]
    },
    python_requires='>= 3.6'
)
