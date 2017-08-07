#!/usr/bin/env python
"""Test bteko2bf SPARQL UPDATES."""
import argparse
import glob
import os.path
import re
from subprocess import Popen, run, check_output
import sys
import time
import unittest


class TestAll(unittest.TestCase):
    """TestAll class to run tests."""

    port = 3030
    fuseki_uri = 'http://localhost:' + str(port) + '/dataset'
    bteko2bf = 'bteko2bf.ru'
    bf_outfilename = 'test_bf_output.ttl'
    start_fuseki = True
    new_for_each_test = False

    def sparql_update(self, in_filename, ru_filename, out_filename):
        """Run SPARQL update ru_filenqme on in_filename to write out_filename."""
        with open(out_filename, 'wb') as fh:
            run(['update', '--dump',
                 '--data=' + in_filename,
                 '--update=' + ru_filename],
                stdout=fh, check=True)

    def test01_testdata(self):
        """Check all pairs in testdata/ dir."""
        for bteko_filename in glob.glob('testdata/*_bteko.ttl'):
            bf_filename = re.sub(r'''^(.+)_bteko.ttl$''', r'''\1_bf.ttl''', bteko_filename)
            self.assertTrue(os.path.exists(bf_filename))
            self.sparql_update(bteko_filename, self.bteko2bf, self.bf_outfilename)
            self.assertIn(
                b'models are equal',
                check_output(['rdfdiff', bf_filename, self.bf_outfilename, 'N3', 'N3']))


# If run from command line, do tests
if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--bteko2bf', action='store', default='bteko2bf.ru',
                        help="Update script to test")
    parser.add_argument('--VeryVerbose', '-V', action='store_true',
                        help="be verbose.")
    (opts, args) = parser.parse_known_args()
    TestAll.bteko2bf = opts.bteko2bf
    # Remaining args go to unittest
    unittest.main(verbosity=(2 if opts.VeryVerbose else 1),
                  argv=sys.argv[:1] + args)
