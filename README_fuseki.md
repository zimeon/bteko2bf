# SPARQL UPDATE using a Fuseki server

## Installation

On OSX Jena Fuseki can be installed with:

```
> brew install fuseki
> fuseki-server --version
Jena:       VERSION: 3.3.0
Jena:       BUILD_DATE: 2017-05-02T17:38:25+0000
ARQ:        VERSION: 3.3.0
ARQ:        BUILD_DATE: 2017-05-02T17:38:25+0000
RIOT:       VERSION: 3.3.0
RIOT:       BUILD_DATE: 2017-05-02T17:38:25+0000
TDB:        VERSION: 3.3.0
TDB:        BUILD_DATE: 2017-05-02T17:38:25+0000
Fuseki:     VERSION: 2.6.0
Fuseki:     BUILD_DATE: 2017-05-02T17:38:25+0000
```

## Window 1 - Run Fuseki sever

The follow
```
> fuseki-server --update --mem --localhost /dataset
[2017-08-04 17:40:27] Server     INFO  Dataset: in-memory
[2017-08-04 17:40:27] Server     INFO  Fuseki 2.6.0
[2017-08-04 17:40:27] Server     INFO  Incoming connections limited to localhost
[2017-08-04 17:40:27] Config     INFO  FUSEKI_HOME=/usr/local/Cellar/fuseki/2.6.0/libexec
[2017-08-04 17:40:27] Config     INFO  FUSEKI_BASE=/usr/local/var/fuseki
[2017-08-04 17:40:27] Servlet    INFO  Initializing Shiro environment
[2017-08-04 17:40:27] Config     INFO  Shiro file: file:///usr/local/var/fuseki/shiro.ini
[2017-08-04 17:40:27] Config     INFO  Template file: templates/config-mem
[2017-08-04 17:40:28] Config     INFO  Register: /dataset
[2017-08-04 17:40:28] Server     INFO  Started 2017/08/04 17:40:28 EDT on port 3030
```

N.B.

  * `--update` is required to support SPARQL UPDATE
  * `--mem` means use in-memory store
  * `--localhost` limits access to locahost (do this unless you need not to)
  * It seems that it would be nice to load an initial graph into the server when starting it up, which is supported with the `--file` option. However, doing so results in a read-only dataset.

## Window 2 - Load graph, transform, download

### Load graph

```
> s-put http://localhost:3030/dataset default testdata/ex_listingCredits_1_bteko.ttl 
```

where:

```
> more testdata/ex_listingCredits_1_bteko.ttl
<http://example.org/obj1> <http://bibliotek-o.org/ontology/listingCredits> "Credit" .
```
### Transform

```
> s-update --service=http://localhost:3030/dataset --update=example-ru/listingCredits.ru
```

where:

```
> more example-ru/listingCredits.ru
DELETE { ?s <http://bibliotek-o.org/ontology/listingCredits> ?o }
INSERT { ?s <http://id.loc.gov/ontologies/bibframe/credits> ?o }
WHERE  { ?s <http://bibliotek-o.org/ontology/listingCredits> ?o } ;
```

### Download

```
> s-get http://localhost:3030/dataset default > output.ttl
```

where:

```
> more output.ttl 
<http://example.org/obj1>
        <http://id.loc.gov/ontologies/bibframe/credits>
                "Credit" .
```

and we can test against the expected output:

```
> rdfdiff output.ttl testdata/ex_listingCredits_1_bf.ttl N3 N3
output.ttl testdata/ex_listingCredits_1_bf.ttl N3 N3 null null
models are equal
```

### Clear

```
> s-update --service=http://localhost:3030/dataset --update=example-ru/clear.ru
> s-get http://localhost:3030/dataset default
>
```
