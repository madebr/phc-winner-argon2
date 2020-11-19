#!/usr/bin/python

import argparse
import os
import subprocess

ARGON2_HOME = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
VERBOSE = False

def verbose_run(*args, **kwargs):
  if VERBOSE:
    print("Running: {}".format(args[0]))
  return subprocess.run(*args, **kwargs)


def test_version_type(genkat, version, type):
  print("Testing argon2{} v={}".format(type, version))
  if str(version) == "19":
    ref = "argon2{}".format(type)
  else:
    ref = "argon2{}_v{}".format(type, version)
  completed = verbose_run([genkat, str(type), str(version)], capture_output=True, text=True, check=True)
  kats_ref = open(os.path.join(ARGON2_HOME, "kats", ref), "r").read()
  if completed.stdout != kats_ref:
    raise Exception


def main(args=None):
  parser = argparse.ArgumentParser()
  parser.add_argument("genkat")
  parser.add_argument("--verbose", action="store_true")
  ns = parser.parse_args(args)
  global VERBOSE
  VERBOSE = ns.verbose

  for version in ("16", "19"):
    for type in ("i", "d", "id"):
      test_version_type(ns.genkat, version, type)

if __name__ == "__main__":
  main()
