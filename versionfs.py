#######################
#Modified by : ssmi397#
#Selina Smith         #
#######################

#!/usr/bin/env python
from __future__ import with_statement

import logging
import shutil 
import os
import sys
import errno
import filecmp
import fnmatch

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
#https://www.pythonforbeginners.com/os/python-the-shutil-module

class VersionFS(LoggingMixIn, Operations):
    def __init__(self):
        # get current working directory as place for versions tree
        self.root = os.path.join(os.getcwd(), '.versiondir')
        self.change = False
        # check to see if the versions directory already exists
        if os.path.exists(self.root):
			
            print ' '			
        else:
            print 'Creating version directory.'
            os.mkdir(self.root)

    # Helpers
    # =======

    def _full_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.root, partial)
        return path
	

    
    # Filesystem methods
    # ==================

	

    def access(self, path, mode):
        print "access:", path, mode
        full_path = self._full_path(path)
        if not os.access(full_path, mode):
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        print "chmod:", path, mode
        full_path = self._full_path(path)
        return os.chmod(full_path, mode)

    def chown(self, path, uid, gid):
        print "chown:", path, uid, gid
        full_path = self._full_path(path)
        return os.chown(full_path, uid, gid)

    def getattr(self, path, fh=None):
        print "getattr:", path
        full_path = self._full_path(path)
        st = os.lstat(full_path)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                     'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))



    def readdir(self, path, fh):
        print "readdir:", path
        full_path = self._full_path(path)
	
        dirents = ['.', '..']
        if os.path.isdir(full_path): 
			dirents.extend(os.listdir(full_path))
        for r in dirents:
			if "*version" not in r: yield r

    def readlink(self, path):
        print "readlink:", path
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            #Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.root)
        else:
            return pathname

    def mknod(self, path, mode, dev):
        print "mknod:", path, mode, dev
        return os.mknod(self._full_path(path), mode, dev)

    def rmdir(self, path):
        print "rmdir:", path
        full_path = self._full_path(path)
        return os.rmdir(full_path)

    def mkdir(self, path, mode):
        print "mkdir:", path, mode
        return os.mkdir(self._full_path(path), mode)

    def statfs(self, path):
        print "statfs:", path
        full_path = self._full_path(path)
        stv = os.statvfs(full_path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))

    def unlink(self, path):
        print "unlink:", path
        return os.unlink(self._full_path(path))

    def symlink(self, name, target):
        print "symlink:", name, target
        return os.symlink(target, self._full_path(name))


    def removeOldVersions(self,filename):
        dirents = []      
        versionsFilenames = [filename+"*version2",filename+"*version3",filename+"*version4",filename+"*version5",filename+"*version6"]        

        if os.path.isdir(self.root): 
			dirents.extend(os.listdir(self.root))
        for r in dirents:
            for i in versionsFilenames:                
                if str(r) == str(i):                 
                    full_path = self._full_path(r)
                    os.remove(full_path)
                
                


    def listVersions(self, filename):         
        dirents = []
        versions = 0       
        if os.path.isdir(self.root): 
			dirents.extend(os.listdir(self.root))
        for r in dirents:            
            if fnmatch.fnmatch(r,filename): 
                if os.stat(self._full_path(r)).st_size > 0:
                    versions += 1                
            versionsFilenames = [filename+"*version2",filename+"*version3",filename+"*version4",filename+"*version5",filename+"*version6"]        
            for i in versionsFilenames:                
                if str(r) == str(i): 
                    if os.stat(self._full_path(r)).st_size > 0:
                        versions += 1   

        v = 1
        while v <= versions:
            print filename+"."+str(v)
            v += 1
            

    def mkcurrent(self, filename, version):
        if str(version) == "1":
            full_path = self._full_path('/'+filename)
        else:
            full_path = self._full_path('/'+filename+"*version"+str(version))
        current = self._full_path('/'+filename + "*versionCurr")      
        os.open(current, os.O_WRONLY | os.O_CREAT, 33188)
        shutil.copyfile(full_path,current) 
        sortedFiles  = [0,0,0,0,0,0,0]       
        search_dir = self.root
        os.chdir(search_dir)
        files = filter(os.path.isfile, os.listdir(search_dir))
        files = [os.path.join(search_dir, f) for f in files] # add path to each file
        c = 0    
        filename = str("/"+filename)        
        while c < len(files):
            r = files[c]         
            last_chars = str(r[-3:])                    
            versionsList = ['urr','on2','on3','on4','on5','on6'] 
            if str(filename) in r:                
                if last_chars == 'urr':
                    sortedFiles[6]=r
                if last_chars == 'on2':
                     sortedFiles[4]= r
                if last_chars == 'on3':
                    sortedFiles[3]=r
                if last_chars == 'on4':
                    sortedFiles[2]=r
                if last_chars == 'on5':
                    sortedFiles[1]=r
                if last_chars == 'on6':
                    sortedFiles[0]=r
                if last_chars not in versionsList:
                    sortedFiles[5]=r
                c += 1
            else:
                c += 1
        os.unlink(sortedFiles[0]) #deleted V6
        i = 1
        a = 5
        while i <= 4:
            old = str(sortedFiles[i])
            new = str(old[:-1]+str(a+1))
            os.rename(old,new)
            a -= 1
            i += 1
        oldV2 = str(sortedFiles[5])
        newV2 = str(old[:-1]+str(2))
        os.rename(oldV2,newV2)
        curr = str(sortedFiles[6])
        newV1 = str(curr[:-12])
        os.rename(curr,newV1)

    def utimens(self, path, times=None):
        print "utimens:", path, times
        return os.utime(self._full_path(path), times)

    def deleteDir(self):
		print "Sucessfully Shutdown"
		return shutil.rmtree(self.root)	 
	
    def link(self, target, name):
		#print "link:", target, name       
        return os.link(self._full_path(name), self._full_path(target))

    # File methods
    # ============

    def open(self, path, flags):
        print '** open:', path, '**'
        full_path = self._full_path(path)
        tempFilePath = self._full_path(path + "*versiontemp")
        os.open(tempFilePath, os.O_WRONLY | os.O_CREAT, 33188)
        shutil.copyfile(full_path,tempFilePath)
        self.change = False
        checkVersions = self._full_path(path + "*version2")
        if os.path.exists(checkVersions) == False and "*version" not in path: 
            i = 2
            print "here"
            while i < 7:
                filename = str(path + "*version"+ str(i))	
                full_pathV = self._full_path(filename)
                os.open(full_pathV, os.O_WRONLY | os.O_CREAT, 33188)
                i += 1
        return os.open(full_path, flags)

    def create(self, path, mode, fi=None):       	
		#print '** create:', path, '**'
        self.change = False
        full_path = self._full_path(path)	
        print "mode: ",mode
        return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)
		 
    def read(self, path, length, offset, fh):
        print '** read:', path, '**'
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):
        print '** write:', path, '**'
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    def truncate(self, path, length, fh=None):
        print '** truncate:', path, '**'
        full_path = self._full_path(path)
        self.change = True
        with open(full_path, 'r+') as f:
            f.truncate(length)

    def flush(self, path, fh):
        print '** flush', path, '**'
        return os.fsync(fh)

    def release(self, path, fh):
        print '** release', path, '**'
        full_path = self._full_path(path)
        #check if tempfile exits, then check if files are the same. Delete tempfile
        tempFilePath = self._full_path(path + "*versiontemp")
        sortedFiles  = [0,0,0,0,0,0,0]
        if os.path.exists(tempFilePath): 
            if (filecmp.cmp(full_path,tempFilePath,False) == True):
                os.unlink(tempFilePath)
                print "No Change"
            else:
                search_dir = self.root
                os.chdir(search_dir)
                files = filter(os.path.isfile, os.listdir(search_dir))
                files = [os.path.join(search_dir, f) for f in files] # add path to each file
                c = 0    
                while c < len(files):
                    r = files[c]
                    last_chars = str(r[-3:])                    
                    versionsList = ['emp','on2','on3','on4','on5','on6']
                    if str(path) in r:
                        if last_chars == 'emp':
                            sortedFiles[5]=r
                        if last_chars == 'on2':
                            sortedFiles[4]= r
                        if last_chars == 'on3':
                            sortedFiles[3]=r
                        if last_chars == 'on4':
                            sortedFiles[2]=r
                        if last_chars == 'on5':
                            sortedFiles[1]=r
                        if last_chars == 'on6':
                            sortedFiles[0]=r                             
                        if last_chars not in versionsList:
                            sortedFiles[6]=r
                            print r
                        c += 1
                    else:
                        c += 1
                os.unlink(sortedFiles[0]) #deleted V6
                i = 1
                a = 5
                while i <= 4:
                    old = str(sortedFiles[i])
                    new = str(old[:-1]+str(a+1))                  
                    os.rename(old,new)
                    a -= 1
                    i += 1
                tempOld = str(sortedFiles[5])    
                tempNew = str(tempOld[:-4]+str(2))
                os.rename(tempOld,tempNew)
        else:
            if "*version" not in full_path:
                while i < 7:
                    filename = str(path + "*version"+ str(i))	
                    full_pathV = self._full_path(filename)
                    os.open(full_pathV, os.O_WRONLY | os.O_CREAT, 33188)
                    i += 1
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        print '** fsync:', path, '**'
        return self.flush(path, fh)	 


def main(mountpoint):
    print "Compsci340 A3 ssmi397"
    FUSE(VersionFS(), mountpoint, nothreads=True, foreground=True)

if __name__ == '__main__':
    #logging.basicConfig(level=logging.DEBUG)
    main(sys.argv[1])



