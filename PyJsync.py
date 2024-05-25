#PyJsync Utility to sync files between directories
#written by Jarrett McAlicher

# V1.0   - Basic functionality
# V1.1   - Adding more future enhancement switches: -d
#          Also updated help file and other messaging.
# V1.2   - Added -r for Recuse sub directories and changed
#          default to only process listed directory.
#          Also added -c for checksum verification.
# V1.2.1 - Added check for '-' in first attribute as error checking
# V1.2.2 - Added check on directories and also creating destination 
#          directory if it doesn't exist - 2/19/2024
# V1.3   - Added -f replicate Folder structure 2/20/24 and updated 
#          some output messages.
# V1.4   - Added -y for auto (Y)es to create destination folder if 
#          it doesn't exist 2/24/24
# V1.5   - Added support for PyRemove_MAC.py to use -x to remove _MACOSX folders
#          from source directory before syncing.
# V1.6   - Replace sys.argv[1] with variable args and setup -M to use the macro file M.m
# V1.7   - Prepare system for eventual gui interface. - Move main program to function and update global variables
#          Also move system arguments to variables.
#          Moved help file to help.h file
# V1.8   - Add "C" Copy (no delete) as well as an auto-rename
#          Added filename() function to provide a non-duplcate filename
#          Various output enhancements on the command line verison
# V1.8.1 - More updates to remove command line output when using GUI

'''
FUTURE ENHANCEMENT:
-V mo(V)e (instead of sync) (copy with a source delete.)

'''

ver='1.8.1'

import os
import os.path
#from os import.system, name
import shutil
#import fnmatch # to be implemented later for filename matching.
import hashlib
from stat import ST_SIZE
import sys
import PyRemove_MAC
from cnfg import *

verbose=False
cverbose=True
rverbose=True #May make this default for command version.

#objects
class directoryandfiles:
    def __init__(self,directory,recurse):
        self.directory=directory
        self.data=[]
        if recurse==True:
            for path, subdir, files in os.walk(directory):
                dir=path.replace(directory,"")
                self.data.append('D:'+dir)
                for file in files:
                    self.data.append('F:'+dir+'/'+file)
        elif recurse==False:
            for file in os.listdir(directory):
                if os.path.isfile(os.path.join(directory,file)):
                    self.data.append('F:/'+file)
                if verbose==True: 
                    print (f'FILE: {file}')
            if verbose==True: print (f'FILE LIST: {self.data}')

    
def printhelp():
    # This will print the help file to the console
    h=open('help.h','r')
    help=h.read()
    if gui==False: print (help)

def getmatchstatus(slist,dlist):
    '''returns a list with 3 lists as follows:\n
    1st List are items not in destination\n
    2nd list are items that are in the destination\n
    3rd list are items in destination not in source'''
    sset=set(slist)
    dset=set(dlist)
    return [list(sset.difference(dset)),list(sset.intersection(dset)),list(dset.difference(sset))]

def gethash(filename):
    return hashlib.md5(open(filename,'rb').read()).hexdigest()

def getifdiff(sfile,dfile):
    sstat=os.stat(sfile)
    dstat=os.stat(dfile)
    sstat1=str(sstat.st_size)+'|'+str(sstat.st_mtime)
    dstat1=str(dstat.st_size)+'|'+str(dstat.st_mtime)
    if verbose==True: 
        print ('*** date size comparison')
        print (sfile)
        print (str(sstat.st_size)+'|'+str(sstat.st_mtime))
        print (str(dstat.st_size)+'|'+str(dstat.st_mtime))
        print (sstat1==dstat1)

    return sstat1==dstat1

def clearscreen():
    if os.name=='nt':
        os.system('cls')
    else:
        os.system('clear')

def filename(filepath):
    if os.path.isfile(filepath)==False:
        if verbose==True: print(filepath)
        return filepath  
    dup=False
    num=1
    file, ext = os.path.splitext(filepath)
    if verbose==True:
        print (f'file: {file}\next: {ext}')
    if file.rfind("(")!=-1:
        file=file[:file.rfind("(")]
        file.strip()
    while dup==False:
        nfile=f'{file} ({num}){ext}'
        if os.path.isfile(nfile)==False:
            if verbose==True: print (nfile)
            return nfile
            break
        else:
            num+=1
    pass
    

def pyjsync(args, sDirectory, dDirectory):   

    global verbose
    global cverbose
    
    #set defaults for variables
    global rverbose
    filesize=0
    transfersize=0
    recurse=False
    doCheckSum=False
    testdir=False
    fsync=False
    autoYes=False
    remove_MAC=False
    gui=False
    copy=False

    # ==== Parce out the arguments

    if "M"  in args:
        if os.path.exists('M.m')==False:
            print('Macro file M.m does not exist')
            exit()
        file=open('M.m',"r")
        line=file.readline()
        if len(line)>7:
            print ('Macro file M.m is malformed')
            exit()
        args=line
        file.close()
        if verbose==True: print (args)

        # Must Include Action item s or t
        if 's' not in args and 't' not in args:
            print ('ERROR: Must include -s (S)ync or -t (T)est in command line.')
            exit()

        if len(sys.argv)!=4:
            print('\nPlease Specify at least 3 arguments or -h for help\n')
            exit()

        if 'v' in args:
            rverbose=True
    
    if 'c' in args:
        doCheckSum=True

    if 'C' in args:
        copy=True
        sync=False

    if 't' in args:
        if gui==False: print('Testing Mode. No Changes will be committed.')
        sync=False
        doCheckSum=False
    else:
        sync=True

    if 'r' in args:
        recurse=True
    
    if 'f' in args:
        fsync=True
        doCheckSum=False
    
    if 'y' in args:
        autoYes=True

    if 'x' in args:
        remove_MAC=True

    if 'g' in args: #this is only used internally when passing from gui.
        gui=True

    # ====== Check Source and Destination Directories ========
    if verbose==True: print(f'*** {sDirectory} and {dDirectory}')
    if os.path.exists(sDirectory)==False:
        if gui==False: print(f'\nERROR: Source directory does not exist\n - {sDirectory}\n')
        exit()
    
    if os.path.exists(dDirectory)==False:
        if autoYes==False:
            if gui==False: print(f'\nDestination directory "{dDirectory} does not exist.')
            answer=input('Would you like it to be created? (y/n):')
            if answer=='y':
                
                if sync==True:
                    if gui==False: print('Creating destination path . . . ',end='')
                    os.makedirs(dDirectory)
                    if gui==False: print('Directory created.\n')
                else:
                    if gui==False: print('TESTING: Source Directory has been created and will be deleted when this test\nrun is complete.')
                    os.makedirs(dDirectory)
                    testdir=True
            else:
                if gui==False: print('Operation cancelled.\n')
                exit()
        else:
            if sync==True:
                if gui==False: print('Creating destination path . . . ',end='')
                os.makedirs(dDirectory)
                if gui==False: print('Directory created.\n')
            else:
                if gui==False: print('TESTING: Source Directory has been created and will be deleted when this test\nrun is complete.')
                os.makedirs(dDirectory)
                testdir=True



    
    # ====== Main Part of Program =========
    
    if remove_MAC==True:
        if gui==False: print('Removing _MACOSX Folders.')
        mfiles=PyRemove_MAC.mfiles(sDirectory)
        if mfiles.checkqty()>0 and sync==True:
            mfiles.remove()

    if rverbose==True and gui==False: print(f'\nScanning Source...',end=' ')
    sfiles=directoryandfiles(sDirectory,recurse) #Source Directory and Files
    
    if verbose==True and gui==False: print(sfiles.data)
    if rverbose==True: print(f'Scanning Destination ...',end=' ')
    
    dfiles=directoryandfiles(dDirectory,recurse) #Destination Directory and Files
    if verbose==True: print(getmatchstatus(sfiles.data,dfiles.data))
    if rverbose==True and gui==False: print(f'Building Differences ...')
    
    statuses=getmatchstatus(sfiles.data,dfiles.data)

    wfilesDF=[] #Delete Files
    wfilesDD=[] #Delete Directories
    wfilesNF=[] #New files
    wfilesND=[] #New Directory
    wfilesUF=[] #Update Files

    # Build Listings

    for status in statuses[0]: #Items are NOT in the destination
        name=status[2:]
        if status[0]=="D":
            wfilesND.append(name)
        else:
            wfilesNF.append(name)
        
   
    for status in statuses[1]: # Items ARE in the destination
        if verbose==True: print (status)
        if status[0]=="D":
            continue
        else:
            sfile=sDirectory+status[2:]
            dfile=dDirectory+status[2:]
            if verbose==True:
                print(f'{sfile}||{dfile}')
                print(f'{dfile} needs updated')
                #print(gethash(sfile)+'|'+ gethash(dfile)) #Not used anymore at this point... 
            
            if copy==False:
                if getifdiff(sfile,dfile)==True:
                    if verbose==True: print(f'{dfile} matches size/date .. Skipping')          
                else:
                    if verbose==True: print(f'{dfile} needs updated')
                    wfilesUF.append(status[2:])
            if copy==True:
                wfilesUF.append(status[2:])
                if 'd' not in args:
                    args=args+'d'
    if 'd' in args and copy==False:
        if rverbose==True: print('Not deleting files from destination that do not exist in source via -d switch')
    else:
        for status in statuses[2]: #Items are NOT not in the Source
            if status[0]=="D":
                wfilesDD.append(status[2:])
            else:
                wfilesDF.append(status[2:])
    


    # ===== This Part actually does the work.

    if len(wfilesND)>0:
        if rverbose==True and gui==False: print('Creating directory(ies):')
        for dir in wfilesND:
            if rverbose==True and gui==False: print (f'  {dir}')
            try:
                if sync==True or copy==True: os.makedirs(dDirectory+dir)
            except FileExistsError:
                if gui==False: print(f'{dir} already exists. Skipping.')

        #if rverbose==True: print (f'Directories created: {len(wfilesND)}')

    if len(wfilesNF)>0:
        if fsync==False:
            if rverbose==True and gui==False: print ('Creating file(s):')
            for file in wfilesNF:
                file_stats=os.stat(sDirectory+file)
                filesize=file_stats.st_size
                transfersize+=filesize
                if rverbose==True and gui==False: print(f'  {file} in {filesize} bytes')
                if sync==True and fsync==False: shutil.copy2(f'{sDirectory}{file}',f'{dDirectory}{file}')
                if doCheckSum==True:
                    if gethash(sDirectory+file)!=gethash(dDirectory+file):
                        if gui==False: print (f'ERROR: {dfile} does not match source after copy!!!')
                        if verbose==True: print (f'Source File: {sfile} {gethash(sfile)}\nDestination File: {dfile} {gethash(dfile)}')
                    if gui==False: print ('Checksum on copy (new) matches')
        #if rverbose==True: print (f'Files created: {len(wfilesNF)}')

    if len(wfilesUF)>0:
        if fsync==False:
            if rverbose==True and gui==False: print('Updating file(s):')
            for file in wfilesUF:
                file_stats=os.stat(sDirectory+file)
                filesize=file_stats.st_size
                transfersize+=filesize
                if rverbose==True and gui==False: print(f'  {file} with {filesize} bytes')
                if sync==True: 
                    os.remove(dDirectory+file)
                    shutil.copy2(f'{sDirectory}{file}',f'{dDirectory}{file}')
                if doCheckSum==True:
                    if gethash(sfile)!=gethash(dfile):
                        if gui==False: print (f'ERROR: {dfile} does not match source after copy!!!')
                        if verbose==True: print (f'Source File: {sfile} {gethash(sfile)}\nDestination File: {dfile} {gethash(dfile)}')
                    if gui==False: print ('Checksum on update matches')
                if copy==True and testing==False:
                    if verbose==True: print(f'{sDirectory}{file} to {filename(dDirectory+file)}')
                    shutil.copy2(f'{sDirectory}{file}',f'{filename(dDirectory+file)}')

        #if rverbose==True: print (f'Files updated: {len(wfilesUF)}')
    if copy==False: #if Copy then do not delete any files or directories
        if len(wfilesDF)>0:
            if rverbose==True and gui==False: print('Deleting file(s):')
            for file in wfilesDF:
                if rverbose==True and gui==False: print(f'  {file}')
                if sync==True: os.remove(dDirectory+file)
            #if rverbose==True: print (f'Files Deleted:  {len(wfilesDF)}')
        if len(wfilesDD)>0:
            if rverbose==True and gui==False: print ('Deleting directory(ies):')
            for dir in wfilesDD:
                if rverbose==True and gui==False: print(f'  {dir}')
                if sync==True: os.rmdir(dDirectory+dir)
            #if rverbose==True: print (f'Directories deleted: {len(wfilesDD)}')
    
    if testdir==True:
        os.rmdir(dDirectory)
        if gui==False: print('Testing destination directory removed.\n')

    if 't' in args:
        if gui==False: print('\nTesting Mode. No Changes were committed.', end='')

    if rverbose==True and gui==False:
        if fsync==False:
            print (f'\n*** Completed {len(wfilesDD)+len(wfilesDF)+len(wfilesUF)+len(wfilesNF)+len(wfilesND)} file operations ***\n')
        else:
            print (f'\n*** Completed {len(wfilesDD)+len(wfilesDF)+len(wfilesND)} directory operations ***\n')
        if fsync==False: print (f'*** Total bytes synced: {transfersize:,}')
        if fsync==False: print (f'*** Total megabytes synced: {round(transfersize/1048576,2):,}\n')
    else:
        if fsync==False:
            if gui==False: print(f'*** {len(wfilesDD)+len(wfilesDF)+len(wfilesUF)+len(wfilesNF)+len(wfilesND)} Operation(s) Completed ***\n')
        else:
            if gui==False: print(f'*** {len(wfilesDD)+len(wfilesDF)+len(wfilesND)} Directory Operation(s) Completed ***\n')

#==============================================================================
if __name__=='__main__':

    clearscreen()
        
    if gui==False: print(f'\nPyJsync {ver} by Jarrett McAlicher')

    # *** SETUP ***
    if verbose==True: print(sys.argv)

    if len(sys.argv)==1: 
        printhelp()
        exit()
    
    if sys.argv[1][0]!='-':
        if gui==False: print('\nArgument must start with a \'-\' (Dash)')
        printhelp()
        exit()
    
    args=sys.argv[1]

    if 'h' in args:
        printhelp()
        exit()
    elif args=='--version':
        if gui==False: print(f'\nVersion {ver}\n')
        exit()

    if 's' in args:
        sync=True
    
    if 'y' in args:
        autoYes=True
    
    if "M" in args:
        sync=True
        autoYes=True
    
    if "t" in args:
        sync=False
        doCheckSum=False   
    
    if 'C' in args:
        copy=True
        sync=False
    
    # ====== Check Source and Destination Directories ========
    if len(sys.argv)==4:
        sDirectory=sys.argv[2]
        dDirectory=sys.argv[3]
    else:
        printhelp()
        exit()
    if verbose==True: print(sys.argv)

    if verbose==True: print(f'*** {sDirectory} and {dDirectory}')
    if os.path.exists(sDirectory)==False:
        if gui==False: print(f'\nERROR: Source directory does not exist\n - {sDirectory}\n')
        exit()
    
    if os.path.exists(dDirectory)==False:
        if autoYes==False:
            if gui==False: print(f'\nDestination directory "{dDirectory} does not exist.')
            answer=input('Would you like it to be created? (y/n):')
            if answer=='y':
                
                if sync==True:
                    if gui==False: print('Creating destination path . . . ',end='')
                    os.makedirs(dDirectory)
                    if gui==False: print('Directory created.\n')
                else:
                    if gui==False and testing==True: print('TESTING: Source Directory has been created and will be deleted when this test\nrun is complete.')
                    os.makedirs(dDirectory)
                    testdir=True
            else:
                if gui==False: print('Operation cancelled.\n')
                exit()
        else:
            if sync==True:
                if gui==False: print('Creating destination path . . . ',end='')
                os.makedirs(dDirectory)
                if gui==False: print('Directory created.\n')
            else:
                if gui==False and testing==True: print('TESTING: Source Directory has been created and will be deleted when this test\nrun is complete.')
                os.makedirs(dDirectory)
                testdir=True


    pyjsync(args, sDirectory, dDirectory)