# whatabagacack

Home page https://github.com/clach04/whatabagacack

If you stumbled on this project in relation to Wallabag, don't use this!
Use Wallabag instead. Or perhaps:

  * https://github.com/LordEidi/wombag - Written in Go

Experimental (incomplete) Wallabag API Server that runs under Python 3 and 2.

What a 👜 of 💩.

Remotely similar to https://github.com/clach04/fake-shaarli-server
make something looking like something else, a bridge/gateway/proxy.

Aim to support a subset of the [Wallabag REST API](https://app.wallabag.it/api/doc/) used by:

  * https://github.com/artur-shaik/wallabag-client
      * `python -m pip install wallabag-client`
  * https://github.com/koreader/koreader
      * https://github.com/koreader/koreader/wiki/Wallabag
      * https://github.com/koreader/koreader/tree/master/plugins/wallabag.koplugin
      * https://github.com/clach04/wallabag2.koplugin

So far:

  * Zero authentication support, server accepts any client without any auth check
  * Handles enough for `wallabag list` to work
  * Handles enough for `wallabag export --format epub ID_HERE` to work - either file specified in json "model" or via override OVERRIDE_EPUB_FILENAME os env
  * Handles enough for KoReader Wallabag plugin to list and then download epub entries

## resources

* https://github.com/search?q=repo%3Awallabag%2Fwallabag%20%40route&type=code
* https://app.wallabag.it/api/doc
* https://github.com/wallabag/doc/blob/master/en/developer/api/methods.md **old** still useful and in easy to read form
* https://github.com/wallabag/doc/blob/master/en/developer/api/oauth.md
* https://github.com/Strubbl/wallabago as a nice short list of API endpoints

## What is this good for?

  * For debugging wallabag clients, e.g. KoReader
  * for replacing the Wallabag epub/page-scraper with an alternative one
