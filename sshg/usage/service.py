# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

import os
from ConfigParser import SafeConfigParser

from sshg import __package__, __summary__
from sshg.usage import certs, config, server
from sshg.usage.base import BaseOptions

from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.python import util, reflect
from zope.interface import implements

from axiom.store import Store

class SSHgDOptions(BaseOptions):
    optParameters = [
        ["config", "C", None, "Configuration file"],
        ["storage", "S", "./storage", "Storage Directory"]
    ]
    subCommands = [
        ["server", None, server.MercurialServerOptions,
         "Mercurial SSH service"],
        ["config", None, config.ConfigServerOptions,
         "Configuration server service"],
        ["certs", None, certs.CertsCreatorOptions, "Certificates creator"],
    ]

    def opt_config(self, config_file):
        config_file = self.opts['config'] = os.path.abspath(
            os.path.expanduser(config_file))
        parser = SafeConfigParser()
        parser.read([config_file])
        self._set_defaults(parser, self.subCommands)

    def _set_defaults(self, parser, subCommands):
        parser_defaults = parser.defaults()
        for name, sname, options, doc in subCommands:
            if hasattr(options, 'optParameters'):
                parameters = []
                instance = options().__class__
                reflect.accumulateClassList(instance, 'optParameters',
                                            parameters)
                for idx, parameter in enumerate(parameters):
                    long, short, default, doc, type = util.padTo(5, parameter)
                    _def = parser_defaults.get(long, default)
                    if parser.has_option(name, long):
                        _def = parser.get(name, long, _def)
                    if _def != default:
                        option = [long, short, type and type(_def) or _def, doc]
                        if type:
                            option.append(type)
                        parameters[idx] = option
                # Override class defaults with config-file defaults
                options.optParameters = parameters
            if hasattr(options, "subCommands"):
                self._set_defaults(parser, options.subCommands)

    @property
    def store(self):
        if not hasattr(self, 'storage'):
            self.opts['storage'] = os.path.abspath(os.path.expanduser(
                self.opts.get('storage'))
            )
            self.storage = Store(self.opts.get('storage')) #, debug=True)
        return self.storage

    def postOptions(self):
        self.opts['storage'] = os.path.abspath(os.path.expanduser(
            self.opts.get('storage'))
        )
        self.storage = Store(self.opts.get('storage')) #, debug=True)

class ServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = __package__.lower()
    description = __summary__
    options = SSHgDOptions

    def makeService(self, options):
        return options.subOptions.getService()


if __name__ == '__main__':
    import sys
    from twisted.python import usage

    sys.path.insert(0, os.path.abspath('../../'))
    print sys.path

    runner = SSHgDOptions()
    try:
        runner.parseOptions() # When given no argument, parses sys.argv[1:]
    except usage.UsageError, errortext:
        print '%s: %s' % (sys.argv[0], errortext)
        print '%s: Try --help for usage details.' % (sys.argv[0])
        sys.exit(1)
