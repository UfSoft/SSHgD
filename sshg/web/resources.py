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

if __name__ == '__main__':
    f = ConfigResource("abc")
    f.addUser('foo')
