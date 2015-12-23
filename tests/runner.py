import unittest
import os
import sys

test_dir = os.path.dirname(__file__)
os.chdir(test_dir)
os.chdir("..")

root_path = os.path.abspath('.')

sys.path.insert(0, root_path)
sys.path.insert(0, test_dir)
loader = unittest.TestLoader()
tests = loader.discover(test_dir)

print tests

runner = unittest.TextTestRunner()
runner.verbosity = 2
runner.run(tests)
