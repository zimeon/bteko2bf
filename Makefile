102063-conv:
	@echo "Processing minimal file 102063..."
	xsltproc vendor/marc2bibframe2-xsl/marc2bibframe2.xsl vendor/bib2lod/102063.min.xml | rapper -o turtle - http://example.org/ > 102063/102063-bf.ttl
	rapper -i turtle -o rdfxml 102063/102063-bf.ttl | rdf2dot | dot -Tpdf > 102063/102063-bf.pdf
	java -jar vendor/bib2lod/bib2lod.jar -c vendor/bib2lod/config.json; rapper -i turtle -o turtle -f xmlns:rdfs=\"http://www.w3.org/2000/01/rdf-schema#\" -f xmlns:bf=\"http://id.loc.gov/ontologies/bibframe/\" -f xmlns:bib=\"http://bibliotek-o.org/ontology/\" -f xmlns:dct=\"http://purl.org/dc/terms/\" -f xmlns:vivo=\"http://vivoweb.org/ontology/core#\" tmp/102063.min.ttl http://example.org/ > 102063/102063-bteko.ttl
	rapper -i turtle -o rdfxml 102063/102063-bteko.ttl | rdf2dot | dot -Tpdf > 102063/102063-bteko.pdf

all: 102063-conv
