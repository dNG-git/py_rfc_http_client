# -*- coding: utf-8 -*-

"""
RFC compliant and simple HTTP client
An abstracted programming interface for an HTTP client
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?py;rfc_http_client

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;mpl2
----------------------------------------------------------------------------
#echo(rfcHttpClientVersion)#
#echo(__FILEPATH__)#
"""

# pylint: disable=import-error,invalid-name,no-name-in-module

import ssl

try:
    import http.client as http_client
    from urllib.parse import quote_plus, urlencode, urlsplit
except ImportError:
    import httplib as http_client
    from urllib import quote_plus, urlencode
    from urlparse import urlsplit
#

from .abstract_raw_client import AbstractRawClient

try:
    _PY_BYTES = unicode.encode
    _PY_BYTES_DECL = str
    _PY_BYTES_TYPE = str
    _PY_STR = unicode.encode
    _PY_UNICODE = str.decode
    _PY_UNICODE_TYPE = unicode
except NameError:
    _PY_BYTES = str.encode
    _PY_BYTES_DECL = lambda x: bytes(x, "raw_unicode_escape")
    _PY_BYTES_TYPE = bytes
    _PY_STR = bytes.decode
    _PY_UNICODE = bytes.decode
    _PY_UNICODE_TYPE = str
#

class RawClient(AbstractRawClient):
    """
Minimal HTTP client abstraction layer returning raw HTTP responses.

:author:    direct Netware Group
:copyright: (C) direct Netware Group - All rights reserved
:package:   rfc_http_client.py
:since:     v0.1.1
:license:   https://www.direct-netware.de/redirect?licenses;mpl2
            Mozilla Public License, v. 2.0
    """

    def __init__(self, url, timeout = 30, return_reader = False, log_handler = None):
        """
Constructor __init__(RawClient)

:param url: URL to be called
:param timeout: Socket timeout in seconds
:param return_reader: Returns a body reader instead of reading the response
                      if true.
:param log_handler: Log handler to use

:since: v0.1.1
        """

        # global: _PY_STR, _PY_UNICODE_TYPE

        self.pem_cert_file_name = None
        """
Path and file name of the PEM-encoded certificate file
        """
        self.pem_key_file_name = None
        """
Path and file name of the private key
        """

        AbstractRawClient.__init__(self, url, timeout, return_reader, log_handler)
    #

    @AbstractRawClient.url.getter
    def url(self):
        """
Returns the URL used for all subsequent requests.

:return: (str) URL to be called
:since:  v1.0.0
        """

        _return = "{0}://".format(self.scheme)

        if (self.auth_username is not None or self.auth_password is not None):
            if (self.auth_username is not None): _return += quote_plus(self.auth_username)
            _return += ":"
            if (self.auth_password is not None): _return += quote_plus(self.auth_password)
            _return += "@"
        #

        _return += self.host

        if ((self.scheme != "https" or self.port != http_client.HTTPS_PORT)
                and (self.scheme != "http" or self.port != http_client.HTTP_PORT)
        ): _return += ":{0:d}".format(self.port)

        _return += self.path

        return _return
    #

    def _configure(self, url):
        """
Configures the HTTP connection parameters for later use.

:param url: URL to be called

:since: v0.1.1
        """

        url_elements = urlsplit(url)
        self.scheme = url_elements.scheme.lower()

        if (url_elements.hostname is None): raise TypeError("URL given is invalid")

        self.auth_username = (None if (url_elements.username is None) else url_elements.username)
        self.auth_password = (None if (url_elements.password is None) else url_elements.password)

        self.host = ("[{0}]".format(url_elements.hostname) if (":" in url_elements.hostname) else url_elements.hostname)

        if (url_elements.port is not None): self.port = url_elements.port
        elif (self.scheme == "https"): self.port = http_client.HTTPS_PORT
        else: self.port = http_client.HTTP_PORT

        self.path = url_elements.path
        if (url_elements.query != ""): self.path = "{0}?{1}".format(self.path, url_elements.query)
    #

    def _get_connection(self):
        """
Returns a connection to the HTTP server.

:return: (mixed) Response data; Exception on error
:since:  v0.1.1
        """

        # pylint: disable=star-args

        if (self.connection is None):
            if (":" in self.host):
                host = self.host[1:-1]
                if (host[:6] == "fe80::" and self.ipv6_link_local_interface is not None): host = "{0}%{1}".format(self.host[1:-1], self.ipv6_link_local_interface)
            else: host = self.host

            if (self.scheme == "https"):
                kwargs = self._get_ssl_connection_arguments()

                try: self.connection = http_client.HTTPSConnection(host, self.port, timeout = self.timeout, **kwargs)
                except TypeError: self.connection = http_client.HTTPSConnection(host, self.port, **kwargs)
            else:
                try: self.connection = http_client.HTTPConnection(host, self.port, timeout = self.timeout)
                except TypeError: self.connection = http_client.HTTPConnection(host, self.port)
            #
        #

        return self.connection
    #

    def _get_ssl_connection_arguments(self):
        """
Returns arguments to be used for creating an SSL connection.

:return: (dict) SSL connection arguments
:since:  v0.1.1
        """

        _return = { }

        if (hasattr(ssl, "create_default_context")):
            ssl_context = ssl.create_default_context()

            if (self.pem_cert_file_name is not None):
                if (self.pem_key_file_name): ssl_context.load_cert_chain(self.pem_cert_file_name, self.pem_key_file_name)
                else: ssl_context.load_cert_chain(self.pem_cert_file_name)
            #

            _return['context'] = ssl_context
        elif (self.pem_cert_file_name is not None):
            if (self.pem_key_file_name): _return['key_file'] = self.pem_key_file_name
            _return['cert_file'] = self.pem_cert_file_name
        #

        return _return
    #

    def _request(self, method, **kwargs):
        """
Sends the request to the connected HTTP server and returns the result.

:param method: HTTP method

:return: (dict) Response data; 'body' may contain the catched Exception
:since:  v0.1.1
        """

        # pylint: disable=star-args

        connection = self._get_connection()
        connection.request(method, **kwargs)
        response = connection.getresponse()

        _return = { "code": response.status, "headers": { }, "body": None }
        for header in response.getheaders(): _return['headers'][header[0].lower().replace("-", "_")] = header[1]

        if (self.return_reader): _return['body_reader'] = response.read

        if (response.status < 100 or response.status >= 400):
            _return['body'] = http_client.HTTPException("{0} {1}".format(str(response.status), str(response.reason)), response.status)
            if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -RawClient._request()- reporting: {0:d} for '{1}'".format(response.status, response.read()))
        elif (method != "HEAD" and (not self.return_reader)): _return['body'] = response.read()

        return _return
    #

    def request_delete(self, params = None, separator = ";", data = None):
        """
Do a DELETE request on the connected HTTP server.

:param params: Query parameters as dict
:param separator: Query parameter separator
:param data: HTTP body

:return: (mixed) Response data; Exception on error
:since:  v0.1.1
        """

        params = self._build_request_parameters(params, separator)
        return self.request("DELETE", separator, params, data)
    #

    def request_get(self, params = None, separator = ";"):
        """
Do a GET request on the connected HTTP server.

:param params: Query parameters as dict
:param separator: Query parameter separator

:return: (mixed) Response data; Exception on error
:since:  v0.1.1
        """

        params = self._build_request_parameters(params, separator)
        return self.request("GET", separator, params)
    #

    def request_head(self, params = None, separator = ";"):
        """
Do a HEAD request on the connected HTTP server.

:param params: Query parameters as dict
:param separator: Query parameter separator

:return: (mixed) Response data; Exception on error
:since:  v0.1.1
        """

        params = self._build_request_parameters(params, separator)
        return self.request("HEAD", separator, params)
    #

    def request_patch(self, data = None, params = None, separator = ";"):
        """
Do a PATCH request on the connected HTTP server.

:param data: HTTP body
:param params: Query parameters as dict
:param separator: Query parameter separator

:return: (mixed) Response data; Exception on error
:since:  v0.1.1
        """

        params = self._build_request_parameters(params, separator)
        return self.request("PATCH", separator, params, data)
    #

    def request_post(self, data = None, params = None, separator = ";"):
        """
Do a POST request on the connected HTTP server.

:param data: HTTP body
:param params: Query parameters as dict
:param separator: Query parameter separator

:return: (mixed) Response data; Exception on error
:since:  v0.1.1
        """

        params = self._build_request_parameters(params, separator)
        return self.request("POST", separator, params, data)
    #

    def request_put(self, data = None, params = None, separator = ";"):
        """
Do a PUT request on the connected HTTP server.

:param data: HTTP body
:param params: Query parameters as dict
:param separator: Query parameter separator

:return: (mixed) Response data; Exception on error
:since:  v0.1.1
        """

        params = self._build_request_parameters(params, separator)
        return self.request("PUT", separator, params, data)
    #

    def request_options(self, params = None, separator = ";", data = None):
        """
Do a OPTIONS request on the connected HTTP server.

:param params: Query parameters as dict
:param separator: Query parameter separator
:param data: HTTP body

:return: (mixed) Response data; Exception on error
:since:  v0.1.1
        """

        params = self._build_request_parameters(params, separator)
        return self.request("OPTIONS", separator, params, data)
    #

    def request_trace(self, params = None, separator = ";"):
        """
Do a TRACE request on the connected HTTP server.

:param params: Query parameters as dict
:param separator: Query parameter separator

:return: (mixed) Response data; Exception on error
:since:  v0.1.1
        """

        params = self._build_request_parameters(params, separator)
        return self.request("TRACE", separator, params)
    #

    def set_pem_cert_file(self, cert_file_name, key_file_name = None):
        """
Sets a PEM-encoded certificate file name to be used. "key_file_name" is used
if the private key is not part of the certificate file.

:param cert_file_name: Path and file name of the PEM-encoded certificate file
:param key_file_name: Path and file name of the private key

:since: v0.1.1
        """

        self.pem_cert_file_name = cert_file_name
        self.pem_key_file_name = key_file_name
    #
#
