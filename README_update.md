# SPARQL UPDATE using the Jena `update` command line script without a server

Very simple: with the following data:

```
> more testdata/ex_listingCredits_1_bteko.ttl
<http://example.org/obj1> <http://bibliotek-o.org/ontology/listingCredits> "Credit" .
```

and the following SPARQL UPDATE command:

```
> more example-ru/listingCredits.ru
DELETE { ?s <http://bibliotek-o.org/ontology/listingCredits> ?o }
INSERT { ?s <http://id.loc.gov/ontologies/bibframe/credits> ?o }
WHERE  { ?s <http://bibliotek-o.org/ontology/listingCredits> ?o } ;
```

one can simply:

```
> update --dump --update=example-ru/listingCredits.ru --data=testdata/ex_listingCredits_1_bteko.ttl 
<http://example.org/obj1> <http://id.loc.gov/ontologies/bibframe/credits> "Credit" .
```
