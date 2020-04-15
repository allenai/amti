"""CLI for running a web server to preview HITs"""

from http import server
import json
import logging
import os
from urllib.parse import urlparse

import click
import jinja2

from amti import settings


logger = logging.getLogger(__name__)


class Server(server.HTTPServer):
    def __init__(
        self,
        server_address,
        request_handler_class,
        template_path=None,
        data_path=None,
    ):
        super().__init__(server_address, request_handler_class)

        self.template_path = template_path
        self.data_path = data_path


class Handler(server.BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self): # handle GET request
        self._set_headers()

        # Get data index from query (optional)
        query = urlparse(self.path).query
        try:
            query_components = dict(qc.split("=") for qc in query.split("&"))
        except ValueError:
            query_components = {}
        index = int(query_components.get('id', '0'))

        # Render
        with open(self.server.template_path, 'r') as template_file:
            question_template = jinja2.Template(template_file.read())
        with open(self.server.data_path, 'r') as data_file:
            ln_data = {}
            for i, f in enumerate(data_file):
                if i == index:
                    ln_data = json.loads(f)
                    break
        self.wfile.write(question_template.render(**ln_data).encode())

def run(
    template_path,
    data_path,
    port,
    server_class=Server,
    handler_class=Handler,
):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class, template_path=template_path, data_path=data_path)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()


@click.command(
    context_settings={
        'help_option_names': ['--help', '-h']
    })
@click.argument(
    'definition_dir',
    type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument(
    'data_path',
    type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option(
    '--port',
    type=click.INT,
    default=8000,
    help='Choose a custom port'
    )
def preview_batch(definition_dir, data_path, port):
    """Preview a batch of rendered HITs using DEFINITION_DIR and DATA_PATH.

    Run a local web server to allow for previewing hits.
    By default, runs at <http://localhost:8000/>.

    You can preview row i by appending `?id=[i]`.
    For example, for row 2, visit <http://localhost:8000/?id=2>.

    """
    run(
        template_path=os.path.join(definition_dir, 'question.xml.j2'),
        data_path=data_path,
        port=port,
    )
