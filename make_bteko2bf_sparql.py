#!/usr/bin/env python
"""Create SPARQL to implement bteko to bf conversion."""

import argparse
import csv
import glob
import html
from itertools import zip_longest
import logging
import os.path
from rdflib import Graph, URIRef
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
    m = re.match(r'''(\w+):([^/].*)$''', uri)
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


def contract_uri(uri):
    """Contract unprefixed URI to a namespace prefixed URI if possible."""
    for p, ns in PREFIXES.items():
        if (uri.startswith(str(ns))):
            return(p + ':' + uri[len(str(ns)):])
    return(uri)


class Mapping(object):
    """Class to represent one mapping."""

    def __init__(self, row=None):
        """Initialize from tsv row."""
        self.uri_type = None if row is None else row[0]
        self.bf_uri = None if row is None else row[1]
        self.bteko_uri = None if row is None else row[2]


def read_tsvfile(tsvfile):
    """Read in and check data from TSV file of mappings. Return list of objects."""
    mappings = []
    with open(tsvfile, 'r') as fh:
        tsv = csv.reader(fh, delimiter='\t')
        # Sanity check on headings in case of changes
        headings = next(tsv)
        if (headings[0:3] != ['Type', 'Term', 'ReplacedTerm (if singular)']):
            raise Exception("Oops... table headings not a expected, aborting.")
        for n, row in enumerate(tsv):
            mapping = Mapping(row)
            if (mapping.bteko_uri.endswith(":")):
                logging.warn("[%d] Ignoring bad '%s'" % (n + 2, mapping.bteko_uri))
                mapping.bteko_uri = ''
            mappings.append(Mapping(row))
    return(mappings)


def direct_mappings(mappings):
    """List of SPARQL UPDATE statements to implement direct mappings.

    Direct mappings are indicated in the spreadsheet as and entry in the
    'ReplacedTerm (if singular)' column. This information is combined with
    the 'Type' in the first column that indicates where in triples the
    term might occur: property as predicate, class as object.

    # FIXME - 2017-08-07 - Not all of the mappings currently marked at singular
    # are actually that simple, some also involve structural change and thus where
    # can't do a simple URI substitution!!!
    """
    updates = []
    n = 0
    class_map = {}
    property_map = {}
    for mapping in mappings:
        n += 1
        if (not mapping.bteko_uri):
            continue
        bf_uri = expand_uri(mapping.bf_uri)
        bteko_uri = expand_uri(mapping.bteko_uri)
        if (mapping.uri_type == 'Class'):
            updates.append("DELETE { ?s ?p <%s> } INSERT { ?s ?p <%s> } WHERE  { ?s ?p <%s> };" %
                           (bteko_uri, bf_uri, bteko_uri))
            logging.debug("Class %s -> %s" % (bteko_uri, bf_uri))
        elif (mapping.uri_type in ['ObjectProperty', 'DatatypeProperty',
                                   'SymmetricProperty']):
            updates.append("DELETE { ?s <%s> ?o } INSERT { ?s <%s> ?o } WHERE  { ?s <%s> ?o };" %
                           (bteko_uri, bf_uri, bteko_uri))
            logging.debug("Property %s -> %s" % (bteko_uri, bf_uri))
        else:
            logging.warn("[%d] Bad row with type %s" % (n, uri_type))
    return(updates)


def complex_mappings(mappings):
    """List of SPARQL UPDATE statements to implement complex mappings."""
    updates = []
    # FIXME - stuff in here...
    return(updates)


def read_examples(data_dir='testdata'):
    """Read all examples, indexed by URIs involved."""
    usedin = {}
    examples = []
    for bteko_filename in glob.glob(os.path.join(data_dir, '*_bteko.ttl')):
        bf_filename = re.sub(r'''^(.+)_bteko.ttl$''', r'''\1_bf.ttl''', bteko_filename)
        if (not os.path.exists(bf_filename)):
            logging.warn("No matching bf for %s, ignoring." % (bteko_filename))
        bteko = open(bteko_filename, 'r').read()
        bf = open(bf_filename, 'r').read()
        try:
            for s, p, o in Graph().parse(data=bf, format='n3'):
                for term in (s, p, o):
                    if (isinstance(term, URIRef) and not
                            str(term).startswith('http://example.org/')):
                        print(str(term))
                    usedin[contract_uri(str(term))] = len(examples)
        except Exception as e:
            logging.warn("Failed to parse bf from '%s', ignoring: %s" % (bf_filename, str(e)))
            continue
        examples.append([bteko, bf])
    logging.info("Read %d examples" % (len(examples)))
    return(usedin, examples)


def mkid(term):
    """Make HTML id from term."""
    return(re.sub(r'''[#: ]''', '_', term))  # FIXME - more in here


def linked_term(term):
    """Term linked to local anchor, empty string if None."""
    if (term is None):
        return('')
    else:
        return('<a href="#%s">%s</a>' % (mkid(term), term))


def write_documentation(fh, mappings):
    """Write HTML documentation to fh."""
    usedin, examples = read_examples()
    fh.write("<html>\n<body>\n")
    fh.write("<h1>Bibliotek-o to BIBFRAME conversion documentation</h1>\n\n")
    bf_uris = set()
    bteko_uris = set()
    for mapping in mappings:
        bf_uris.add(contract_uri(mapping.bf_uri))
        bteko_uris.add(contract_uri(mapping.bteko_uri))
    bteko_uris.remove('')
    fh.write("<h2>Index by terms</h2>\n\n")
    fh.write("<table>\n")
    fh.write("<tr><th>BIBFRAME terms</th><th>Bibliotek-o terms</th></tr>\n")
    for bf_uri, bteko_uri in zip_longest(sorted(bf_uris), sorted(bteko_uris)):
        fh.write('<tr><td>' + linked_term(bf_uri) + '</td><td>' + linked_term(bteko_uri) + '</td></tr>\n')
    fh.write("</table>\m\n")
    fh.write("<h2>Mappings by term involved</h2>\n\n")
    for term in sorted(bf_uris):
        fh.write('<h3 id="%s">%s</h3>\n\n' % (mkid(term), term))
        if (term in usedin):
            j = usedin[term]
            fh.write("<table>\n")
            fh.write("<tr><th>BIBFRAME</th><th>Bibliotek-o equivalent</th></td>\n")
            fh.write("<tr>\n<td><pre>%s</pre></td>\n" % (html.escape(examples[j][0])))
            fh.write("<td><pre>%s</pre></td>\n</tr>\n" % (html.escape(examples[j][1])))
            fh.write("</table>\n\n")
    fh.write("</body>\n</html>\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate SPARQL UPDATE for bibliotek-o to BIBRAME conversion.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--tsv', action='store',
                        default='vendor/bibliottek-o_bibframe_usage/bibliotek-o_bibframe_usage_unused_bf_terms.tsv',
                        help='tsv dump of Bibliotek-o BIBFRAME Usage')
    parser.add_argument('--outfile', '-o', action='store',
                        default='bteko2bf.ru',
                        help="output filename")
    parser.add_argument('--docsfile', action='store',
                        default='mappings.html',
                        help="documentation output filename")
    parser.add_argument('--verbose', '-v', action='store_true',
                        help="be verbose")
    parser.add_argument('--debug', '-d', action='store_true',
                        help="be very verbose")
    (opts, args) = parser.parse_known_args()
    if (len(args) > 0):
        parser.error("No command line argument allowed, see -h for help.")
    logging.basicConfig(level=logging.DEBUG if opts.debug else
                        (logging.INFO if opts.verbose else logging.WARN))
    mappings = read_tsvfile(opts.tsv)
    with open(opts.outfile, 'w') as fh:
        n = 0
        for update in direct_mappings(mappings):
            n += 1
            fh.write(update + '\n')
        for update in complex_mappings(mappings):
            n += 1
            fh.write(update + '\n')
    logging.info("Written %d mappings to %s" % (n, opts.outfile))
    with open(opts.docsfile, 'w') as fh:
        write_documentation(fh, mappings)
    logging.info("Written documentation to %s" % (opts.docsfile))
