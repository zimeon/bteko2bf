# Experiments/thoughts for bibliotek-o to BIBFRAME conversion

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
> java -jar vendor/bib2lod/bib2lod.jar -c vendor/bib2lod/config.json; rapper -i ntriples -o turtle -f xmlns:rdfs=\"http://www.w3.org/2000/01/rdf-schema#\" -f xmlns:bf=\"http://id.loc.gov/ontologies/bibframe/\" -f xmlns:bib=\"http://bibliotek-o.org/ontology/\" -f xmlns:dct=\"http://purl.org/dc/terms/\" -f xmlns:vivo=\"http://vivoweb.org/ontology/core#\" tmp/102063.min.nt http://data.ld4l.org/cornell/ > tmp/102063-bteko.ttl
 
11:59:34.640 INFO  org.ld4l.bib2lod.managers.SimpleManager line 39 - START CONVERSION.
11:59:38.434 INFO  org.ld4l.bib2lod.managers.SimpleManager line 44 - END CONVERSION.
rapper: Parsing URI file:///Users/simeon/src/bteko2bf/tmp/102063.min.nt with parser ntriples
rapper: Serializing with serializer turtle
rapper: Parsing returned 31 triples
```

Which produces:

```
> more tmp/102063-bteko.ttl 
@base <http://data.ld4l.org/cornell/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix bf: <http://id.loc.gov/ontologies/bibframe/> .
@prefix bib: <http://bibliotek-o.org/ontology/> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix vivo: <http://vivoweb.org/ontology/core#> .

<n1a2af2499c92d41c>
    vivo:rank "1"^^<http://www.w3.org/2001/XMLSchema#int> ;
    a bib:MainTitleElement ;
    rdf:value "Clinical cardiopulmonary physiology." .

<n386b4c790e19f0e8>
    dct:hasPart <n1a2af2499c92d41c> ;
    a bf:Title ;
    rdf:value "Clinical cardiopulmonary physiology." .

<n445f05d5e9165831>
    bf:identifiedBy <n73205fbd2e8a1764> ;
    a bf:AdminMetadata .

<n73205fbd2e8a1764>
    a bf:Local ;
    rdf:value "102063" .

<n73437ac2c628886b>
    a bf:Item .

<n789f010491428529>
    bib:hasActivity <n865aa7ec7d9a9f58> ;
    bib:hasPreferredTitle <nd95e57b81fac7218> ;
    bf:adminMetadata <n445f05d5e9165831> ;
    bf:hasItem <n73437ac2c628886b> ;
    bf:instanceOf <na6fd58b8eb1c1551> ;
    a bf:Instance .

<n865aa7ec7d9a9f58>
    bib:atLocation <http://id.loc.gov/vocabulary/countries/nyu> ;
    dct:date "1957" ;
    a bib:PublisherActivity ;
    rdfs:label "Publishing" .

<na6fd58b8eb1c1551>
    bib:hasPreferredTitle <n386b4c790e19f0e8> ;
    dct:language <http://id.loc.gov/vocabulary/languages/eng> ;
    a bf:Text, bf:Work .

<nb952b1aee2ec439>
    vivo:rank "1"^^<http://www.w3.org/2001/XMLSchema#int> ;
    a bib:MainTitleElement ;
    rdf:value "Clinical cardiopulmonary physiology." .

<nd95e57b81fac7218>
    dct:hasPart <nb952b1aee2ec439> ;
    a bf:Title ;
    rdf:value "Clinical cardiopulmonary physiology." .

```

