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
    print('### Debug dumper')
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


WALLABAG_VERSION_STR = "2.6.1"  # TODO make this configurable
entries_config_filename = os.environ.get('WEB_SITE_METADATA_FILENAME', 'entries.json')  # TODO make this configurable
OVERRIDE_EPUB_FILENAME = os.environ.get('OVERRIDE_EPUB_FILENAME')  # i.e. override what ever is in config

if os.path.exists(entries_config_filename):
    f = open(entries_config_filename, 'rb')
    entries_metadata = json.loads(f.read())
    f.close()
else:
    print('default entries')
    entries_metadata = {
        "1": {
            "wallabag_entry": {
                "id": 1,
                "tags": [],
                "url": "http://some.domain.com/some/path.html",
                "title": "Some Title",
                "content": None,
                "is_archived": 0,
                "is_starred": 0
            },
            "epub": "some_title.epub"
        }
    }


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
    print('debug ' + path_info)
    print('debug ' + environ['SERVER_PROTOCOL'])
    print('debug ' + environ['HTTP_HOST'])
    print('debug ' + environ['SERVER_NAME'])
    print('debug ' + environ['SERVER_PORT'])
    print('debug ' + environ['SCRIPT_NAME'])

    if path_info and path_info.startswith('/oauth/v2/token'):
        # don't get if GET, POST, etc.
        # wallabag-client uses GET, KoReader sends a POST
        fake_auth_token = {
            "access_token": "ACCESS_TOKEN_GOES_HERE",
            "expires_in": 3600,  # fake token, claim it expires in 1 hour.. but we won't check...
            "token_type": "bearer",
            "scope": None,
            "refresh_token": "REFRESH_TOKEN_GOES_HERE"
        }
        fake_info_str = json.dumps(fake_auth_token)
    elif 'GET' == request_method:
        # Returns a dictionary in which the values are lists
        get_dict = cgi.parse_qs(environ['QUERY_STRING'])  # FIXME not needed here, defer to later when GET is needed (useless OP when POST/PUT used)

        if path_info and path_info.startswith('/api/info'):
            #server = environ['HTTP_HOST'] or (environ['SERVER_NAME'] + ':' + environ['SERVER_PORT'])
            wallabag_version_dict = {
                "appname": "wallabag",
                "version": WALLABAG_VERSION_STR,
                "allowed_registration": False
            }
            fake_info_str = json.dumps(wallabag_version_dict)
        elif path_info and path_info == '/api/version':  # NOTE this is deprecated BUT KoReader Wallabag plugin uses this
            fake_info_str = '"%s"' % WALLABAG_VERSION_STR
        #elif path_info and path_info.startswith('/api/entries'):
        elif path_info and (path_info == '/api/entries' or path_info == '/api/entries.json'):  # NOTE .json is not documented (maybe old v1 API) and is used by KoReader
            #import pdb ; pdb.set_trace()  # DEBUG
            # only intend to support wallabag-client python app from pypi and KoReader
            # expecting QUERY_STRING dict {'perPage': ['46'], 'detail': ['metadata']}
            # FIXME not yet seen paging api request....
            #if environ['QUERY_STRING'] != 'perPage=46&detail=metadata':  # {'perPage': ['46'], 'detail': ['metadata']}:
            #  'archive=0&page=1&perPage=30'  --  {'perPage': ['30'], 'archive': ['0'], 'page': ['1']}
            """
            if get_dict == {'perPage': [get_dict.get('get_dict')], 'detail': ['metadata']}:
                # Not supported / implemented, dump out information about the request
                tmp_result = debug_dumper(environ, start_response, request_body=None, get_dict=get_dict)
                if tmp_result:
                    return tmp_result
                else:
                    fake_info_str = tmp_result
            """
            # NOTE bare minimum so wallabag-client from pypi will run with "list"
            # TODO 1 - use dict and dump to json (rather than raw string as it is now)
            # TODO 2 - pages of results
            """args to handle:
                'archive':
                'detail': 'metadata' / 'full' - likely never support full?
                'page':
                'perPage':
            """
            wallabag_articles = {
                "_embedded": {
                    "items": [
                    ]
                }
            }
            for entry in entries_metadata:
                wallabag_articles['_embedded']['items'].append(entries_metadata[entry]['wallabag_entry'])
            #print(json.dumps(wallabag_articles, indent=4))  # DEBUG
            fake_info_str = json.dumps(wallabag_articles)
        elif path_info and path_info.startswith('/api/entries') and path_info.endswith('/export.epub'):
            # epub download
            #epub_filename = wallabag_articles['_embedded'][items][id]['epub']  # TODO need id
            #title = wallabag_articles['_embedded'][items][id]['wallabag_entry']['title']  # TODO need id
            title = 'title_goes_here'
            epub_filename = OVERRIDE_EPUB_FILENAME
            if epub_filename:
                f = open(epub_filename, 'rb')
                result = f.read()
                f.close()
            else:
                result = b'epub goes here'
            headers = [
                #('Content-type', 'application/epub+zip')
                ('content-type', 'application/epub+zip'),
                ('content-description', 'File Transfer'),
                ('content-disposition', 'attachment; filename="%s.epub"' % title),  # FIXME escape filename.. or just use the epub filename
                ('content-transfer-encoding', 'binary'),
                ('cache-control', 'no-cache, private')
            ]
            start_response(status, headers)
            return result
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

        if path_info and path_info.startswith('/debugdebug'):
            fake_info_str = '{}'
            #status = '201 OK'
        else:
            # Not supported, dump out information about the request
            tmp_result = debug_dumper(environ, start_response, request_body=request_body, get_dict=None)
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
