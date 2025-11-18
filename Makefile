# PAA Graph Knowledge Base - Makefile
# Consolidates all workflow steps for staging data generation, Linked Art transformation,
# and GraphDB loading.

# Load environment variables from .env file if it exists
-include .env
export

.PHONY: help setup-env setup-graphdb staging linkedart-local validate \
	graphdb-load-staging graphdb-run-constructs graphdb-load-ontology graphdb-all local-all clean \
	perseus-staging-objects perseus-staging-images perseus-staging-all entity-resolution

# Configuration
PYTHON := python
STAGING_FILE := staging.ttl
LINKEDART_FILE := linkedart.ttl
TEMPLATES_DIR := src/paa_graph_kb/resources/templates
ONTOLOGIES_DIR := src/paa_graph_kb/resources/ontologies
SHAPES_FILE := src/paa_graph_kb/shapes/linkedart.ttl
GRAPHDB_ENV := src/paa_graph_kb/graphdb/graphdb_env
CIDOC_CRM_FILE := $(ONTOLOGIES_DIR)/CIDOC_CRM_v7.1.3.rdf
CIDOC_CRM_PC_FILE := $(ONTOLOGIES_DIR)/CIDOC_CRM_v7.1.3_PC.rdf
CIDOC_CRM_SUPP_FILE := $(ONTOLOGIES_DIR)/CIDOC_CRM_v7.1.3_Supplement.rdf

# HAM API parameters (loaded from .env, or override with make staging HAM_APIKEY=your_key)
# If not set in .env or command line, staging target will show an error
HAM_PARAMS ?= culture=Greek hasimage=1
HAM_LIMIT ?= 50

# Perseus data files
PERSEUS_OBJECTS_JSON ?= data/perseus/objects.json
PERSEUS_IMAGES_JSON ?= data/perseus/images.json
PERSEUS_OBJECTS_TTL := data/staging/perseus_objects.ttl
PERSEUS_IMAGES_TTL := data/staging/perseus_images.ttl
ENTITY_EQUIVALENCES := entity_equivalences.ttl

# Default target - show help
help:
	@echo "PAA Graph Knowledge Base - Available Make Targets"
	@echo "=================================================="
	@echo ""
	@echo "Setup:"
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
	@echo "  make graphdb-load-staging     - Load staging.ttl into GraphDB"
	@echo "  make graphdb-run-constructs   - Apply CONSTRUCT templates in GraphDB"
	@echo "  make graphdb-load-ontology    - Load CIDOC-CRM ontology into GraphDB (optional)"
	@echo "  make graphdb-all              - Run complete GraphDB workflow (load → constructs)"
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

# Generate staging.ttl from HAM API
# Reads HAM_APIKEY from .env by default, or override with HAM_APIKEY=key on command line
staging:
	@echo "Generating staging data from HAM API..."
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
		--out $(STAGING_FILE)
	@echo "✅ Generated $(STAGING_FILE)"

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
entity-resolution: $(PERSEUS_OBJECTS_TTL) $(STAGING_FILE)
	@echo "🔗 Running entity resolution..."
	$(PYTHON) -m paa_graph_kb.cli.entity_resolution \
		--perseus-staging $(PERSEUS_OBJECTS_TTL) \
		--ham-staging $(STAGING_FILE) \
		--out $(ENTITY_EQUIVALENCES)
	@echo ""
	@echo "✅ Entity resolution complete!"
	@echo "   Output: $(ENTITY_EQUIVALENCES)"

# Build Linked Art locally using rdflib
linkedart-local: $(STAGING_FILE)
	@echo "Building Linked Art from staging using rdflib..."
	$(PYTHON) -m paa_graph_kb.run_constructs \
		--staging $(STAGING_FILE) \
		--templates $(TEMPLATES_DIR) \
		--out $(LINKEDART_FILE)
	@echo "✅ Generated $(LINKEDART_FILE)"

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

# Load staging data into GraphDB
graphdb-load-staging: $(STAGING_FILE) $(GRAPHDB_ENV)
	@echo "Loading staging data into GraphDB..."
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

# Complete GraphDB workflow
graphdb-all: graphdb-load-staging graphdb-run-constructs
	@echo ""
	@echo "✅ GraphDB workflow complete!"
	@echo "   - Loaded staging data"
	@echo "   - Applied all CONSTRUCT templates"
	@echo ""
	@echo "💡 Tip: To enable OWL inferencing with CIDOC-CRM:"
	@echo "   1. Run: make graphdb-load-ontology"
	@echo "   2. Enable reasoning in GraphDB Workbench (Setup → Repositories)"

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	@rm -f $(STAGING_FILE) $(LINKEDART_FILE) linkedart_new.ttl
	@echo "✅ Cleaned: $(STAGING_FILE) $(LINKEDART_FILE) linkedart_new.ttl"

# Ensure staging file exists
$(STAGING_FILE):
	@echo "❌ Error: $(STAGING_FILE) not found."
	@echo "Run: make staging HAM_APIKEY=your_key"
	@exit 1

# Ensure linkedart file exists
$(LINKEDART_FILE):
	@echo "❌ Error: $(LINKEDART_FILE) not found."
	@echo "Run: make linkedart-local"
	@exit 1

# Ensure GraphDB config exists
$(GRAPHDB_ENV):
	@echo "❌ Error: GraphDB configuration not found."
	@echo "Run: make setup-graphdb"
	@echo "Then edit $(GRAPHDB_ENV) with your GraphDB connection details."
	@exit 1
