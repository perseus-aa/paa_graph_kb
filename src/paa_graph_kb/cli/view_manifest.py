import typer
from typing import Annotated, Optional
from enum import Enum
from pathlib import Path
import json
from rich.console import Console
import os

app = typer.Typer(help="Generate an HTML viewer for a IIIF Manifest.")
console = Console()

class ViewerType(str, Enum):
    MIRADOR = "mirador"
    # CLOVER = "clover" # Keeping it simple with Mirador for now as it supports inline JSON easily

@app.command()
def main(
    manifest_path: Annotated[str, typer.Argument(help="Path to a local manifest file (JSON) or a URL.")],
    output: Annotated[Path, typer.Option("--output", "-o", help="Output HTML file path.")] = Path("manifest_view.html"),
    viewer: Annotated[ViewerType, typer.Option("--viewer", "-v", help="Viewer to use.")] = ViewerType.MIRADOR,
):
    """
    Generates a self-contained HTML file to view a IIIF manifest.
    
    If a local file path is provided, the manifest content is embedded directly into the HTML,
    allowing it to be opened locally without CORS issues.
    """
    
    manifest_data = None
    manifest_url = None
    
    # Determine if input is URL or File
    if manifest_path.startswith("http://") or manifest_path.startswith("https://"):
        manifest_url = manifest_path
        console.log(f"Using remote manifest URL: {manifest_url}")
    else:
        # Assume local file
        path = Path(manifest_path)
        if not path.exists():
            console.log(f"[bold red]Error:[/bold red] File not found: {manifest_path}")
            raise typer.Exit(code=1)
        
        try:
            with open(path, 'r') as f:
                manifest_data = json.load(f)
            console.log(f"Loaded local manifest: {path}")
        except Exception as e:
            console.log(f"[bold red]Error:[/bold red] Failed to read manifest file: {e}")
            raise typer.Exit(code=1)

    # Generate HTML
    html_content = ""
    
    if viewer == ViewerType.MIRADOR:
        html_content = generate_mirador_html(manifest_url, manifest_data)
    
    # Write Output
    try:
        with open(output, 'w') as f:
            f.write(html_content)
        
        abs_path = output.resolve()
        console.log(f"[green]Success:[/green] Viewer generated at: {abs_path}")
        console.log(f"You can open this file in your browser: file://{abs_path}")
        
    except Exception as e:
        console.log(f"[bold red]Error:[/bold red] Failed to write output file: {e}")
        raise typer.Exit(code=1)


def generate_mirador_html(url: Optional[str], data: Optional[dict]) -> str:
    """
    Generates HTML for Mirador 3.
    """
    
    # Mirador Configuration
    # If we have local data, we inject it into the catalog.
    # If we have a URL, we just point to it.
    
    config_script = ""
    
    if data:
        # Embed the JSON data
        json_str = json.dumps(data)
        config_script = f"""
        var manifestData = {json_str};
        var mirador = Mirador.viewer({{
          "id": "mirador",
          "windows": [
            {{
              "manifestId": "local-manifest",
              "view": "single" 
            }}
          ],
          "catalog": [
            {{
              "manifestId": "local-manifest",
              "manifest": manifestData
            }}
          ],
          "window": {{
            "allowClose": false,
            "allowFullscreen": true,
            "sideBarOpen": true
          }}
        }});
        """
    else:
        # Use URL
        config_script = f"""
        var mirador = Mirador.viewer({{
          "id": "mirador",
          "windows": [
            {{
              "manifestId": "{url}"
            }}
          ],
          "window": {{
            "allowClose": false,
            "allowFullscreen": true
          }}
        }});
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Mirador Viewer - PAA Graph KB</title>
    <style>
        body {{ margin: 0; padding: 0; overflow: hidden; }}
        #mirador {{ position: absolute; top: 0; bottom: 0; left: 0; right: 0; }}
    </style>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500">
    <script src="https://unpkg.com/mirador@latest/dist/mirador.min.js"></script>
</head>
<body>
    <div id="mirador"></div>
    <script type="text/javascript">
        {config_script}
    </script>
</body>
</html>"""
    return html

if __name__ == "__main__":
    app()
