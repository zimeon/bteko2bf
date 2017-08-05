# Experiments/thoughts for bibliotek-o to BIBFRAME conversion

## Idea...

Bibliotek-o to BIBFRAME is an RDF to RDF conversion where a significant portion of the data will remain the same (things in the `bf:` namespace). It thus seems that SPARQL [`UPDATE`](https://www.w3.org/TR/sparql11-update/#deleteInsert) to delete bibliotek-o triples and replace them with BIBFRAME?

## Building the conversion

The Python `make-bteko2bf-sparql.py` program is designed to write a SPARQL UPDATE script `bteko2bf.ru`. Generate with:

```
> python make-bteko2bf-sparql.py -v
INFO:root:Done, written 90 mappings to bteko2bf.ru
```

## Running the conversion

**NEED TO FIND A PURE COMMAND LINE WAY TO DO THIS** -- currently it seems to work OK with a [Fuseki triplestore server](README_fuseki.md) but this seems rather inconvenient and wasteful in terms of startup time.

## Setup

The `vendor` directory include a JAR of [`bib2lod`](https://github.com/ld4l-labs/bib2lod) which does MARCXML to bibliotek-o conversion.

The `vendor` directory includes LC `marc2bibframe` XSL which does MARCXML to BIBFRAME RDF/XML conversion. These XSLs can be used with `xsltproc` which for me reports:

```
> xsltproc --version
Using libxml 20900, libxslt 10128 and libexslt 817
xsltproc was compiled against libxml 20900, libxslt 10128 and libexslt 817
libxslt 10128 was compiled against libxml 20900
libexslt 817 was compiled against libxml 20900
```

For RDF format conversion I use `rapper` (so I never have to see any RDF/XML!):

```
> rapper --version
2.0.15
```

### Converting MARC -> BIBFRAME

```
xsltproc vendor/marc2bibframe2-xsl/marc2bibframe2.xsl vendor/bib2lod/102063.min.xml | rapper -o turtle - http://example.org/ > tmp/102063-bf.ttl
rapper: Parsing file <stdin> with parser rdfxml and base URI http://example.org/
rapper: Serializing with serializer turtle and base URI http://example.org/
rapper: Parsing returned 48 triples
```

which gives:

```
> more tmp/102063-bf.ttl 
@base <http://example.org/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix bf: <http://id.loc.gov/ontologies/bibframe/> .
@prefix bflc: <http://id.loc.gov/ontologies/bflc/> .
@prefix madsrdf: <http://www.loc.gov/mads/rdf/v1#> .

<102063#Instance>
    bf:illustrativeContent <http://id.loc.gov/vocabulary/millus/ill> ;
    bf:instanceOf <102063#Work> ;
    bf:issuance <http://id.loc.gov/vocabulary/issuance/mono> ;
    bf:provisionActivity [
        bf:date "1957"^^<http://id.loc.gov/datatypes/edtf> ;
        bf:place <http://id.loc.gov/vocabulary/countries/nyu> ;
        a bf:ProvisionActivity, bf:Publication
    ] ;
    bf:title [
        bflc:titleSortKey "Clinical cardiopulmonary physiology." ;
        bf:mainTitle "Clinical cardiopulmonary physiology" ;
        a bf:Title ;
        rdfs:label "Clinical cardiopulmonary physiology."
    ] ;
    a bf:Instance ;
    rdfs:label "Clinical cardiopulmonary physiology." .

<102063#Work>
    bf:adminMetadata [
        bflc:encodingLevel [
            bf:code "1" ;
            a bflc:EncodingLevel
        ] ;
        bf:creationDate "1986-05-06"^^<http://www.w3.org/2001/XMLSchema#date> ;
        bf:descriptionConventions [
            bf:code "unknown" ;
            a bf:DescriptionConventions
        ] ;
        bf:identifiedBy [
            a bf:Local ;
            rdf:value "102063"
        ] ;
        bf:status [
            bf:code "c" ;
            a bf:Status
        ] ;
        a bf:AdminMetadata
    ] ;
```

We note there are a couple of additions here in the `bflc` namespace that are  

### Converting MARC -> bibliotek-o

```
> java -jar vendor/bib2lod/bib2lod.jar -c vendor/bib2lod/config.json; rapper -i turtle -o turtle -f xmlns:rdfs=\"http://www.w3.org/2000/01/rdf-schema#\" -f xmlns:bf=\"http://id.loc.gov/ontologies/bibframe/\" -f xmlns:bib=\"http://bibliotek-o.org/ontology/\" -f xmlns:dct=\"http://purl.org/dc/terms/\" -f xmlns:vivo=\"http://vivoweb.org/ontology/core#\" tmp/102063.min.ttl http://example.org/ > tmp/102063-bteko.ttl
15:14:06.093 INFO  org.ld4l.bib2lod.managers.SimpleManager line 39 - START CONVERSION.
15:14:06.793 INFO  org.ld4l.bib2lod.managers.SimpleManager line 44 - END CONVERSION.
rapper: Parsing URI file:///Users/simeon/src/bteko2bf/tmp/102063.min.ttl with parser turtle and base URI http://example.org/
rapper: Serializing with serializer turtle and base URI http://example.org/
rapper: Parsing returned 31 triples
```

Which produces:

```
> more tmp/102063-bteko.ttl
@base <http://example.org/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix bf: <http://id.loc.gov/ontologies/bibframe/> .
@prefix bib: <http://bibliotek-o.org/ontology/> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix vivo: <http://vivoweb.org/ontology/core#> .

<n49bd4013c951e3fe>
    dct:hasPart <n940b179f7c128f51> ;
    a bf:Title ;
    rdf:value "Clinical cardiopulmonary physiology." .

<n4ddfc97a89c72d82>
    bib:hasPreferredTitle <na6d6b62a64809d48> ;
    dct:language <http://id.loc.gov/vocabulary/languages/eng> ;
    a bf:Text, bf:Work .

<n7b454d8a8ce9e261>
    a bf:Local ;
    rdf:value "102063" .

<n84cafe41bcd09ce6>
    vivo:rank "1"^^<http://www.w3.org/2001/XMLSchema#int> ;
    a bib:MainTitleElement ;
    rdf:value "Clinical cardiopulmonary physiology." .

<n851e67e62c11def2>
    a bf:Item .

<n940b179f7c128f51>
    vivo:rank "1"^^<http://www.w3.org/2001/XMLSchema#int> ;
    a bib:MainTitleElement ;
    rdf:value "Clinical cardiopulmonary physiology." .

<na6d6b62a64809d48>
    dct:hasPart <n84cafe41bcd09ce6> ;
    a bf:Title ;
    rdf:value "Clinical cardiopulmonary physiology." .

<ndc2c85f4ef4ecb09>
    bib:atLocation <http://id.loc.gov/vocabulary/countries/nyu> ;
    dct:date "1957" ;
    a bib:PublisherActivity ;
    rdfs:label "Publishing" .

<ne04f254e09dd485f>
    bf:identifiedBy <n7b454d8a8ce9e261> ;
    a bf:AdminMetadata .

<nf543a03c69fb4af6>
    bib:hasActivity <ndc2c85f4ef4ecb09> ;
    bib:hasPreferredTitle <n49bd4013c951e3fe> ;
    bf:adminMetadata <ne04f254e09dd485f> ;
    bf:hasItem <n851e67e62c11def2> ;
    bf:instanceOf <n4ddfc97a89c72d82> ;
    a bf:Instance .

```

