#!/usr/bin/python

import argparse
import os
import subprocess
import tempfile

ARGON2_HOME = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
VERBOSE = False

def verbose_run(*args, **kwargs):
  if VERBOSE:
    print("Running: {}".format(args[0]))
  return subprocess.run(*args, **kwargs)


def build_argon2(simd_opts):
  if simd_opts:
    print("Building argon2 with simd optimizations")
  else:
    print("Building argon2 without simd optimizations")
  run_extra_args = {}
  if VERBOSE:
    run_extra_args["stdout"] = subprocess.DEVNULL
    run_extra_args["stdout"] = subprocess.DEVNULL
    run_extra_args["capture_output"] = True
  verbose_run(["cmake", ARGON2_HOME, "-DARGON2_TESTS=ON", "-DARGON2_OPTIMIZED={}".format(bool(simd_opts)), "-DCMAKE_RUNTIME_OUTPUT_DIRECTORY=bin"], check=True, **run_extra_args)

  make_extra_args = []
  if VERBOSE:
    make_extra_args.append("--verbose")
  verbose_run(["cmake", "--build", ".", "--target", "genkat"] + make_extra_args, check=True, **run_extra_args)


def test_version_type(version, type):
  print("Testing argon2{} v={}".format(type, version))
  if str(version) == "19":
    ref = "argon2{}".format(type)
  else:
    ref = "argon2{}_v{}".format(type, version)
  completed = verbose_run(["bin/genkat", str(type), str(version)], capture_output=True, text=True, check=True)
  kats_ref = open(os.path.join(ARGON2_HOME, "kats", ref), "r").read()
  if completed.stdout != kats_ref:
    raise Exception


def main(args=None):
  parser = argparse.ArgumentParser()
  parser.add_argument("--verbose", action="store_true")
  ns = parser.parse_args(args)
  global VERBOSE
  VERBOSE = ns.verbose

  with tempfile.TemporaryDirectory() as tempdir:
    print("Building in {}".format(tempdir))
    os.chdir(tempdir)
    for simd_optimizations in (True, False):
      build_argon2(simd_optimizations)
      for version in ("16", "19"):
        for type in ("i", "d", "id"):
          test_version_type(version, type)

if __name__ == "__main__":
  main()
