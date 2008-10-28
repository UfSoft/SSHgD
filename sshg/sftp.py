# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

import os
import struct

from twisted.conch import unix, error
from twisted.conch.ssh import filetransfer
from twisted.python import components, log
from twisted.internet import defer

from twisted.conch.unix import UnixSFTPFile, UnixSFTPDirectory

import errno

SSH_FX_NO_SPACE_ON_FILESYSTEM = 14
SSH_FX_QUOTA_EXCEEDED = 15


class LimittedUnixSFTPFile(UnixSFTPFile):
    file_size = 0
    file_limit = 51200 # Aprox 130 lines of pub keys; more than enough
    limit_reached = False

    def writeChunk(self, offset, data):
        if self.file_size > self.file_limit:
#            log.msg("User %s tried to upload a file bigger than %i bytes. "
#                    "Bailing out!!!" %(self.server.avatar.username,
#                                       self.file_limit))
#            raise Exception("File limit reached")
#            print dir(self)
#            print dir(self.server)
#            self.server.connectionLost("File limit reached")
            raise filetransfer.SFTPError(filetransfer.FX_FAILURE, "no more space just go away already")
            raise IOError(errno.EACCES, "File limit reached")
#            raise errno.ENOSPC
#            self.limit_reached = True
##            print dir(self.server)
#            self.server.avatar.conn.transport.transport.loseConnection()
#            print self.server.avatar.conn.transport.transport
#            print dir(self.server.avatar)
#            print dir(self.server.avatar.factory)
#            print dir(self.server.avatar.factory.protocol)
##            self.server.avatar.logout()
##            self.server._sendRequest(self.handle, 25, "file limit reached")
#            return 0
            # SSH_FX_INVALID_PARAMETER
            #
#            raise errno.EACCES
#            raise EOFError("File limit reached. Stopping")
#            raise error.ConchError()
#            self.close()
#            print "FD", self.fd
#            raise NotImplementedError
        uploaded = UnixSFTPFile.writeChunk(self, offset, data)
        self.file_size += uploaded
        return uploaded

class SFTPFileTransfer(unix.SFTPServerForUnixConchUser):

    def __init__(self, avatar):
        unix.SFTPServerForUnixConchUser.__init__(self, avatar)

    def gotVersion(self, version, extData):
        return {}

    def openFile(self, filename, flags, attrs):
        print "ATTRS", attrs, "Flags", flags
        return LimittedUnixSFTPFile(self, self._absPath(filename), flags, attrs)

    def openDirectory(self, path):
        return UnixSFTPDirectory(self, self.avatar.getHomeDir())

    def realPath(self, path):
        return '/'

    def _notimpl(self, *args, **kwargs):
        raise NotImplementedError

    makeDirectory = removeDirectory = readLink = makeLink = _notimpl
    renameFile = removeFile = setAttrs = _notimpl


class FileTransferServer(filetransfer.FileTransferServer):

    def packet_OPEN(self, data):
        requestId = data[:4]
        data = data[4:]
        filename, data = filetransfer.getNS(data)
        flags ,= struct.unpack('!L', data[:4])
        data = data[4:]
        attrs, data = self._parseAttributes(data)
        # Force file to be written on the same dir. No change dir's allowed
        filename = os.path.basename(filename)

        assert data == '', 'still have data in OPEN: %s' % repr(data)
        d = defer.maybeDeferred(self.client.openFile, filename, flags, attrs)
        d.addCallback(self._cbOpenFile, requestId)
        d.addErrback(self._ebStatus, requestId, "open failed")

    def packet_OPENDIR(self, data):
        requestId = data[:4]
        data = data[4:]
        path, data = filetransfer.getNS(data)
        # No change dir's allowed
        path = os.path.basename(path)
        assert data == '', 'still have data in OPENDIR: %s' % repr(data)
        d = defer.maybeDeferred(self.client.openDirectory, path)
        d.addCallback(self._cbOpenDirectory, requestId)
        d.addErrback(self._ebStatus, requestId, "opendir failed")

    def packet_STAT(self, data, followLinks = 1):
        followLinks = 0 # Don't follow links
        requestId = data[:4]
        data = data[4:]
        path, data = filetransfer.getNS(data)
        # No change dir's allowed
        if not path == '/':
            log.msg("Original path: %s" % path)
            path = os.path.basename(path)
            log.msg("New path: %s" % path)
        assert data == '', 'still have data in STAT/LSTAT: %s' % repr(data)
        d = defer.maybeDeferred(self.client.getAttrs, path, followLinks)
        d.addCallback(self._cbStat, requestId)
        d.addErrback(self._ebStatus, requestId, 'stat/lstat failed')

    def packet_SETSTAT(self, data):
        requestId = data[:4]
        data = data[4:]
        path, data = filetransfer.getNS(data)
        attrs, data = self._parseAttributes(data)
        # No change dir's allowed
        path = os.path.basename(path)
        if data != '':
            log.msg('WARN: still have data in SETSTAT: %s' % repr(data))
        d = defer.maybeDeferred(self.client.setAttrs, path, attrs)
        d.addCallback(self._cbStatus, requestId, 'setstat succeeded')
        d.addErrback(self._ebStatus, requestId, 'setstat failed')

#    def packet_WRITE(self, data):
#        requestId = data[:4]
#        data = data[4:]
#        handle, data = filetransfer.getNS(data)
#        offset, = struct.unpack('!Q', data[:8])
#        data = data[8:]
#        writeData, data = filetransfer.getNS(data)
#        assert data == '', 'still have data in WRITE: %s' % repr(data)
#        if handle not in self.openFiles:
#            self._ebWrite(failure.Failure(KeyError()), requestId)
#        else:
#            fileObj = self.openFiles[handle]
#            d = defer.maybeDeferred(fileObj.writeChunk, offset, writeData)
#            d.addCallback(self._cbStatus, requestId, "write succeeded")
#            d.addErrback(self._ebStatus, requestId, "write failed")

#    def _ebStatus(self, reason, requestId, msg = "request failed"):
#        code = filetransfer.FX_FAILURE
#        message = msg
#        if reason.type in (IOError, OSError):
#            if reason.value.errno == errno.ENOENT: # no such file
#                code = filetransfer.FX_NO_SUCH_FILE
#                message = reason.value.strerror
#            elif reason.value.errno == errno.EACCES: # permission denied
#                code = filetransfer.FX_PERMISSION_DENIED
#                message = reason.value.strerror
#            elif reason.value.errno == errno.EEXIST:
#                code = filetransfer.FX_FILE_ALREADY_EXISTS
#            elif reason.value.errno == errno.ENOSPC:
#                code = 15 #14 # 25
#            else:
#                log.err(reason)
#        elif reason.type == EOFError: # EOF
#            code = filetransfer.FX_EOF
#            if reason.value.args:
#                message = reason.value.args[0]
#        elif reason.type == NotImplementedError:
#            code = filetransfer.FX_OP_UNSUPPORTED
#            if reason.value.args:
#                message = reason.value.args[0]
#        elif reason.type == filetransfer.SFTPError:
#            code = reason.value.code
#            message = reason.value.message
#        else:
#            log.err(reason)
#        self._sendStatus(requestId, code, message)



    def dataReceived(self, data):
        self.buf += data
        while len(self.buf) > 5:
            length, kind = struct.unpack('!LB', self.buf[:5])
            if len(self.buf) < 4 + length:
                return
            data, self.buf = self.buf[5:4+length], self.buf[4+length:]
            packetType = self.packetTypes.get(kind, None)
            if not packetType:
                log.msg('no packet type for', kind)
                continue
            f = getattr(self, 'packet_%s' % packetType, None)
            if not f:
                log.msg('not implemented: %s' % packetType)
                log.msg(repr(data[4:]))
                reqId, = struct.unpack('!L', data[:4])
                self._sendStatus(reqId, filetransfer.FX_OP_UNSUPPORTED,
                                 "don't understand %s" % packetType)
                #XXX not implemented
                continue
            try:
                print "FUNCTION", f
                f(data)
            except:
                log.err()
                continue
                reqId ,= struct.unpack('!L', data[:4])
                self._ebStatus(failure.Failure(e), reqId)

