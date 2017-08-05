#!/usr/bin/env python
"""Test bteko2bf SPARQL UPDATES."""
import argparse
import glob
import os.path
import re
from subprocess import Popen, check_output
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

    @classmethod
    def _start_fuseki(cls):
        """Start fuseki."""
        cls.proc = Popen(['fuseki-server', '--update', '--mem',
                          '--localhost', '/dataset'])
        print("Started fuseki (pid=%d)" % (cls.proc.pid))
        time.sleep(10)

    @classmethod
    def _stop_fuseki(cls):
        """Kill fuseki."""
        cls.proc.kill()
        outs, errs = cls.proc.communicate()
        print("Killed fuseki (%s, %s)" % (outs, errs))

    @classmethod
    def setUpClass(cls):
        """Setup for class."""
        if (cls.start_fuseki and not cls.new_for_each_test):
            cls._start_fuseki()

    @classmethod
    def tearDownClass(cls):
        """Teardown for class."""
        if (cls.start_fuseki and not cls.new_for_each_test):
            cls._stop_fuseki()

    def setUp(self):
        """Setup for each test."""
        if (self.start_fuseki and self.new_for_each_test):
            self._start_fuseki()

    def tearDown(self):
        """Teardown for each test."""
        if (self.start_fuseki and self.new_for_each_test):
            self._stop_fuseki()

    def test01_testdata(self):
        """Check all pairs in testdata/ dir."""
        for bteko_filename in glob.glob('testdata/*_bteko.ttl'):
            bf_filename = re.sub(r'''^(.+)_bteko.ttl$''', r'''\1_bf.ttl''', bteko_filename)
            self.assertTrue(os.path.exists(bf_filename))
            self.assertEqual(
                check_output(['s-update', '--service=' + self.fuseki_uri,
                              '--update=example-ru/clear.ru']),
                b'')
            self.assertEqual(
                check_output(['s-put', self.fuseki_uri, 'default', bteko_filename]),
                b'')
            self.assertEqual(
                check_output(['s-update', '--service=' + self.fuseki_uri,
                              '--update=' + self.bteko2bf]),
                b'')
            bf_out = check_output(['s-get', self.fuseki_uri, 'default'])
            with open(self.bf_outfilename, 'wb') as fh:
                fh.write(bf_out)
            self.assertIn(
                b'models are equal',
                check_output(['rdfdiff', bf_filename, self.bf_outfilename, 'N3', 'N3']))


# If run from command line, do tests
if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--bteko2bf', action='store', default='bteko2bf.ru',
                        help="Update script to test")
    parser.add_argument('--fuseki-uri', action='store', default='',
                        help="Use Fuseki at given URIrather than running fuseki")
    parser.add_argument('--fresh', action='store_true',
                        help="Start fuseki fresh for each test (slow)")
    parser.add_argument('--VeryVerbose', '-V', action='store_true',
                        help="be verbose.")
    (opts, args) = parser.parse_known_args()
    TestAll.bteko2bf = opts.bteko2bf
    if (opts.fuseki_uri):
        TestAll.start_fuseki = False
        TestAll.fuseki_uri = opts.fuseki_uri
    else:
        TestAll.new_for_each_test = opts.fresh
    # Remaining args go to unittest
    unittest.main(verbosity=(2 if opts.VeryVerbose else 1),
                  argv=sys.argv[:1] + args)
