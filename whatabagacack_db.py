import json
import logging
import os
import sqlite3
import sys


log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel(level=logging.DEBUG)


class UrlDb:
    def __del__(self):
        self._disconnect()
    def __init__(self, database_name, autocommit=True, autoconnect=False):
        """autocommit is really  pseudo autocommit, and handled in the application NOT the database (driver)
        autoconnect - if true, connect and disconnect for each operation
        """
        self.database_name = database_name
        self._db = None
        self.autocommit = autocommit or False  # implemented in this class, not using/relying on database autocommit
        self.autoconnect = autoconnect or False

    def _disconnect(self, commit=False):
        """Ignores autocommit, assumes autocommit was issued previously
        """
        db = self._db
        if db:
            if commit:
                db.commit()
            else:
                db.rollback()  # explictly, not really needed but here as just-in-case
            db.close()
            self._db = None

    def _connect(self):
        self._db = db = sqlite3.connect(self.database_name)
        c = db.cursor()
        # TODO move this?
        c.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            rowid INTEGER PRIMARY KEY ASC,
            url TEXT UNIQUE NOT NULL,
            is_archived INT NOT NULL,  /* Wallabag is_archived metadata */

            epub TEXT NULLABLE,  /* epub filename, if NULL, not scraped. Consider making UNIQUE It should be unique, but does this need to be enforced in the database (with index overhead)? */
            wallabag_entry TEXT  /* TODO dociment min-schema - (bare minimum) wallabag json metadata to allow KoReader to work. If NULL, not scraped */
        )
        ''')
        if self.autocommit:
            db.commit()

    def auto_connect(self):
        if self.autoconnect and self._db is None:
            self._disconnect()

    def auto_disconnect(self):
        if self.autoconnect and self._db:
            self._connect()

    def commit(self):
        db = self._db
        if self._db:
            db.commit()
        else:
            raise NotImplmentedError('no database connection')

    def rollback(self):
        db = self._db
        if self._db:
            db.rollback()
        else:
            raise NotImplmentedError('no database connection')

    def url_add(self, url):
        """Add to url into database
        Returns unique id (integer, basically sqlite3 rowid)
        """
        self.auto_connect()
        db = self._db
        c = db.cursor()
        result = None
        # check first and abort
        if not self.url_check(url, autocommit=False):
            bind_params = (url, 0)
            log.debug('bind_params %r', bind_params)
            c.execute('insert into entries (url, is_archived) values (?, ?)', bind_params)
            result = c.lastrowid
        if self.autocommit:
            db.commit()
        self.auto_disconnect()
        return result

    def url_check(self, url, autocommit=None):
        """Return True if url already in database
        """
        if autocommit is None:
            autocommit = self.autocommit
        self.auto_connect()
        db = self._db
        c = db.cursor()
        bind_params = (url,)
        c.execute('SELECT rowid FROM entries WHERE url = ?', bind_params)  # TODO COUNT(*) instead?
        rows = c.fetchall()
        if autocommit:
            db.commit()
        self.auto_disconnect()
        if rows:
            return True
        else:
            return False

