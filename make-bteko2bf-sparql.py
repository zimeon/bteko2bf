#!/usr/bin/env python
"""Create SPARQL to implement bteko to bf conversion."""

import csv
import logging
from rdflib.namespace import Namespace, DCTERMS, FOAF, RDF, RDFS
import re
import sys


BF = Namespace('http://id.loc.gov/ontologies/bibframe/')
BIB = Namespace('http://bibliotek-o.org/ontology/')
MADSRDF = Namespace('http://www.loc.gov/mads/rdf/v1#')
LINGVOJ = Namespace('http://www.lingvoj.org/ontology#')
OA = Namespace('http://www.w3.org/ns/oa#')
PROV = Namespace('http://www.w3.org/ns/prov#')
RDAU = Namespace('http://rdaregistry.info/Elements/u/')
SCHEMA = Namespace('http://schema.org/')
VIVO = Namespace('http://vivoweb.org/ontology/core#')
PREFIXES = {  # prefix to namespace mappings
    'bf': BF,
    'bib': BIB,
    'dcterms': DCTERMS,
    'foaf': FOAF,
    'lingvoj': LINGVOJ,
    'madsrdf': MADSRDF,
    'oa': OA,
    'prov': PROV,
    'rdau': RDAU,
    'rdf': RDF,
    'rdfs': RDFS,
    'schema': SCHEMA,
    'vivo': VIVO
}
ALTPREFIXES = {  # alternate to preferred prefix mappings
    'dct': 'dcterms'
}


def expand_uri(uri):
    """Expand prefixed URI to full URI."""
    m = re.match(r'''(\w+):([^/].+)$''', uri)
    if (m):
        prefix = m.group(1)
        local = m.group(2)
        if (prefix in PREFIXES):
            uri = str(PREFIXES[prefix]) + local
        elif (prefix in ALTPREFIXES):
            uri = str(PREFIXES[ALTPREFIXES[prefix]]) + local
        else:
            logging.warn("Unknown prefix '%s', can't expand '%s'" % (prefix, uri))
    return(uri)


def direct_mappings():
    """Work out direct mappings that just change property URI."""
    tsvfile = 'vendor/bibliottek-o_bibframe_usage/bibliotek-o_bibframe_usage_unused_bf_terms.tsv' 
    with open(tsvfile, 'r') as fh:
        tsv = csv.reader(fh, delimiter='\t')
        # Sanity check on headings in case of changes
        headings = next(tsv)
        if (headings[0:3] != ['Type', 'Term', 'ReplacedTerm (if singular)']):
            raise Exception("Oops... table headings not a expected, aborting.")
        n = 0
        class_map = {}
        property_map = {}
        for row in tsv:
            n += 1
            (uri_type, bf_uri, bteko_uri) = row[0:3]
            if (not bteko_uri):
                continue
            bf_uri = expand_uri(bf_uri)
            bteko_uri = expand_uri(bteko_uri)
            if (uri_type == 'Class'):
                print("Class %s %s" % (bf_uri, bteko_uri))
            elif (uri_type in ['ObjectProperty', 'DatatypeProperty',
                               'SymmetricProperty']):
                print("Property %s %s" % (bf_uri, bteko_uri))
            else:
                logging.warn("[%d] Bad row with type %s" % (n, uri_type))


direct_mappings()


