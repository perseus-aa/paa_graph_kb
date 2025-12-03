import typer
from typing import Annotated, Optional
from enum import Enum
from pathlib import Path
import json
from rich.console import Console
import os
import http.server
import socketserver
import webbrowser
import socket

app = typer.Typer(help="Generate an HTML viewer for a IIIF Manifest.")
console = Console()

class ViewerType(str, Enum):
    MIRADOR = "mirador"

@app.command()
def main(
    manifest_path: Annotated[str, typer.Argument(help="Path to a local manifest file (JSON) or a URL.")],
    output: Annotated[Path, typer.Option("--output", "-o", help="Output HTML file path.")] = Path("manifest_view.html"),
    viewer: Annotated[ViewerType, typer.Option("--viewer", "-v", help="Viewer to use.")] = ViewerType.MIRADOR,
    serve: Annotated[bool, typer.Option("--serve", "-s", help="Start a local web server and open in browser.")] = False,
    port: Annotated[int, typer.Option("--port", "-p", help="Port for local web server.")] = 8000,
):
    """
    Generates a self-contained HTML file to view a IIIF manifest.
    
    If a local file path is provided, the manifest content is embedded directly into the HTML.
    Use --serve to bypass browser security restrictions on local files.
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
        
        if serve:
            serve_and_open(abs_path, port)
        else:
            console.log(f"You can open this file in your browser: file://{abs_path}")
            console.log("[yellow]Note:[/yellow] If images fail to load, try running with --serve")
        
    except Exception as e:
        console.log(f"[bold red]Error:[/bold red] Failed to write output file: {e}")
        raise typer.Exit(code=1)


def serve_and_open(file_path: Path, port: int):
    """Starts a local server and opens the file."""
    # Change to the directory containing the file
    directory = file_path.parent
    filename = file_path.name
    os.chdir(directory)
    
    # Find a free port if the default is taken
    while is_port_in_use(port):
        console.log(f"[yellow]Port {port} is in use, trying {port + 1}...[/yellow]")
        port += 1

    url = f"http://localhost:{port}/{filename}"
    
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass # Suppress request logging to keep console clean

    console.log(f"[green]Starting local server at {url}[/green]")
    console.log("Press Ctrl+C to stop.")
    
    # Open browser shortly after server start
    webbrowser.open(url)
    
    try:
        with socketserver.TCPServer(("", port), QuietHandler) as httpd:
            httpd.allow_reuse_address = True
            httpd.serve_forever()
    except KeyboardInterrupt:
        console.log("\nStopping server.")


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def generate_mirador_html(url: Optional[str], data: Optional[dict]) -> str:
    """
    Generates HTML for Mirador 3.
    """
    
    if data:
        # Embed the JSON data safely using a hidden script tag
        # This avoids python string formatting issues with the JSON content
        json_str = json.dumps(data)
        
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
    
    <!-- Embed Manifest Data Safely -->
    <script id="manifest-data" type="application/json">
        {json_str}
    </script>

    <script type="text/javascript">
        // Read the JSON data from the script tag
        var manifestData = JSON.parse(document.getElementById('manifest-data').textContent);
        
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
            "sideBarOpen": true,
            "defaultSideBarPanel": 'info'
          }},
          "workspace": {{
            "showZoomControls": true
          }}
        }});
    </script>
</body>
</html>"""
    else:
        # Use URL
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
    </script>
</body>
</html>"""

    return html

if __name__ == "__main__":
    app()
