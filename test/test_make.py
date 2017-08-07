"""Test make_bteko2bf_sparql.py."""
import unittest
from make_bteko2bf_sparql import expand_uri, contract_uri

class TestAll(unittest.TestCase):
    """TestAll class to run tests."""

    def test01_expand_uri(self):
        """Test expand_uri()."""
        self.assertEqual(expand_uri(''), '')
        self.assertEqual(expand_uri('zzz'), 'zzz')
        self.assertEqual(expand_uri('http://example.org/abc'), 'http://example.org/abc')
        self.assertEqual(expand_uri('bib:a'), 'http://bibliotek-o.org/ontology/a')
        self.assertEqual(expand_uri('dct:hasPart'), 'http://purl.org/dc/terms/hasPart')
        self.assertEqual(expand_uri('dcterms:hasPart'), 'http://purl.org/dc/terms/hasPart')

    def test01_contract_uri(self):
        """Test contract_uri()."""
        self.assertEqual(contract_uri(''), '')
        self.assertEqual(contract_uri('xyz'), 'xyz')
        self.assertEqual(contract_uri('http://purl.org/dc/terms/hasPart'), 'dcterms:hasPart')