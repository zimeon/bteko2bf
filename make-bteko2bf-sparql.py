#!/usr/bin/env python
"""Create SPARQL to implement bteko to bf conversion."""

import argparse
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


def direct_mappings(tsvfile):
    """List of SPARQL UPDATE statements to implement direct mappings.

    Direct mappings are indicated in the spreadsheet as and entry in the
    'ReplacedTerm (if singular)' column. This information is combined with
    the 'Type' in the first column that indicates where in triples the
    term might occur: property as predicate, class as object.
    """
    updates = []
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
                updates.append("DELETE { ?s ?p <%s> } INSERT { ?s ?p <%s> } WHERE  { ?s ?p <%s> };" %
                               (bteko_uri, bf_uri, bteko_uri))
                logging.debug("Class %s -> %s" % (bteko_uri, bf_uri))
            elif (uri_type in ['ObjectProperty', 'DatatypeProperty',
                               'SymmetricProperty']):
                updates.append("DELETE { ?s <%s> ?o } INSERT { ?s <%s> ?o } WHERE  { ?s <%s> ?o };" %
                               (bteko_uri, bf_uri, bteko_uri))
                logging.debug("Property %s -> %s" % (bteko_uri, bf_uri))
            else:
                logging.warn("[%d] Bad row with type %s" % (n, uri_type))
    return(updates)


def complex_mappings():
    """List of SPARQL UPDATE statements to implement complex mappings."""
    updates = []
    # FIXME - stuff in here...
    return(updates)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate SPARQL UPDATE for bibliotek-o to BIBRAME conversion.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--tsv', action='store',
                        default='vendor/bibliottek-o_bibframe_usage/bibliotek-o_bibframe_usage_unused_bf_terms.tsv',
                        help='tsv dump of Bibliotek-o BIBFRAME Usage')
    parser.add_argument('--outfile', '-o', action='store',
                        default='bteko2bf.ru',
                        help="output filename")
    parser.add_argument('--verbose', '-v', action='store_true',
                        help="be verbose")
    parser.add_argument('--debug', '-d', action='store_true',
                        help="be very verbose")
    (opts, args) = parser.parse_known_args()
    if (len(args) > 0):
        parser.error("No command line argument allowed, see -h for help.")
    logging.basicConfig(level=logging.DEBUG if opts.debug else
                        (logging.INFO if opts.verbose else logging.WARN))
    with open(opts.outfile, 'w') as fh:
        n = 0
        for update in direct_mappings(opts.tsv):
            n += 1
            fh.write(update + '\n')
        for update in complex_mappings():
            n += 1
            fh.write(update + '\n')
    logging.info("Done, written %d mappings to %s" % (n, opts.outfile))
