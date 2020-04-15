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
    # Construct the template path.
    _, batch_dir_subpaths = settings.BATCH_DIR_STRUCTURE
    _, definition_dir_subpaths = \
        batch_dir_subpaths['definition']
    template_file_name, _ = definition_dir_subpaths['question_template']

    template_path = os.path.join(definition_dir, template_file_name)

    # Instantiate the HIT preview server.
    httpd = Server(
        server_address=('', port),
        request_handler_class=Handler,
        template_path=template_path,
        data_path=data_path)

    # Run the server.
    logger.info(
        f'\n'
        f'\n    Running HIT preview server on port {port}.'
        f'\n')

    httpd.serve_forever()
