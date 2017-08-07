# Experiments/thoughts for bibliotek-o to BIBFRAME conversion

## Idea...

Bibliotek-o to BIBFRAME is a lossy RDF to RDF conversion where a significant portion of the data will remain the same (things in the `bf:` namespace). It thus seems that [SPARQL UPDATE](https://www.w3.org/TR/sparql11-update/#deleteInsert) to delete bibliotek-o triples and replace them with BIBFRAME equivalent would be a good approach?

The conversion is lossy because bibliotek-o is more expressive than BIBFRAME.

## Building the conversion

The Python `make-bteko2bf-sparql.py` program is designed to write a SPARQL UPDATE script `bteko2bf.ru` based on data from bibliotek-o to BIBFRAME mappings. Generate with:

```
> python make-bteko2bf-sparql.py -v
INFO:root:Done, written 90 mappings to bteko2bf.ru
```

## Running the conversion

Assuming the SPARQL UPDATE code is `bteko2bf.ru`, one can run it on a bibliotek-o file `testdata/ex_listingCredits_1_bteko.ttl` with:

```
> update --dump --data=testdata/ex_listingCredits_1_bteko.ttl --update=bteko2bf.ru
<http://example.org/obj1> <http://id.loc.gov/ontologies/bibframe/credits> "Credit" .
```

the output BIBFRAME is written to STDOUT (just one triple in this example).

See for notes on running [SPARQL UPDATE as a command-line tool](README_update.md). There are also notes about running against a [Fuseki triplestore server](README_fuseki.md).

## Tests

The program `test-bteko2bf-sparql.py` uses the Python `unittest` framework to run tests against all examples `*_bteko.ttl` -> `*_bf.ttl` in the [`testdata`](testdata) directory. Run with:

```
> python test-bteko2bf-sparql.py 
.
----------------------------------------------------------------------
Ran 1 test in 3.018s

OK
```

## Setup

### Python

The code is designed to run with Python3.5 or higher.

### Apache Jena

The tests rely on [Apache Jena](https://jena.apache.org/download/index.cgi) tools, on OSX these can be installed with homebrew:

```
> brew install jena
```

I'm not sure how sensitive any of this is to version on Jena. Developement has been done against 3.1.0:

```
> update --version
Jena:       VERSION: 3.1.0
Jena:       BUILD_DATE: 2016-05-10T11:59:39+0000
ARQ:        VERSION: 3.1.0
ARQ:        BUILD_DATE: 2016-05-10T11:59:39+0000
RIOT:       VERSION: 3.1.0
RIOT:       BUILD_DATE: 2016-05-10T11:59:39+0000
```

and the travis tests run aginst 3.4.0 (as of 2017-08-07).

### Bibliotek-o to BIBFRAME mappings

**WARNING - Mappings currently work in progress, the versions here are an incomplete dump***

The directory [vendor/bibliottek-o_bibframe_usage](vendor/bibliottek-o_bibframe_usage) has TSV dumps of the current mapping spreadsheets from the [LD4P bibliottek-o work](https://wiki.duraspace.org/display/LD4P/bibliotek-o). This will be updated when real/final mappings are published.

