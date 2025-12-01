# PAA Graph Knowledge Base - Makefile
# Consolidates all workflow steps for staging data generation, Linked Art transformation,
# and GraphDB loading.

# Load environment variables from .env file if it exists
-include .env
export

.PHONY: help setup setup-env setup-graphdb staging linkedart-local validate \
	graphdb-load-ham-staging graphdb-run-constructs graphdb-load-ontology local-all clean \
	perseus-staging-objects perseus-staging-images perseus-staging-all entity-resolution \
	graphdb-load-perseus-staging graphdb-load-perseus-linkedart graphdb-load-equivalences \
	graphdb-ham-all graphdb-perseus-all graphdb-all

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
EQUIVALENCES_DIR := $(DATA_DIR)/equivalences

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

# Entity resolution
ENTITY_EQUIVALENCES := $(EQUIVALENCES_DIR)/entity_equivalences.ttl

# Legacy aliases for backwards compatibility
STAGING_FILE := $(HAM_STAGING)
LINKEDART_FILE := $(HAM_LINKEDART)

# HAM API parameters (loaded from .env, or override with make staging HAM_APIKEY=your_key)
# If not set in .env or command line, staging target will show an error
HAM_PARAMS ?= culture=Greek hasimage=1
HAM_LIMIT ?= 50

# Default target - show help
help:
	@echo "PAA Graph Knowledge Base - Available Make Targets"
	@echo "=================================================="
	@echo ""
	@echo "Setup:"
	@echo "  make setup               - Install package with PDM (run after cloning)"
	@echo "  make setup-env           - Copy dotenv template to .env (edit with your HAM API key)"
	@echo "  make setup-graphdb       - Copy graphdb_env.example to graphdb_env (edit manually after)"
	@echo ""
	@echo "Local Workflow (using rdflib):"
	@echo "  make staging             - Generate staging.ttl from HAM API (uses HAM_APIKEY from .env)"
	@echo "  make linkedart-local     - Build linkedart.ttl using local rdflib"
	@echo "  make validate            - Validate linkedart.ttl with SHACL shapes"
	@echo "  make local-all           - Run complete local workflow (staging → linkedart → validate)"
	@echo ""
	@echo "Perseus Data Integration:"
	@echo "  make perseus-staging-objects  - Convert Perseus objects JSON to staging RDF"
	@echo "  make perseus-staging-images   - Convert Perseus images JSON to staging RDF"
	@echo "  make perseus-staging-all      - Convert both Perseus objects and images"
	@echo "  make entity-resolution        - Link Perseus and HAM objects via owl:sameAs"
	@echo ""
	@echo "GraphDB Workflow:"
	@echo "  make graphdb-load-ham-staging        - Load HAM staging.ttl into GraphDB"
	@echo "  make graphdb-run-constructs          - Apply CONSTRUCT templates in GraphDB"
	@echo "  make graphdb-load-ontology           - Load CIDOC-CRM ontology (optional)"
	@echo "  make graphdb-load-perseus-staging    - Load Perseus staging (objects + images)"
	@echo "  make graphdb-load-perseus-linkedart  - Load Perseus CRM (objects + images)"
	@echo "  make graphdb-load-equivalences       - Load entity equivalences (owl:sameAs)"
	@echo ""
	@echo "GraphDB Complete Workflows:"
	@echo "  make graphdb-ham-all                 - Load HAM data only"
	@echo "  make graphdb-perseus-all             - Load Perseus data + equivalences"
	@echo "  make graphdb-all                     - Load EVERYTHING (HAM + Perseus + equivalences)"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean               - Remove generated TTL files"
	@echo "  make help                - Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  # First time setup"
	@echo "  make setup-env                              # Creates .env from template"
	@echo "  # Edit .env to add your HAM_APIKEY"
	@echo ""
	@echo "  # Run workflows (uses .env automatically)"
	@echo "  make local-all                              # Complete local workflow"
	@echo "  make staging HAM_LIMIT=200                  # Override default limit"
	@echo "  make staging HAM_APIKEY=key HAM_LIMIT=100   # Override .env settings"
	@echo ""

# Install package in editable mode using PDM
setup:
	@echo "Installing paa_graph_kb package with PDM..."
	pdm install
	@echo "✅ Package installed. You can now run make targets."

# Setup .env file from template
setup-env:
	@echo "Setting up .env file..."
	@if [ -f ".env" ]; then \
		echo "⚠️  .env already exists. Skipping."; \
	else \
		cp dotenv .env; \
		echo "✅ Created .env from dotenv template"; \
		echo "⚠️  Please edit .env to set your HAM_APIKEY and other configuration."; \
	fi

# Setup GraphDB configuration
setup-graphdb:
	@echo "Setting up GraphDB configuration..."
	@if [ -f "$(GRAPHDB_ENV)" ]; then \
		echo "⚠️  $(GRAPHDB_ENV) already exists. Skipping."; \
	else \
		cp src/paa_graph_kb/graphdb/graphdb_env.example $(GRAPHDB_ENV); \
		echo "✅ Created $(GRAPHDB_ENV)"; \
		echo "⚠️  Please edit $(GRAPHDB_ENV) to configure your GraphDB connection."; \
	fi

# Generate HAM staging data from HAM API
# Reads HAM_APIKEY from .env by default, or override with HAM_APIKEY=key on command line
staging: $(HAM_STAGING)

$(HAM_STAGING):
	@echo "Generating HAM staging data from API..."
	@mkdir -p $(STAGING_DIR)
	@if [ ! -f ".env" ] && [ -z "$(HAM_APIKEY)" ]; then \
		echo "⚠️  No .env file found and HAM_APIKEY not provided."; \
		echo "   Run: make setup-env"; \
		echo "   Then edit .env to add your HAM_APIKEY"; \
		echo "   Or provide HAM_APIKEY on command line: make staging HAM_APIKEY=your_key"; \
	fi
	$(PYTHON) -m paa_graph_kb.cli.staging_loader \
		$(if $(HAM_APIKEY),--apikey $(HAM_APIKEY),) \
		--params $(HAM_PARAMS) \
		--limit $(HAM_LIMIT) \
		--out $(HAM_STAGING)
	@echo "✅ Generated $(HAM_STAGING)"

# Perseus staging targets
perseus-staging-objects: $(PERSEUS_OBJECTS_JSON)
	@echo "Converting Perseus objects to staging RDF..."
	@mkdir -p data/staging
	$(PYTHON) -m paa_graph_kb.cli.perseus_staging_loader \
		--objects $(PERSEUS_OBJECTS_JSON) \
		--out-objects $(PERSEUS_OBJECTS_TTL)
	@echo "✅ Generated $(PERSEUS_OBJECTS_TTL)"

perseus-staging-images: $(PERSEUS_IMAGES_JSON)
	@echo "Converting Perseus images to staging RDF..."
	@mkdir -p data/staging
	$(PYTHON) -m paa_graph_kb.cli.perseus_staging_loader \
		--images $(PERSEUS_IMAGES_JSON) \
		--out-images $(PERSEUS_IMAGES_TTL)
	@echo "✅ Generated $(PERSEUS_IMAGES_TTL)"

perseus-staging-all: perseus-staging-objects perseus-staging-images
	@echo ""
	@echo "✅ Perseus staging complete!"
	@echo "   - Generated: $(PERSEUS_OBJECTS_TTL)"
	@echo "   - Generated: $(PERSEUS_IMAGES_TTL)"

# Entity resolution - Link Perseus and HAM objects
# Entity resolution - creates entity_equivalences.ttl
$(ENTITY_EQUIVALENCES): $(PERSEUS_OBJECTS_TTL) $(HAM_STAGING)
	@echo "🔗 Running entity resolution..."
	@mkdir -p $(EQUIVALENCES_DIR)
	$(PYTHON) -m paa_graph_kb.cli.entity_resolution \
		--perseus-staging $(PERSEUS_OBJECTS_TTL) \
		--ham-staging $(HAM_STAGING) \
		--out $(ENTITY_EQUIVALENCES)
	@echo ""
	@echo "✅ Entity resolution complete!"
	@echo "   Output: $(ENTITY_EQUIVALENCES)"

# Convenience alias for entity resolution
entity-resolution: $(ENTITY_EQUIVALENCES)

# Build Linked Art locally using rdflib
linkedart-local: $(HAM_LINKEDART)

$(HAM_LINKEDART): $(HAM_STAGING)
	@echo "Building HAM Linked Art from staging using rdflib..."
	@mkdir -p $(LINKEDART_DIR)
	$(PYTHON) -m paa_graph_kb.run_constructs \
		--staging $(HAM_STAGING) \
		--templates $(TEMPLATES_DIR) \
		--out $(HAM_LINKEDART)
	@echo "✅ Generated $(HAM_LINKEDART)"

# Validate Linked Art with SHACL
validate: $(LINKEDART_FILE)
	@echo "Validating Linked Art with SHACL shapes..."
	$(PYTHON) -m paa_graph_kb.cli.validate_shacl \
		--data $(LINKEDART_FILE) \
		--shapes $(SHAPES_FILE)
	@echo "✅ Validation complete"

# Complete local workflow
local-all: staging linkedart-local validate
	@echo ""
	@echo "✅ Local workflow complete!"
	@echo "   - Generated: $(STAGING_FILE)"
	@echo "   - Generated: $(LINKEDART_FILE)"
	@echo "   - Validated against SHACL shapes"

# Load HAM staging data into GraphDB
graphdb-load-ham-staging: $(STAGING_FILE) $(GRAPHDB_ENV)
	@echo "Loading HAM staging data into GraphDB..."
	@bash src/paa_graph_kb/graphdb/load_staging.sh $(STAGING_FILE)

# Run CONSTRUCT templates in GraphDB
graphdb-run-constructs: $(GRAPHDB_ENV)
	@echo "Running CONSTRUCT templates in GraphDB..."
	@bash src/paa_graph_kb/graphdb/run_constructs.sh $(TEMPLATES_DIR)

# Load CIDOC-CRM ontology into GraphDB (all three files)
graphdb-load-ontology: $(GRAPHDB_ENV)
	@echo "Loading CIDOC-CRM v7.1.3 ontology files into GraphDB..."
	@if [ ! -f "$(CIDOC_CRM_FILE)" ]; then \
		echo "❌ Error: CIDOC-CRM main ontology not found at $(CIDOC_CRM_FILE)"; \
		echo "   Please ensure ontology files are present in:"; \
		echo "   $(ONTOLOGIES_DIR)/"; \
		exit 1; \
	fi
	@if [ ! -f "$(CIDOC_CRM_PC_FILE)" ]; then \
		echo "❌ Error: CIDOC-CRM Property Classes not found at $(CIDOC_CRM_PC_FILE)"; \
		exit 1; \
	fi
	@if [ ! -f "$(CIDOC_CRM_SUPP_FILE)" ]; then \
		echo "❌ Error: CIDOC-CRM Supplement not found at $(CIDOC_CRM_SUPP_FILE)"; \
		exit 1; \
	fi
	@echo "Loading 1/3: Main ontology..."
	@bash -c 'source $(GRAPHDB_ENV) && \
		curl -s -f -X POST "$$GRAPHDB_BASE/repositories/$$REPOSITORY/statements?context=%3Chttp://www.cidoc-crm.org/cidoc-crm/%3E" \
		-H "Content-Type: application/rdf+xml" \
		--data-binary "@$(CIDOC_CRM_FILE)" && \
		echo "  ✅ Main ontology loaded" || \
		(echo "  ❌ Failed to load. Is GraphDB running at $$GRAPHDB_BASE?" && exit 1)'
	@echo "Loading 2/3: Property Classes (PC)..."
	@bash -c 'source $(GRAPHDB_ENV) && \
		curl -s -f -X POST "$$GRAPHDB_BASE/repositories/$$REPOSITORY/statements?context=%3Chttp://www.cidoc-crm.org/cidoc-crm/%3E" \
		-H "Content-Type: application/rdf+xml" \
		--data-binary "@$(CIDOC_CRM_PC_FILE)" && \
		echo "  ✅ Property Classes loaded" || \
		(echo "  ❌ Failed to load PC file" && exit 1)'
	@echo "Loading 3/3: Supplement (rdfs:label extensions)..."
	@bash -c 'source $(GRAPHDB_ENV) && \
		curl -s -f -X POST "$$GRAPHDB_BASE/repositories/$$REPOSITORY/statements?context=%3Chttp://www.cidoc-crm.org/cidoc-crm/%3E" \
		-H "Content-Type: application/rdf+xml" \
		--data-binary "@$(CIDOC_CRM_SUPP_FILE)" && \
		echo "  ✅ Supplement loaded" || \
		(echo "  ❌ Failed to load Supplement file" && exit 1)'
	@echo ""
	@echo "✅ All CIDOC-CRM v7.1.3 files loaded into <http://www.cidoc-crm.org/cidoc-crm/>"
	@echo ""
	@echo "💡 Next steps:"
	@echo "   1. Enable OWL reasoning in GraphDB (Setup → Repositories)"
	@echo "   2. Set Ruleset to 'OWL-Horst (Optimized)' or 'OWL-Max'"
	@echo "   3. Save and restart repository"

# HAM-only GraphDB workflow
graphdb-ham-all: graphdb-load-ham-staging graphdb-run-constructs
	@echo ""
	@echo "✅ HAM data loaded to GraphDB!"
	@echo "   - HAM staging data"
	@echo "   - HAM CRM (Linked Art)"
	@echo ""
	@echo "💡 Next: make graphdb-perseus-all  (to load Perseus data)"

# Load Perseus staging data to GraphDB
graphdb-load-perseus-staging: $(PERSEUS_OBJECTS_TTL) $(PERSEUS_IMAGES_TTL) $(GRAPHDB_ENV)
	@echo "📦 Loading Perseus staging data to GraphDB..."
	@bash -c 'source $(GRAPHDB_ENV) && \
		src/paa_graph_kb/graphdb/load_to_graph.sh $(PERSEUS_OBJECTS_TTL) "$$PERSEUS_STAGING_GRAPH"'
	@bash -c 'source $(GRAPHDB_ENV) && \
		src/paa_graph_kb/graphdb/load_to_graph.sh $(PERSEUS_IMAGES_TTL) "$$PERSEUS_IMAGES_GRAPH"'
	@echo "✅ Perseus staging data loaded"

# Load Perseus CRM (Linked Art) data to GraphDB
graphdb-load-perseus-linkedart: $(PERSEUS_LINKEDART) $(PERSEUS_IMAGES_LINKEDART) $(GRAPHDB_ENV)
	@echo "📦 Loading Perseus CRM data to GraphDB..."
	@bash -c 'source $(GRAPHDB_ENV) && \
		src/paa_graph_kb/graphdb/load_to_graph.sh $(PERSEUS_LINKEDART) "$$PERSEUS_LINKEDART_GRAPH"'
	@bash -c 'source $(GRAPHDB_ENV) && \
		src/paa_graph_kb/graphdb/load_to_graph.sh $(PERSEUS_IMAGES_LINKEDART) "$$PERSEUS_IMAGES_GRAPH"'
	@echo "✅ Perseus CRM data loaded"

# Generate Perseus Linked Art (automatic dependency)
$(PERSEUS_LINKEDART): $(PERSEUS_OBJECTS_TTL)
	@echo "Building Perseus Linked Art from staging..."
	@mkdir -p $(LINKEDART_DIR)
	$(PYTHON) -m paa_graph_kb.cli.run_constructs \
		--staging $(PERSEUS_OBJECTS_TTL) \
		--templates $(TEMPLATES_DIR) \
		--out $(PERSEUS_LINKEDART)
	@echo "✅ Generated $(PERSEUS_LINKEDART)"

$(PERSEUS_IMAGES_LINKEDART): $(PERSEUS_IMAGES_TTL)
	@echo "Building Perseus images Linked Art from staging..."
	@mkdir -p $(LINKEDART_DIR)
	$(PYTHON) -m paa_graph_kb.cli.run_constructs \
		--staging $(PERSEUS_IMAGES_TTL) \
		--templates $(TEMPLATES_DIR) \
		--out $(PERSEUS_IMAGES_LINKEDART)
	@echo "✅ Generated $(PERSEUS_IMAGES_LINKEDART)"

# Load entity equivalences to GraphDB
graphdb-load-equivalences: $(ENTITY_EQUIVALENCES) $(GRAPHDB_ENV)
	@echo "🔗 Loading entity equivalences to GraphDB..."
	@bash -c 'source $(GRAPHDB_ENV) && \
		src/paa_graph_kb/graphdb/load_to_graph.sh $(ENTITY_EQUIVALENCES) "$$EQUIVALENCES_GRAPH"'
	@echo "✅ Entity equivalences loaded"

# Perseus-only GraphDB workflow
graphdb-perseus-all: graphdb-load-perseus-staging graphdb-load-perseus-linkedart graphdb-load-equivalences
	@echo ""
	@echo "✅ Perseus data loaded to GraphDB!"
	@echo "   - Perseus staging (objects + images)"
	@echo "   - Perseus CRM (Linked Art)"
	@echo "   - Entity equivalences (owl:sameAs)"
	@echo ""
	@echo "💡 Next: Try the cross-dataset queries in src/paa_graph_kb/graphdb/README.md"

# Load ALL data to GraphDB (HAM + Perseus + equivalences)
graphdb-all: graphdb-ham-all graphdb-perseus-all
	@echo ""
	@echo "🎉 COMPLETE KNOWLEDGE GRAPH LOADED!"
	@echo "   ✅ HAM data (staging + CRM)"
	@echo "   ✅ Perseus data (staging + CRM + images)"
	@echo "   ✅ Entity equivalences (95 owl:sameAs pairs)"
	@echo ""
	@echo "📊 Your GraphDB now contains:"
	@echo "   - 6 named graphs (HAM, Perseus, equivalences)"
	@echo "   - Multi-source linked data with automatic reasoning"
	@echo ""
	@echo "💡 Try these SPARQL queries:"
	@echo "   - List all graphs: SELECT ?g (COUNT(*) as ?n) WHERE { GRAPH ?g {?s ?p ?o} } GROUP BY ?g"
	@echo "   - Find matches: See examples in src/paa_graph_kb/graphdb/README.md"

# Clean generated files
clean:
	@echo "Cleaning generated data files..."
	@rm -rf $(STAGING_DIR) $(LINKEDART_DIR) $(EQUIVALENCES_DIR)
	@echo "✅ Cleaned data directories"

# Ensure GraphDB config exists
$(GRAPHDB_ENV):
	@echo "❌ Error: GraphDB configuration not found."
	@echo "Run: make setup-graphdb"
	@echo "Then edit $(GRAPHDB_ENV) with your GraphDB connection details."
	@exit 1
