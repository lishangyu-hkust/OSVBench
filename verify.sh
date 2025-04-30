#!/bin/bash

make hv6-verify -- -v --failfast HV6.test_sys_set_runnable
python spec_util.py --input=$1


