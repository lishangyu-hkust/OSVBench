import json
import os
import subprocess
import argparse
import signal

parser = argparse.ArgumentParser()
parser.add_argument('--input', type=str, default='', help='input specification and output name.')
args = parser.parse_args()

def timeout_handler(signum, frame):
    raise TimeoutError

class Task(object):
    command = "make hv6-verify -- -v --failfast HV6.test_"
    output = ""
    input = args.input

    specs_content = """
#
# Copyright 2017 Hyperkernel Authors
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

import z3
from libirpy import util
import hv6py.kernel.spec.datatypes as dt
import types

from hv6py.base import Accessor, BaseStruct, Struct, Map, Refcnt, Refcnt2

from helpers import (
        is_dmapn_valid,
        is_fd_valid,
        is_fn_valid,
        is_intremap_valid,
        is_pcipn_valid,
        is_pid_valid,
        is_pn_valid,
)

"""

    def load_dataset(self):
        with open("./" + self.input + ".json") as f:
            self.specs_to_append = json.load(f)

    def containOK(self, out1, err1):
        flag = False
        if "... ok" in out1:
            flag = True
        if "... ok" in err1:
            flag = True
        return flag

    def print_dataset(self):
        print type(self.specs_to_append)
        print self.specs_content

    def write_specs(self):
        # Handle the timeout cases.
        signal.signal(signal.SIGALRM, timeout_handler)

        for i in range(len(self.specs_to_append)):
            for key, value in self.specs_to_append[str(i)].items():
                counter = 0
                size = len(value)
                for spec in value:

                    with open("./o.x86_64/hv6/hv6py/kernel/spec/spec/specs.py", "w") as f:
                        f.write(self.specs_content + spec + "\n")

                    process = ""
                    try:
                        # Timeout limit: 600s.
                        signal.alarm(600)
                        process = subprocess.Popen(self.command + key, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # Linux/Mac
                    except TimeoutError as e:
                        if size == counter + 1:
                            with open("./outputs/" + "output_" + self.input, "a") as f:
                                f.write("\nSyscall " + key + ":\n" + "Error: Timeout.\n")
                        counter += 1
                        continue
                    except Exception as e:
                        pass

                    self.output, stderr = process.communicate()

                    if size == counter + 1:
                        with open("./outputs/" + "output_" + self.input, "a") as f:
                            f.write("\nSyscall " + key + ":\n" + self.output + "\n" + stderr)
                    else:
                        if self.containOK(self.output, stderr):
                            with open("./outputs/" + "output_" + self.input, "a") as f:
                                f.write("\nSyscall " + key + ":\n" + self.output + "\n" + stderr)
                            break
                    counter += 1

if __name__ == '__main__':
    task = Task()
    task.load_dataset()
    task.write_specs()

