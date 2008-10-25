# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

from twisted.web import xmlrpc

from sshg.web import resources

class RPCResource(xmlrpc.XMLRPC):

    def __init__(self, store, allowNone=False):
        xmlrpc.XMLRPC.__init__(self, allowNone=allowNone)
        self.resource = resources.ConfigResource(store)

    def xmlrpc_getUser(self, username):
        return self.resource.getUser(username)

    def xmlrpc_addUser(self, username):
        return self.resource.addUser(username).username

    def xmlrpc_foo(self, arg):
        print arg
        return "FOOOOO " + arg
