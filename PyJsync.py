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

'''
FUTURE ENHANCEMENT:
-m (m)ove (instead of sync) - probably not implement because then it is no longer a SYNC :)

-

'''

ver='1.6'

import os
#from os import.system, name
import shutil
#import fnmatch # to be implemented later for filename matching.
import hashlib
from stat import ST_SIZE
import sys
import PyRemove_MAC

verbose = False
cverbose = True
rverbose = False #Runtime verbose
filesize=0.00
transfersize=0.00
recurse=False
doCheckSum=False
testdir=False
fsync=False
autoYes=False
remove_MAC=False

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
    print('\n********** Help File **********\n')
    print('--Three(3) parameters are required:')
    print('  PyJsync.py -arguments "Source Folder" "Destination Folder"\n')
    print('--Action Arguments: 1 is required')
    print('     -s do the (S)ync. This checks to see if size and date are different')
    print('        default is sync to destination and only checks if the file size and')
    print('        date are different (does not compare if date is newer/older)')
    print('        by defult this does not recurse sub directories.')
    print('     -t (T)est do not sync, this overrides the -s and will not perform the.')
    print('        actual sync, but uses all other arguments to "test" the outcome.\n')  
    print('     -f Replicate (F)older structure. Respects additional arguments (-vdry)')   
    print('        cancels -s (sync) for files. Without -r not much will happen except')  
    print('        creating the initial destination directory if it doesn\'t exist')  
    print('     -M Uses a (M)acro file M.m with a single line file with the arguments')
    print('        to set as defaults. The dash - is not required in the file')
    print('--Additional Arguments. These can be added to the above action arguments.')      
    print('     -v (v)erbose listing is displayed')
    print('     -d (D)o not Delete files or folders in destination if not in source') 
    print('     -r (R)ecurse sub directories') 
    print('     -c (C)heck with MD5 Hash after file has been copied. Will provide error')
    print('        if file does not match. Not this could significantly slow operation.')
    print('     -y Automatically input (Y)es to create root directory if it does not exist.')
    print('     -x Remove __MACOS(X) files from source before sync')
    print('\n--These arguments can not be mixed')
    print('     --help    Prints this help file')
    print('     -h        This help file is displayed (is ignored if mixed)')
    print('     --version Prints the Version number.')
    print('\nNOTES: If Source Directory doesn\'t exist, Program will terminate.')
    print('       If Destination directory doesn\'t exist, user will be prompted to\n       create directory.')
    print('       This is over ridden with the -y argument.')
    print('\n')

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
    

if __name__=='__main__':
    
    clearscreen()
        
    print(f'\nPyJsync {ver} by Jarrett McAlicher')

    # *** SETUP ***
    if verbose==True: print(sys.argv)

    if len(sys.argv)==1: 
        printhelp()
        exit()
    
    if sys.argv[1][0]!='-':
        print('\nArgument must start with a \'-\' (Dash)')
        printhelp()
        exit()
    
    args=sys.argv[1]

    if 'h' in args:
        printhelp()
        exit()
    elif args=='--version':
        print(f'\nVersion {ver}\n')
        exit()

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
    
    if len(sys.argv)==4:
        sDirectory=sys.argv[2]
        dDirectory=sys.argv[3]
    if verbose==True: print(sys.argv)

    if 'v' in args:
        rverbose=True
    
    if 'c' in args:
        doCheckSum=True

    if 't' in args:
        print('Testing Mode. No Changes will be committed.')
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

    # ====== Check Source and Destination Directories ========
    if verbose==True: print(f'*** {sDirectory} and {dDirectory}')
    if os.path.exists(sDirectory)==False:
        print(f'\nERROR: Source directory does not exist\n - {sDirectory}\n')
        exit()
    
    if os.path.exists(dDirectory)==False:
        if autoYes==False:
            print(f'\nDestination directory "{dDirectory} does not exist.')
            answer=input('Would you like it to be created? (y/n):')
            if answer=='y':
                
                if sync==True:
                    print('Creating destination path . . . ',end='')
                    os.makedirs(dDirectory)
                    print('Directory created.\n')
                else:
                    print('TESTING: Source Directory has been created and will be deleted when this test\nrun is complete.')
                    os.makedirs(dDirectory)
                    testdir=True
            else:
                print('Operation cancelled.\n')
                exit()
        else:
            if sync==True:
                print('Creating destination path . . . ',end='')
                os.makedirs(dDirectory)
                print('Directory created.\n')
            else:
                print('TESTING: Source Directory has been created and will be deleted when this test\nrun is complete.')
                os.makedirs(dDirectory)
                testdir=True




    # ====== Main Part of Program =========
    
    if remove_MAC==True:
        print('Removing _MACOSX Folders.')
        mfiles=PyRemove_MAC.mfiles(sDirectory)
        if mfiles.checkqty()>0 and sync==True:
            mfiles.remove()

    if rverbose==True: print(f'\nScanning Source...',end=' ')
    sfiles=directoryandfiles(sDirectory,recurse) #Source Directory and Files
    
    if verbose==True: print(sfiles.data)
    if rverbose==True: print(f'Scanning Destination ...',end=' ')
    
    dfiles=directoryandfiles(dDirectory,recurse) #Destination Directory and Files
    if verbose==True: print(getmatchstatus(sfiles.data,dfiles.data))
    if rverbose==True: print(f'Building Differences ...')
    
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
            
            if getifdiff(sfile,dfile)==True:
                if verbose==True: print(f'{dfile} matches size/date .. Skipping')
            
            else:
                if verbose==True: print(f'{dfile} needs updated')
                wfilesUF.append(status[2:])
    
    if 'd' in args:
        if rverbose==True: print('Not deleting files from destination that do not exist in source via -d switch')
    else:
        for status in statuses[2]: #Items are NOT not in the Source
            if status[0]=="D":
                wfilesDD.append(status[2:])
            else:
                wfilesDF.append(status[2:])
    


    # ===== This Part actually does the work.

    if len(wfilesND)>0:
        if rverbose==True: print('Creating directory(ies):')
        for dir in wfilesND:
            if rverbose==True: print (f'  {dir}')
            try:
                if sync==True: os.makedirs(dDirectory+dir)
            except FileExistsError:
                print(f'{dir} already exists. Skipping.')

        #if rverbose==True: print (f'Directories created: {len(wfilesND)}')

    if len(wfilesNF)>0:
        if fsync==False:
            if rverbose==True: print ('Creating file(s):')
            for file in wfilesNF:
                file_stats=os.stat(sDirectory+file)
                filesize=file_stats.st_size
                transfersize+=filesize
                if rverbose==True: print(f'  {file} in {filesize} bytes')
                if sync==True and fsync==False: shutil.copy2(f'{sDirectory}{file}',f'{dDirectory}{file}')
                if doCheckSum==True:
                    if gethash(sDirectory+file)!=gethash(dDirectory+file):
                        print (f'ERROR: {dfile} does not match source after copy!!!')
                        if cverbose==True: print (f'Source File: {sfile} {gethash(sfile)}\nDestination File: {dfile} {gethash(dfile)}')
                    print ('Checksum on copy (new) matches')
        #if rverbose==True: print (f'Files created: {len(wfilesNF)}')

    if len(wfilesUF)>0:
        if fsync==False:
            if rverbose==True: print('Updating file(s):')
            for file in wfilesUF:
                file_stats=os.stat(sDirectory+file)
                filesize=file_stats.st_size
                transfersize+=filesize
                if rverbose==True: print(f'  {file} with {filesize} bytes')
                if sync==True: os.remove(dDirectory+file)
                if sync==True: shutil.copy2(f'{sDirectory}{file}',f'{dDirectory}{file}')
                if doCheckSum==True:
                    if gethash(sfile)!=gethash(dfile):
                        print (f'ERROR: {dfile} does not match source after copy!!!')
                        if cverbose==True: print (f'Source File: {sfile} {gethash(sfile)}\nDestination File: {dfile} {gethash(dfile)}')
                    print ('Checksum on update matches')
        #if rverbose==True: print (f'Files updated: {len(wfilesUF)}')

    if len(wfilesDF)>0:
        if rverbose==True: print('Deleting file(s):')
        for file in wfilesDF:
            if rverbose==True: print(f'  {file}')
            if sync==True: os.remove(dDirectory+file)
        #if rverbose==True: print (f'Files Deleted:  {len(wfilesDF)}')
    
    if len(wfilesDD)>0:
        if rverbose==True: print ('Deleting directory(ies):')
        for dir in wfilesDD:
            if rverbose==True: print(f'  {dir}')
            if sync==True: os.rmdir(dDirectory+dir)
        #if rverbose==True: print (f'Directories deleted: {len(wfilesDD)}')
    
    if testdir==True:
        os.rmdir(dDirectory)
        print('Testing destination directory removed.\n')

    if 't' in args:
        print('\nTesting Mode. No Changes were committed.', end='')

    if rverbose==True:
        if fsync==False:
            print (f'\n*** Completed {len(wfilesDD)+len(wfilesDF)+len(wfilesUF)+len(wfilesNF)+len(wfilesND)} file operations ***')
        else:
            print (f'\n*** Completed {len(wfilesDD)+len(wfilesDF)+len(wfilesND)} directory operations ***')
        if fsync==False: print (f'*** Total bytes synced: {transfersize:,}')
        if fsync==False: print (f'*** Total megabytes synced: {round(transfersize/1048576,2):,}')
    else:
        if fsync==False:
            print(f'*** {len(wfilesDD)+len(wfilesDF)+len(wfilesUF)+len(wfilesNF)+len(wfilesND)} Operation(s) Completed ***')
        else:
            print(f'*** {len(wfilesDD)+len(wfilesDF)+len(wfilesND)} Directory Operation(s) Completed ***')