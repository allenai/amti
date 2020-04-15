"""CLI for running a web server to preview HITs"""

import html
from http import server
import json
import logging
import os
import re
from xml.etree import ElementTree

import click
import jinja2

from amti import settings


logger = logging.getLogger(__name__)


class Server(server.HTTPServer):
    """A server for previewing HTMLQuestion HITs."""

    def __init__(
        self,
        server_address,
        request_handler_class,
        template_path,
        data_path,
    ):
        super().__init__(server_address, request_handler_class)

        self.template_path = template_path
        self.data_path = data_path

        with open(self.template_path, 'r') as template_file:
            template_xml = ElementTree.fromstring(template_file.read())
            html_content = template_xml.find(
                'mturk:HTMLContent',
                {'mturk': 'http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2011-11-11/HTMLQuestion.xsd'}
            )
            if html_content is None:
                raise ValueError(
                    'The preview server can only preview HTMLQuestion HITs.')

            html_template_string = html_content.text

            self.template = jinja2.Template(html_template_string)

        with open(self.data_path, 'r') as data_file:
            self.data = [json.loads(ln) for ln in data_file]

            if len(self.data) == 0:
                raise ValueError('The data file cannot be empty.')


class Handler(server.BaseHTTPRequestHandler):
    """A request handler for rendering HTMLQuestion HITs."""

    URL_PATTERN = re.compile(r'^/hits/(?P<hit_idx>\d+)/$')

    def _render_error_page(self, status, error, message):
        status = str(int(status))
        error = html.escape(error)
        message = html.escape(message)

        return (
            f'<!DOCTYPE html>\n'
            f'<html>\n'
            f'  <head>\n'
            f'    <meta charset="utf-8">\n'
            f'    <title>HIT Preview Server Error: {status}</title>\n'
            f'  </head>\n'
            f'  <body>\n'
            f'    <h1>({status}) {error}</h1>\n'
            f'    <p>{message}</p>\n'
            f'  </body>\n'
            f'</html>\n'
        )

    def _create_response(self, path):
        match = self.URL_PATTERN.match(self.path)
        if match is None:
            return (
                self._render_error_page(
                    status=404,
                    error='Page not found: bad URL',
                    message='The URL should look like: /hits/${HIT_IDX}/.'),
                404
            )

        hit_idx = int(match.groupdict()['hit_idx'])
        template = self.server.template
        data = self.server.data

        # Check that the HIT index is in range.
        if hit_idx < 0 or hit_idx >= len(data):
            return (
                self._render_error_page(
                    status=404,
                    error='Page not found: HIT index out of range',
                    message='The HIT index from the URL was out of range. The'
                            ' index must be an integer between 0 and'
                           f' {len(data) - 1}, inclusive.'),
                404
            )

        return template.render(**data[hit_idx]), 200

    def do_GET(self):
        body, status = self._create_response(path=self.path)

        # Set the headers.
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Write out the message body.
        self.wfile.write(body.encode())


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
    '--port', type=int, default=8000,
    help='The port on which to run the server. Defaults to 8000.')
def preview_batch(definition_dir, data_path, port):
    """Preview HTMLQuestion HITs based on DEFINITION_DIR and DATA_PATH.

    Run a web server that previews the HITs defined by DEFINITION_DIR
    and DATA_PATH. The HIT corresponding to each row of the data file
    can be previewed by navigating to
    http://127.0.0.1:$PORT/hits/${HIT_IDX}/ where $HIT_IDX is the row's
    index (starting from zero).
    """
    # Construct the template path.
    _, batch_dir_subpaths = settings.BATCH_DIR_STRUCTURE
    _, definition_dir_subpaths = \
        batch_dir_subpaths['definition']
    template_file_name, _ = definition_dir_subpaths['question_template']

    template_path = os.path.join(definition_dir, template_file_name)

    # Instantiate the HIT preview server.
    httpd = Server(
        server_address=('127.0.0.1', port),
        request_handler_class=Handler,
        template_path=template_path,
        data_path=data_path)

    # Run the server.
    logger.info(
        f'\n'
        f'\n    Running the HIT preview server at http://127.0.0.1:{port}/.'
        f'\n'
        f'\n    Navigate to http://127.0.0.1:{port}/hits/0/ to view the first HIT.'
        f'\n')

    httpd.serve_forever()
