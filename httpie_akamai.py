"""
Akamai utility plugins for Httpie. Colorize Akamai headers and modify request headers.
"""
import os
import re
from requests.adapters import HTTPAdapter

try:
    from urllib.parse import urlsplit, urlunsplit
except ImportError:
    from urlparse import urlsplit, urlunsplit

from httpie.plugins import TransportPlugin, FormatterPlugin

__version__ = '0.1.5'
__author__ = 'Matt Eckhaus'
__licence__ = 'BSD'

# Unsafely import the default plugin ColorFormatter so we can re-apply it with Akamai highlighting
import httpie.plugins
colors_module = os.path.dirname(os.path.dirname(httpie.plugins.__file__)) + '/output/formatters/colors.py'
exec(open(colors_module).read())

class AkamaiFormatterPlugin(ColorFormatter):

    """
    If Akamai headers are present, strip out the ANSI highlighting applied by the default ColorFormatter
    plugin and re-apply it with some additional highlighting for Akamai headers.
    """

    name = 'Akamai formatter'
    description = 'Syntax highlighting for Akamai response headers'

    def format_headers(self, headers):
        if headers.lower().find('x-akamai-request-id') >= 0:
            headers = re.sub('\x1b\[[0-9;]*m', '', headers)
            return pygments.highlight(headers, AkamaiFormatterPlugin.AkamaiHTTPLexer(), self.formatter).strip()
        else:
            return headers

    def format_body(self, content, mime):
        """
        This plugin doesn't modify the content
        """
        return content

    class AkamaiHTTPLexer(HTTPLexer):
        """Enhanced version of default HTTPie HTTPLexer, with additional patterns for Akamai-specific headers
        """

        name = 'AkamaiHTTP'
        aliases = ['akamaihttp']
        filenames = ['*.http']
        tokens = {
            'root' : [
                # Akamai Cache Key
                (r'(X-Cache-Key)( *)(:)( *)([L/\d]+/)(\d+[smhd])(/.+)', pygments.lexer.bygroups(
                    pygments.token.String.Escape,  # Name
                    pygments.token.Text,
                    pygments.token.Operator,  # Colon
                    pygments.token.Text,
                    pygments.token.String,  # Value
                    pygments.token.Keyword.Reserved, # Akamai TTL
                    pygments.token.String  # Value
                )),
                # Cacheability Header
                (r'(X-Check-Cacheable)( *)(:)( *)(YES|NO)', pygments.lexer.bygroups(
                    pygments.token.String.Escape,  # Name
                    pygments.token.Text,
                    pygments.token.Operator,  # Colon
                    pygments.token.Text,
                    pygments.token.Keyword.Reserved  # Value "YES" or "NO"
                )),
                # Hit or miss
                (r'(X-Cache)( *)(:)( *)(\w*HIT\w*|\w*MISS\w*)( ?.*)', pygments.lexer.bygroups(
                    pygments.token.String.Escape,  # Name
                    pygments.token.Text,
                    pygments.token.Operator,  # Colon
                    pygments.token.Text,
                    pygments.token.Keyword.Reserved,  # Value HIT or MISS
                    pygments.token.String
                )),
                # Extracted values
                (r'(X-Akamai-Session-Info)( *)(:)( *)(name=)(\w*)(;)( *)(value=)(.*)', pygments.lexer.bygroups(
                    pygments.token.String.Escape,  # Name
                    pygments.token.Text,
                    pygments.token.Operator,  # Colon
                    pygments.token.Text,
                    pygments.token.Name.Function,  # name
                    pygments.token.String,
                    pygments.token.Operator, # semi colon
                    pygments.token.Text,
                    pygments.token.Name.Function, # value
                    pygments.token.String
                )),
                # Akamai Header
                (r'((?:X-Akamai|X-Cache|X-Check|X-Serial|X-True-Cache).*?)( *)(:)( *)(.+)', pygments.lexer.bygroups(
                    pygments.token.String.Escape,  # Name
                    pygments.token.Text,
                    pygments.token.Operator,  # Colon
                    pygments.token.Text,
                    pygments.token.String  # Value
                ))
            ] + HTTPLexer.tokens['root']
        }

class AkamaiHTTPAdapter(HTTPAdapter):

    """
    If the mock "ak-" transport is used this plugin will add the Akamai debugging headers to the request.
    If "akp-" or "aks-" is used it will force the request to the Akamai production or staging network
    respectively. For this to work the target name has to be the same as the edge hostname.
    """


    original_hostname = None
    modified_hostname = None

    def get_connection(self, url, proxies=None):
        (scheme, netloc, path, query, fragment) = urlsplit(url)
        self.original_hostname = netloc
        if scheme == 'aks-http':
            netloc += '.edgesuite-staging.net'
            scheme = 'http'
        elif scheme == 'akp-http':
            netloc += '.edgesuite.net'
            scheme = 'http'
        elif scheme == 'aks-https':
            netloc += '.edgekey-staging.net'
            scheme = 'https'
        elif scheme == 'akp-https':
            netloc += '.edgekey.net'
            scheme = 'https'
        elif scheme == 'ak-http':
            scheme = 'http'
        elif scheme == 'ak-https':
            scheme = 'https'
        else:
            raise Exception("Invalid Akamai schema %s" % scheme)
        self.modified_hostname = netloc
        url = urlunsplit((scheme, netloc, path, query, fragment))
        return super(AkamaiHTTPAdapter, self).get_connection(url, proxies)

    def add_headers(self, request, **kwargs):
        akamai_headers = "akamai-x-cache-on,akamai-x-cache-remote-on,akamai-x-check-cacheable,akamai-x-get-cache-key,akamai-x-get-nonces,akamai-x-get-request-id,akamai-x-get-true-cache-key,akamai-x-serial-no,akamai-x-get-ssl-client-session-id,akamai-x-get-client-ip"
        # Others you may like to use: akamai-x-feo-trace,akamai-get-extracted-values
        if self.original_hostname != self.modified_hostname:
            request.headers['Host'] = self.original_hostname
            request.headers['X-httpie-host'] = self.modified_hostname
        if 'Pragma' in request.headers:
            request.headers['Pragma'] += ',' + akamai_headers
        else:
            request.headers['Pragma'] = akamai_headers

class AkamaiTransportPlugin(TransportPlugin):

    name = 'Akamai headers & host rewrite'
    prefix = 'ak'

    def get_adapter(self):
        return AkamaiHTTPAdapter()
