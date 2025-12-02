# PAA Graph Knowledge Base

A toolkit for building a CIDOC-CRM compliant knowledge graph integrating data from the Perseus Digital Library and the Harvard Art Museums.

## Installation

This project is managed with [PDM](https://pdm-project.org/).

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd paa_graph_kb
    ```

2.  **Install dependencies:**
    ```bash
    make setup
    # OR manually:
    pdm install
    ```

3.  **Set up environment:**
    ```bash
    make setup-env
    # Edit .env with your API keys
    ```

## Usage

The project provides several CLI tools accessible via `pdm run` or the installed scripts:

*   `paa-browse-kb`: Browse terms and objects in the knowledge base.
*   `paa-run-constructs`: Apply SPARQL CONSTRUCT templates.
*   `paa-staging-loader`: Load and transform staging data.

See the `Makefile` for common workflow commands (e.g., `make local-all`, `make graphdb-all`).
