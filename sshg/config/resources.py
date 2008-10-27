# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

from sshg.db import model

class ConfigResource(object):
    def __init__(self, store):
        self.store = store

    def addUser(self, username):
        user = model.User.create(username, store=self.store)
        return user

    def getUser(self, username):
        return model.User(username=username, store=self.store)

    def delUser(self, username):
        pass

    def addPubKey(self, username, pubkey):
        username = unicode(username)
        pubkey = unicode(pubkey)
        user = None
        for item in self.store.query(model.User, model.User.username==username):
            user = item
            break
        print "user", user
        if not user:
            return "No such user"
        try:
            user.addPubKey(pubkey)
            return "OK"
        except Exception, err:
            raise err
            return "Something failed %s" % err

    def getPubKeys(self, username):
        username = unicode(username)
        user = None
        for item in self.store.query(model.User, model.User.username==username):
            user = item
            break
        if user:
            return user.keys
        else:
            return "No Such User"
        return []

if __name__ == '__main__':
    f = ConfigResource("abc")
    f.addUser('foo')
