# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

import os
import sys
import getopt
from ConfigParser import SafeConfigParser

from twisted.python import usage

class BaseOptions(usage.Options):

    def opt_version(self):
        """Show version"""
        print os.path.basename(sys.argv[0]), '- 0.1'
    opt_v = opt_version

    def opt_help(self):
        """Show this help message"""
        super(BaseOptions, self).opt_help()
    opt_h = opt_help

    def parseOptions(self, options=None):
        """
        The guts of the command-line parser.
        """

        if options is None:
            options = sys.argv[1:]
        try:
            opts, args = getopt.getopt(options,
                                       self.shortOpt, self.longOpt)
        except getopt.error, e:
            raise usage.UsageError(str(e))

        for opt, arg in opts:
            if opt[1] == '-':
                opt = opt[2:]
            else:
                opt = opt[1:]

            optMangled = opt
            if optMangled not in self.synonyms:
                optMangled = opt.replace("-", "_")
                if optMangled not in self.synonyms:
                    raise usage.UsageError("No such option '%s'" % (opt,))

            optMangled = self.synonyms[optMangled]
            if isinstance(self._dispatch[optMangled], usage.CoerceParameter):
                self._dispatch[optMangled].dispatch(optMangled, arg)
            else:
                self._dispatch[optMangled](optMangled, arg)

        if (getattr(self, 'subCommands', None)
            and (args or self.defaultSubCommand is not None)):
            if not args:
                args = [self.defaultSubCommand]
            sub, rest = args[0], args[1:]
            for (cmd, short, parser, doc) in self.subCommands:
                if sub == cmd or sub == short:
                    self.subCommand = cmd
                    self.subOptions = parser()
                    # Config file options parsing
                    cfgfile = None
                    if self.parent and 'config' in self.parent:
                        cfgfile = self.parent.get('config')
                    elif 'config' in self:
                        cfgfile = self.get('config')
                    if cfgfile is not None:
                        parser = SafeConfigParser()
                        parser.read([cfgfile])
                        self.subOptions.defaults.update(parser.defaults())
                        if parser.has_section(cmd):
                            self.subOptions.defaults.update(
                                dict(parser.items(cmd))
                            )
                    # Resume twisted code
                    self.subOptions.parent = self
                    self.subOptions.parseOptions(rest)
                    break
            else:
                raise usage.UsageError("Unknown command: %s" % sub)
        else:
            try:
                self.parseArgs(*args)
            except TypeError:
                raise usage.UsageError("Wrong number of arguments.")

        self.postOptions()
    def getService(self):
        raise NotImplementedError
