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

class Response(object):
    """
HTTP response object handling chunked transfer-encoded data transparently.

:author:    direct Netware Group
:copyright: (C) direct Netware Group - All rights reserved
:package:   rfc_http_client.py
:since:     v0.1.01
:license:   https://www.direct-netware.de/redirect?licenses;mpl2
            Mozilla Public License, v. 2.0
    """

    def __init__(self):
        """
Constructor __init__(Response)

:since: v0.1.01
        """

        self.body_reader = None
        """
Body reader callable
        """
        self.code = None
        """
HTTP status code
        """
        self.exception = None
        """
Exception occurred while receiving an response.
        """
        self.headers = { }
        """
Response headers
        """
    #

    def get_code(self):
        """
Returns the HTTP status code for the request.

:return: (int) HTTP status code; None otherwise
:since:  v0.1.01
        """

        return self.code
    #

    def get_error_message(self):
        """
Returns the error message based on the exception that occurred while
processing the request.

:return: (str) Error message; None otherwise
:since:  v0.1.01
        """

        return (None if (self.exception is None) else str(self.exception))
    #

    def get_exception(self):
        """
Returns the exception that occurred while processing the request.

:return: (object) Exception instance; None otherwise
:since:  v0.1.01
        """

        return self.exception
    #

    def get_header(self, name):
        """
Returns the response header if defined.

:param name: Header name

:return: (str) Header value if set; None otherwise
:since:  v0.1.01
        """

        name = name.lower().replace("-", "_")
        return self.headers.get(name)
    #

    def get_headers(self):
        """
Returns the response headers.

:return: (dict) Dictionary of headers
:since:  v0.1.03
        """

        return self.headers
    #

    def is_readable(self):
        """
Returns true if the body reader is ready to receive the response and no
exception occurred while processing the request.

:return: (bool) True if ready
:since:  v0.1.01
        """

        return (self.body_reader is not None and self.exception is None)
    #

    def read(self, n = 0):
        """
Reads data using the given body reader. Chunked transfer-encoded data is
handled automatically.

:param n: How many bytes to read from the current position (0 means until
          EOF)

:return: (bytes) Data; None if EOF
        """

        return (self.body_reader() if (n < 1) else self.body_reader(n))
    #

    def _set_body_reader(self, body_reader):
        """
Sets the body reader callable of this response object.

:param body_reader: Body reader callable

:since: v0.1.01
        """

        self.body_reader = body_reader
    #

    def _set_code(self, code):
        """
Sets the HTTP status code for the request.

:param code: HTTP status code; None otherwise

:since: v0.1.01
        """

        self.code = code
    #

    def _set_exception(self, exception):
        """
Sets the exception occurred while processing the request.

:param exception: Exception object

:since: v0.1.01
        """

        self.exception = exception
    #

    def _set_headers(self, headers):
        """
Sets the headers of the response.

:param headers: HTTP response headers

:since: v0.1.01
        """

        if (headers is not None): self.headers = headers
    #
#
