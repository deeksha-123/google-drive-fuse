
from __future__ import with_statement
from __future__ import print_function
#def f1():
	#FUSE(Passthrough(drive_folder), mount_point, nothreads=True, foreground=False)
	

import os
import sys
import errno
from fuse import FUSE, FuseOSError, Operations
print("main")
os.system('clear')
x=os.getcwd()
#print(x)

mount_point = x+"/mount_point"
drive_folder = x+"/gdrive"


if not os.path.isdir(drive_folder):
    os.mkdir(drive_folder)
if not os.path.isdir(mount_point):
    os.mkdir(mount_point)

class Passthrough(Operations):
    def __init__(self, root):
        self.root = root
        print("main_init")

    # creating full path to google drive

    def _full_path(self, partial):
        partial = partial.lstrip("/")
        path = os.path.join(self.root, partial)
        return path

    # Filesystem functions
    
    #converts link to symbolic link
    def symlink(self, name, target):
        print("symlink executed:")
        return os.symlink(name, self._full_path(target))
    
    #change the owner
    def chown(self, path, uid, gid):
        print("chown executed:")
        full_path = self._full_path(path)
        return os.chown(full_path, uid, gid)

    #retrieves the information about the file
    def getattr(self, path, fh=None):
        print("getattr executed:")
        full_path = self._full_path(path)
        st = os.lstat(full_path)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                     'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
	
    #validating a path
    def access(self, path, mode):
        full_path = self._full_path(path)
        print("main_access")
        if not os.access(full_path, mode):
            raise FuseOSError(errno.EACCES)
    
    #creates the image of the google drive	
    def link(self, target, name):
        print("link executed:")
        return os.link(self._full_path(target), self._full_path(name))
    
    #returns the status of the file system
    def statfs(self, path):
        print("statfs executed:")
        full_path = self._full_path(path)
        stv = os.statvfs(full_path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))
    
    #updates the modified,creation time 
    def utimens(self, path, times=None):
        print("utimens executed:")
        return os.utime(self._full_path(path), times)
    
    #creating node for each file in google drive
    def mknod(self, path, mode, dev):
        print("mknod executed:")
        return os.mknod(self._full_path(path), mode, dev)
    
    #change mode from kernel to user mode
    def chmod(self, path, mode):
        print("chmod executed:")
        full_path = self._full_path(path)
        return os.chmod(full_path, mode)
    
    #if directory exists then returns the directories at that path
    def readdir(self, path, fh):
        print("readdir executed:")
        full_path = self._full_path(path)
        dirents = ['.', '..']
        if os.path.isdir(full_path):
            dirents.extend(os.listdir(full_path))
        for r in dirents:
            yield r
    
    #symbolic link to readable form
    def readlink(self, path):
        print("readlink executed:")
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.root)
        else:
            return pathname
    
    #remove a directory
    def rmdir(self, path):
        print("rmdir executed:")
        full_path = self._full_path(path)
        return os.rmdir(full_path)
    
    #creating a directory
    def mkdir(self, path, mode):
        print("mkdir executed:")
        return os.mkdir(self._full_path(path), mode)
    
    #removing the image of the google drive
    def unlink(self, path):
        print("unlink executed:")
        return os.unlink(self._full_path(path))

    def rename(self, old, new):
        print("rename executed:")
        print(old)
        print(new)
        return os.rename(self._full_path(old), self._full_path(new))


    # File methods

    def fsync(self, path, fdatasync, fh):
        print("fsync executed:")
        return self.flush(path, fh)

    def truncate(self, path, length, fh=None):
        print("truncate executed:")
        full_path = self._full_path(path)
        with open(full_path, 'r+') as f:
            f.truncate(length)

    def open(self, path, flags):
        print("open executed:")
        full_path = self._full_path(path)
        return os.open(full_path, flags)

    def read(self, path, length, offset, fh):
        print("read executed:")
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def flush(self, path, fh):
        print("flush executed:")
        return os.fsync(fh)
    
    def release(self, path, fh):
        print("release executed:")
        return os.close(fh)

    def write(self, path, buf, offset, fh):
        print("write executed:")
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)
    
    def create(self, path, mode, fi=None):
        print("create executed:")
        full_path = self._full_path(path)
        print(full_path)
        return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)


if __name__ == '__main__':
    FUSE(Passthrough(drive_folder), mount_point, nothreads=True, foreground=False)
    print("fuse completed")
    
