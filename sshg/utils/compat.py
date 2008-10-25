# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

try:
    from twisted.python.util import runAsEffectiveUser
except ImportError:
    def runAsEffectiveUser(euid, egid, function, *args, **kwargs):
        """
        Run the given function wrapped with seteuid/setegid calls.

        This will try to minimize the number of seteuid/setegid calls, comparing
        current and wanted permissions

        @param euid: effective UID used to call the function.
        @type euid: C{int}

        @type egid: effective GID used to call the function.
        @param egid: C{int}

        @param function: the function run with the specific permission.
        @type function: any callable

        @param *args: arguments passed to C{function}
        @param **kwargs: keyword arguments passed to C{function}
        """
        uid, gid = os.geteuid(), os.getegid()
        if uid == euid and gid == egid:
            return function(*args, **kwargs)
        else:
            if uid != 0 and (uid != euid or gid != egid):
                os.seteuid(0)
            if gid != egid:
                os.setegid(egid)
            if euid != 0 and (euid != uid or gid != egid):
                os.seteuid(euid)
            try:
                return function(*args, **kwargs)
            finally:
                if euid != 0 and (uid != euid or gid != egid):
                    os.seteuid(0)
                if gid != egid:
                    os.setegid(gid)
                if uid != 0 and (uid != euid or gid != egid):
                    os.seteuid(uid)
