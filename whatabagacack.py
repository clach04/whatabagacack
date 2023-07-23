#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
# fake-shaarli-server.py - Fake out Shaarli REST API
# Copyright (C) 2022  Chris Clark
"""WIP - aim is to provide just enough API support to allow wallabag-client and KoReader to run

  * https://github.com/artur-shaik/wallabag-client
  * https://github.com/koreader/koreader


Uses WSGI, see http://docs.python.org/library/wsgiref.html

Python 2 or Python 3
"""

import cgi
import os
try:
    import json
except ImportError:
    json = None
import logging
import mimetypes
from pprint import pprint

import socket
import struct
import sys
from wsgiref.simple_server import make_server


version_tuple = (0, 0, 1)
version = __version__ = '%d.%d.%d' % version_tuple
__author__ = 'clach04'

def force_bool(in_bool):
    """Force string value into a Python boolean value
    Everything is True with the exception of; false, off, and 0"""
    value = str(in_bool).lower()
    if value in ('false', 'off', '0'):
        return False
    else:
        return True

ALWAYS_RETURN_404 = force_bool(os.environ.get('ALWAYS_RETURN_404', True))
DEFAULT_SERVER_PORT = 8000


log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel(level=logging.DEBUG)


def to_bytes(in_str):
    # could choose to only encode for Python 3+
    return in_str.encode('utf-8')

def not_found(environ, start_response):
    """serves 404s."""
    #start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
    #return ['Not Found']
    start_response('404 NOT FOUND', [('Content-Type', 'text/html')])
    return [to_bytes('''<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>404 Not Found</title>
</head><body>
<h1>Not Found</h1>
<p>The requested URL /??????? was not found on this server.</p>
</body></html>''')]


def determine_local_ipaddr():
    local_address = None

    # Most portable (for modern versions of Python)
    if hasattr(socket, 'gethostbyname_ex'):
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
            if not ip.startswith('127.'):
                local_address = ip
                break
    # may be none still (nokia) http://www.skweezer.com/s.aspx/-/pypi~python~org/pypi/netifaces/0~4 http://www.skweezer.com/s.aspx?q=http://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib has alonger one

    if sys.platform.startswith('linux'):
        import fcntl

        def get_ip_address(ifname):
            ifname = ifname.encode('latin1')
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            return socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', ifname[:15])
            )[20:24])

        if not local_address:
            for devname in os.listdir('/sys/class/net/'):
                try:
                    ip = get_ip_address(devname)
                    if not ip.startswith('127.'):
                        local_address = ip
                        break
                except IOError:
                    pass

    # Jython / Java approach
    if not local_address and InetAddress:
        addr = InetAddress.getLocalHost()
        hostname = addr.getHostName()
        for ip_addr in InetAddress.getAllByName(hostname):
            if not ip_addr.isLoopbackAddress():
                local_address = ip_addr.getHostAddress()
                break

    if not local_address:
        # really? Oh well lets connect to a remote socket (Google DNS server)
        # and see what IP we use them
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 53))
        ip = s.getsockname()[0]
        s.close()
        if not ip.startswith('127.'):
            local_address = ip

    return local_address


def debug_dumper(environ, start_response, request_body=None, get_dict=None):
    #print(environ)
    #pprint(environ)
    print('PATH_INFO %r' % environ['PATH_INFO'])
    print('CONTENT_TYPE %r' % environ['CONTENT_TYPE'])
    print('QUERY_STRING %r' % environ['QUERY_STRING'])
    print('QUERY_STRING dict %r' % get_dict)
    print('REQUEST_METHOD %r' % environ['REQUEST_METHOD'])
    #print('environ %r' % environ) # DEBUG, potentially pretty print, but dumping this is non-default
    #print('environ:') # DEBUG, potentially pretty print, but dumping this is non-default
    #pprint(environ, indent=4)
    print('Filtered headers, HTTP*')
    for key in environ:
        if key.startswith('HTTP_'):  # TODO potentially startswith 'wsgi' as well
            # TODO remove leading 'HTTP_'?
            print('http header ' + key + ' = ' + repr(environ[key]))

    print('POST body %r' % request_body)
    if environ['CONTENT_TYPE'] == 'application/json' and json and request_body:
        # 1. Validate the payload - with stacktrace on failure
        # 2. Pretty Print/display the payload
        print('POST json body\n-------------\n%s\n-------------\n' % json.dumps(json.loads(request_body), indent=4))
    #print('environ %r' % environ)
    if ALWAYS_RETURN_404:
        # Disable this to send 200 and empty body
        return not_found(environ, start_response)
    fake_info_str = ''
    return fake_info_str


def wallabag_rest_api_wsgi(environ, start_response):
    """Simple WSGI application that implements bare minimum of
    http://shaarli.github.io/api-documentation/ so that
    https://github.com/dimtion/Shaarlier and
    https://github.com/shaarli/python-shaarli-client completes
    """
    status = '200 OK'
    headers = [('Content-type', 'application/json')]
    result= []

    path_info = environ['PATH_INFO']
    request_method = environ['REQUEST_METHOD']
    # from https://wsgi.readthedocs.io/en/latest/definitions.html
    print('debug ' + environ['SERVER_PROTOCOL'])
    print('debug ' + environ['HTTP_HOST'])
    print('debug ' + environ['SERVER_NAME'])
    print('debug ' + environ['SERVER_PORT'])
    print('debug ' + environ['SCRIPT_NAME'])

    if 'GET' == request_method:
        # Returns a dictionary in which the values are lists
        get_dict = cgi.parse_qs(environ['QUERY_STRING'])  # FIXME not needed here, defer to later when GET is needed (useless OP when POST/PUT used)

        if path_info and path_info.startswith('/api/v1/info'):  ## TODO FIXME version
            # http://shaarli.github.io/api-documentation/#links-instance-information-get
            # python -m shaarli_client.main  get-info
            server = environ['HTTP_HOST'] or (environ['SERVER_NAME'] + ':' + environ['SERVER_PORT'])
            fake_info_str = '{}'  # DEBUG
        elif path_info and path_info.startswith('/oauth/v2/token'):
            # FIXME dict to json rather than string
            fake_info_str = '''
            {
                "access_token":"ACCESS_TOKEN_GOES_HERE",
                "expires_in":3600,
                "token_type":"bearer",
                "scope":null,
                "refresh_token":"REFRESH_TOKEN_GOES_HERE"
            }'''  # fake token, claim it expires in 1 hour.. but we won't check...

        elif path_info and path_info.startswith('/api/entries'):
            #import pdb ; pdb.set_trace()  # DEBUG
            # only intend to support wallabag-client python app from pypi and KoReader
            # expecting QUERY_STRING dict {'perPage': ['46'], 'detail': ['metadata']}
            # FIXME not yet seen paging api request....
            #if environ['QUERY_STRING'] != 'perPage=46&detail=metadata':  # {'perPage': ['46'], 'detail': ['metadata']}:
            if get_dict == {'perPage': [get_dict.get('get_dict')], 'detail': ['metadata']}:
                # Not supported / implemented, dump out information about the request
                tmp_result = debug_dumper(environ, start_response, request_body=None, get_dict=get_dict)
                if tmp_result:
                    return tmp_result
                else:
                    fake_info_str = tmp_result
            else:
                # NOTE bare minimum so wallabag-client from pypi will run with "list"
                # TODO 1 - use dict and dump to json (rather than raw string as it is now)
                # TODO 2 - pages of results
                fake_info_str = """
    {
        "_embedded": {
            "items": [
                {
                    "id": 1, 
                    "tags": [], 
                    "url": "http://some.domain.com/some/path.html", 
                    "title": "Some Title",
                    "content": null,
                    "is_archived": 0,
                    "is_starred": 0
                }
            ]
        }
    }
"""
        else:
            # Not supported / implemented, dump out information about the request
            tmp_result = debug_dumper(environ, start_response, request_body=None, get_dict=get_dict)
            if tmp_result:
                return tmp_result
            else:
                fake_info_str = tmp_result
    else:
        # Assume PUT or POST

        # the environment variable CONTENT_LENGTH may be empty or missing
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0
        # Read POST body
        request_body = environ['wsgi.input'].read(request_body_size)
        link_payload_dict = json.loads(request_body)
        print('%r with payload %r' % (request_method, link_payload_dict))

        if path_info and path_info.startswith('/api/v1/links/'):
            fake_info_str = '{}'  # DEBUG
            #status = '201 OK'
        else:
            # Not supported, dump out information about the request
            tmp_result = debug_dumper(environ, start_response, request_body=request_body, get_dict=get_dict)
            if tmp_result:
                return tmp_result
            else:
                fake_info_str = tmp_result

    result.append(to_bytes(fake_info_str))

    start_response(status, headers)
    return result


def main(argv=None):
    print('Python %s on %s' % (sys.version, sys.platform))
    server_port = int(os.environ.get('PORT', DEFAULT_SERVER_PORT))

    httpd = make_server('', server_port, wallabag_rest_api_wsgi)
    print("Serving on port %d..." % server_port)
    print("ALWAYS_RETURN_404 = %r" % ALWAYS_RETURN_404)
    local_ip = determine_local_ipaddr()
    log.info('Starting server: %r', (local_ip, server_port))
    httpd.serve_forever()

if __name__ == "__main__":
    sys.exit(main())
