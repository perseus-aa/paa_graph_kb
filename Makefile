# PAA Graph Knowledge Base - Makefile
# Consolidates all workflow steps for staging data generation, Linked Art transformation,
# and GraphDB loading.

.PHONY: help setup-graphdb staging linkedart-local validate \
	graphdb-load-staging graphdb-run-constructs graphdb-all local-all clean

# Configuration
PYTHON := python
STAGING_FILE := staging.ttl
LINKEDART_FILE := linkedart.ttl
TEMPLATES_DIR := src/paa_graph_kb/resources/templates
SHAPES_FILE := src/paa_graph_kb/shapes/linkedart.ttl
GRAPHDB_ENV := src/paa_graph_kb/graphdb/graphdb_env

# HAM API parameters (override with make staging HAM_APIKEY=your_key HAM_PARAMS="culture=Greek" HAM_LIMIT=50)
HAM_APIKEY ?=
HAM_PARAMS ?= culture=Greek hasimage=1
HAM_LIMIT ?= 50

# Default target - show help
help:
	@echo "PAA Graph Knowledge Base - Available Make Targets"
	@echo "=================================================="
	@echo ""
	@echo "Setup:"
	@echo "  make setup-graphdb       - Copy graphdb_env.example to graphdb_env (edit manually after)"
	@echo ""
	@echo "Local Workflow (using rdflib):"
	@echo "  make staging             - Generate staging.ttl from HAM API"
	@echo "  make linkedart-local     - Build linkedart.ttl using local rdflib"
	@echo "  make validate            - Validate linkedart.ttl with SHACL shapes"
	@echo "  make local-all           - Run complete local workflow (staging → linkedart → validate)"
	@echo ""
	@echo "GraphDB Workflow:"
	@echo "  make graphdb-load-staging     - Load staging.ttl into GraphDB"
	@echo "  make graphdb-run-constructs   - Apply CONSTRUCT templates in GraphDB"
	@echo "  make graphdb-all              - Run complete GraphDB workflow (load → constructs)"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean               - Remove generated TTL files"
	@echo "  make help                - Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make staging HAM_APIKEY=your_key HAM_LIMIT=100"
	@echo "  make local-all HAM_APIKEY=your_key"
	@echo "  make graphdb-all"
	@echo ""

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
staging:
	@echo "Generating staging data from HAM API..."
	@if [ -z "$(HAM_APIKEY)" ]; then \
		echo "❌ Error: HAM_APIKEY is required."; \
		echo "Usage: make staging HAM_APIKEY=your_key"; \
		exit 1; \
	fi
	$(PYTHON) -m paa_graph_kb.cli.staging_loader \
		--apikey $(HAM_APIKEY) \
		--params $(HAM_PARAMS) \
		--limit $(HAM_LIMIT) \
		--out $(STAGING_FILE)
	@echo "✅ Generated $(STAGING_FILE)"

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

# Complete GraphDB workflow
graphdb-all: graphdb-load-staging graphdb-run-constructs
	@echo ""
	@echo "✅ GraphDB workflow complete!"
	@echo "   - Loaded staging data"
	@echo "   - Applied all CONSTRUCT templates"

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
