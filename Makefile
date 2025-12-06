# PAA Graph Knowledge Base - Makefile
# Consolidates all workflow steps for staging data generation, Linked Art transformation,
# and GraphDB loading.

# Load environment variables from .env file if it exists
-include .env
export

.PHONY: help setup setup-env setup-graphdb staging linkedart-local validate \
	graphdb-load-ham-staging graphdb-run-constructs graphdb-load-ontology local-all clean \
	perseus-staging-objects perseus-staging-images perseus-staging-all entity-resolution \
	getty-bundle \
	graphdb-load-perseus-staging graphdb-load-perseus-linkedart graphdb-load-links \
	graphdb-load-getty \
	graphdb-ham-all graphdb-perseus-all graphdb-getty-all graphdb-all

# Configuration
PYTHON := python
TEMPLATES_DIR := src/paa_graph_kb/resources/templates
ONTOLOGIES_DIR := src/paa_graph_kb/resources/ontologies
SHAPES_FILE := src/paa_graph_kb/shapes/linkedart.ttl
GRAPHDB_ENV := src/paa_graph_kb/graphdb/graphdb_env
CIDOC_CRM_FILE := $(ONTOLOGIES_DIR)/CIDOC_CRM_v7.1.3.rdf
CIDOC_CRM_PC_FILE := $(ONTOLOGIES_DIR)/CIDOC_CRM_v7.1.3_PC.rdf
CIDOC_CRM_SUPP_FILE := $(ONTOLOGIES_DIR)/CIDOC_CRM_v7.1.3_Supplement.rdf

# Data directories
DATA_DIR := data
STAGING_DIR := $(DATA_DIR)/staging
LINKEDART_DIR := $(DATA_DIR)/linkedart
RECONCILIATION_DIR := $(DATA_DIR)/reconciliation

# HAM data files
HAM_STAGING := $(STAGING_DIR)/ham_staging.ttl
HAM_LINKEDART := $(LINKEDART_DIR)/ham_linkedart.ttl

# Perseus data files
PERSEUS_OBJECTS_JSON ?= $(DATA_DIR)/perseus/objects.json
PERSEUS_IMAGES_JSON ?= $(DATA_DIR)/perseus/images.json
PERSEUS_OBJECTS_TTL := $(STAGING_DIR)/perseus_objects.ttl
PERSEUS_IMAGES_TTL := $(STAGING_DIR)/perseus_images.ttl
PERSEUS_LINKEDART := $(LINKEDART_DIR)/perseus_linkedart.ttl
PERSEUS_IMAGES_LINKEDART := $(LINKEDART_DIR)/perseus_images_linkedart.ttl

# Getty data files
GETTY_OBJECTS_DIR := $(DATA_DIR)/getty/objects
GETTY_BUNDLE := $(STAGING_DIR)/getty_bundle.json

# Reconciliation Links
PERSEUS_HAM_LINKS := $(RECONCILIATION_DIR)/perseus_ham_links.ttl
PERSEUS_GETTY_LINKS := $(RECONCILIATION_DIR)/perseus_getty_links.ttl

# Legacy aliases for backwards compatibility
STAGING_FILE := $(HAM_STAGING)
LINKEDART_FILE := $(HAM_LINKEDART)

# HAM API parameters (loaded from .env, or override with make staging HAM_APIKEY=your_key)
HAM_PARAMS ?= culture=Greek hasimage=1
HAM_LIMIT ?= 50

# Default target - show help
help:
	@echo "PAA Graph Knowledge Base - Available Make Targets"
	@echo "=================================================="
	@echo ""
	@echo "Setup:"
	@echo "  make setup               - Install package with PDM"
	@echo "  make setup-env           - Copy dotenv template to .env"
	@echo "  make setup-graphdb       - Copy graphdb_env.example to graphdb_env"
	@echo ""
	@echo "Data Generation:"
	@echo "  make staging             - Generate HAM staging from API"
	@echo "  make perseus-staging-all - Generate Perseus staging (objects + images)"
	@echo "  make linkedart-local     - Transform all staging to Linked Art (rdflib)"
	@echo "  make entity-resolution   - Generate Perseus-HAM links"
	@echo "  make getty-bundle        - Bundle cached Getty JSON-LDs into single file"
	@echo ""
	@echo "GraphDB Loading:"
	@echo "  make graphdb-load-ontology           - Load CIDOC-CRM ontology"
	@echo "  make graphdb-load-ham-staging        - Load HAM staging"
	@echo "  make graphdb-run-constructs          - Run HAM transforms in GraphDB"
	@echo "  make graphdb-load-perseus-staging    - Load Perseus staging"
	@echo "  make graphdb-load-perseus-linkedart  - Load Perseus Linked Art"
	@echo "  make graphdb-load-getty              - Load Getty Linked Art (JSON-LD)"
	@echo "  make graphdb-load-links              - Load all reconciliation links"
	@echo ""
	@echo "Complete Workflows:"
	@echo "  make graphdb-ham-all                 - Load/Transform HAM data"
	@echo "  make graphdb-perseus-all             - Load Perseus data"
	@echo "  make graphdb-getty-all               - Load Getty data"
	@echo "  make graphdb-all                     - Load EVERYTHING"

setup:
	@echo "Installing paa_graph_kb package..."
	pdm install

setup-env:
	@if [ -f ".env" ]; then echo ".env exists."; else cp dotenv .env; echo "Created .env"; fi

setup-graphdb:
	@if [ -f "$(GRAPHDB_ENV)" ]; then echo "$(GRAPHDB_ENV) exists."; else cp src/paa_graph_kb/graphdb/graphdb_env.example $(GRAPHDB_ENV); echo "Created $(GRAPHDB_ENV)"; fi

# HAM Staging
staging: $(HAM_STAGING)
$(HAM_STAGING):
	@mkdir -p $(STAGING_DIR)
	$(PYTHON) -m paa_graph_kb.cli.staging_loader \
		$(if $(HAM_APIKEY),--apikey $(HAM_APIKEY),) \
		--params $(HAM_PARAMS) \
		--limit $(HAM_LIMIT) \
		--out $(HAM_STAGING)

# Perseus Staging
perseus-staging-objects: $(PERSEUS_OBJECTS_JSON)
	@mkdir -p $(STAGING_DIR)
	$(PYTHON) -m paa_graph_kb.cli.perseus_staging_loader \
		--objects $(PERSEUS_OBJECTS_JSON) \
		--out-objects $(PERSEUS_OBJECTS_TTL)

perseus-staging-images: $(PERSEUS_IMAGES_JSON)
	@mkdir -p $(STAGING_DIR)
	$(PYTHON) -m paa_graph_kb.cli.perseus_staging_loader \
		--images $(PERSEUS_IMAGES_JSON) \
		--out-images $(PERSEUS_IMAGES_TTL)

perseus-staging-all: perseus-staging-objects perseus-staging-images

# Getty Bundle
getty-bundle: $(GETTY_BUNDLE)
$(GETTY_BUNDLE):
	@echo "Bundling Getty JSON-LD files..."
	@mkdir -p $(STAGING_DIR)
	$(PYTHON) -m paa_graph_kb.utils.bundle_jsonld \
		--input-dir $(GETTY_OBJECTS_DIR) \
		--output $(GETTY_BUNDLE)

# Entity Resolution (Perseus <-> HAM)
entity-resolution: $(PERSEUS_HAM_LINKS)
$(PERSEUS_HAM_LINKS): $(PERSEUS_OBJECTS_TTL) $(HAM_STAGING)
	@mkdir -p $(RECONCILIATION_DIR)
	$(PYTHON) -m paa_graph_kb.cli.entity_resolution \
		--perseus-staging $(PERSEUS_OBJECTS_TTL) \
		--ham-staging $(HAM_STAGING) \
		--out $(PERSEUS_HAM_LINKS)

# Linked Art Transformation (Perseus & HAM)
linkedart-local: $(HAM_LINKEDART) $(PERSEUS_LINKEDART)

$(HAM_LINKEDART): $(HAM_STAGING)
	@mkdir -p $(LINKEDART_DIR)
	$(PYTHON) -m paa_graph_kb.run_constructs \
		--staging $(HAM_STAGING) \
		--templates $(TEMPLATES_DIR) \
		--out $(HAM_LINKEDART)

$(PERSEUS_LINKEDART): $(PERSEUS_OBJECTS_TTL)
	@mkdir -p $(LINKEDART_DIR)
	$(PYTHON) -m paa_graph_kb.run_constructs \
		--staging $(PERSEUS_OBJECTS_TTL) \
		--templates $(TEMPLATES_DIR) \
		--out $(PERSEUS_LINKEDART)

# GraphDB: Load Ontology
graphdb-load-ontology: $(GRAPHDB_ENV)
	@bash -c 'source $(GRAPHDB_ENV) && \
		curl -s -f -X POST "$$GRAPHDB_BASE/repositories/$$REPOSITORY/statements?context=%3Chttp://www.cidoc-crm.org/cidoc-crm/%3E" \
		-H "Content-Type: application/rdf+xml" \
		--data-binary "@$(CIDOC_CRM_FILE)" && echo "✅ Main ontology loaded"'
	@bash -c 'source $(GRAPHDB_ENV) && \
		curl -s -f -X POST "$$GRAPHDB_BASE/repositories/$$REPOSITORY/statements?context=%3Chttp://www.cidoc-crm.org/cidoc-crm/%3E" \
		-H "Content-Type: application/rdf+xml" \
		--data-binary "@$(CIDOC_CRM_PC_FILE)" && echo "✅ Property Classes loaded"'
	@bash -c 'source $(GRAPHDB_ENV) && \
		curl -s -f -X POST "$$GRAPHDB_BASE/repositories/$$REPOSITORY/statements?context=%3Chttp://www.cidoc-crm.org/cidoc-crm/%3E" \
		-H "Content-Type: application/rdf+xml" \
		--data-binary "@$(CIDOC_CRM_SUPP_FILE)" && echo "✅ Supplement loaded"'

# GraphDB: Load HAM
graphdb-load-ham-staging: $(HAM_STAGING) $(GRAPHDB_ENV)
	@bash src/paa_graph_kb/graphdb/load_staging.sh $(HAM_STAGING)

graphdb-run-constructs: $(GRAPHDB_ENV)
	@bash src/paa_graph_kb/graphdb/run_constructs.sh $(TEMPLATES_DIR)

graphdb-ham-all: graphdb-load-ham-staging graphdb-run-constructs

# GraphDB: Load Perseus
graphdb-load-perseus-staging: $(PERSEUS_OBJECTS_TTL) $(PERSEUS_IMAGES_TTL) $(GRAPHDB_ENV)
	@bash -c 'source $(GRAPHDB_ENV) && src/paa_graph_kb/graphdb/load_to_graph.sh $(PERSEUS_OBJECTS_TTL) "$$PERSEUS_STAGING_GRAPH"'
	@bash -c 'source $(GRAPHDB_ENV) && src/paa_graph_kb/graphdb/load_to_graph.sh $(PERSEUS_IMAGES_TTL) "$$PERSEUS_IMAGES_GRAPH"'

graphdb-load-perseus-linkedart: $(PERSEUS_LINKEDART) $(GRAPHDB_ENV)
	@bash -c 'source $(GRAPHDB_ENV) && src/paa_graph_kb/graphdb/load_to_graph.sh $(PERSEUS_LINKEDART) "$$PERSEUS_LINKEDART_GRAPH"'

$(PERSEUS_IMAGES_LINKEDART): $(PERSEUS_IMAGES_TTL)
	@echo "Building Perseus images Linked Art from staging..."
	@mkdir -p $(LINKEDART_DIR)
	$(PYTHON) -m paa_graph_kb.run_constructs \
		--staging $(PERSEUS_IMAGES_TTL) \
		--templates $(TEMPLATES_DIR) \
		--out $(PERSEUS_IMAGES_LINKEDART)
	@echo "✅ Generated $(PERSEUS_IMAGES_LINKEDART)"

graphdb-perseus-all: graphdb-load-perseus-staging graphdb-load-perseus-linkedart

# GraphDB: Load Getty
graphdb-load-getty: $(GETTY_BUNDLE) $(GRAPHDB_ENV)
	@echo "Loading Getty JSON-LD into GraphDB..."
	@bash -c 'source $(GRAPHDB_ENV) && \
		src/paa_graph_kb/graphdb/load_to_graph.sh $(GETTY_BUNDLE) "urn:graph:getty" "application/ld+json"'

graphdb-getty-all:getty-bundle graphdb-load-getty

# GraphDB: Load Links
graphdb-load-links: $(GRAPHDB_ENV)
	@echo "Loading reconciliation links..."
	@if [ -f "$(PERSEUS_HAM_LINKS)" ]; then \
		bash -c 'source $(GRAPHDB_ENV) && src/paa_graph_kb/graphdb/load_to_graph.sh $(PERSEUS_HAM_LINKS) "$$EQUIVALENCES_GRAPH"'; \
	fi
	@if [ -f "$(PERSEUS_GETTY_LINKS)" ]; then \
		bash -c 'source $(GRAPHDB_ENV) && src/paa_graph_kb/graphdb/load_to_graph.sh $(PERSEUS_GETTY_LINKS) "$$EQUIVALENCES_GRAPH"'; \
	fi

# GraphDB: Load All
graphdb-all: graphdb-ham-all graphdb-perseus-all graphdb-getty-all graphdb-load-links
	@echo "✅ All datasets loaded."

clean:
	rm -rf $(STAGING_DIR) $(LINKEDART_DIR) $(RECONCILIATION_DIR)
