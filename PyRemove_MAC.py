#PyRemove_MAC by Jarrett McAlicher
'''
This file is meant to be run as a stand alone utility OR a module for your Python Program.

This will remove __MACOSX folders

V1.0  Initial Release
'''

ver='1.0'
import sys
import shutil

verbose=False
remove=True



class mfiles():
    '''
    mfiles(directory)
    - directory is the root directory
    *** This always recurses the directory.

    Other methods:
    - checklist - Checks to see if the folder is in the list
    - checkqty - Returns the number of folders in the list to be removed
    - list - prints the folders to the console
    - remove - actually removes the objects from the file system.
    '''
    def __init__(self,directory):
        self.ufiles=['__MACOSX']
        import shutil
        import os
        
        self.directory=directory

        self.data=[]
        if verbose==True: print(f'*** {directory}')
        for path, subdirs, files in os.walk(directory,topdown=False):
            for name in subdirs:
                if verbose==True: print(path+name)
                if self.checklist(name)==True:
                    self.data.append(path+'/'+name)
    
    def checklist(self,folderName):
        '''checklist(folderName) Checks to see if the folder is in the remove list.'''
        check=False
        if folderName in self.ufiles:
            return True
        else: 
            return False  
        
    def checkqty(self):
        '''Returns the qty of folders in the list'''
        return len(self.data)

    def list(self):
        '''Prints the list to the console'''
        for dir in self.data:
            print(dir)  

    def remove(self):
        '''Removes the folders in the list.
        Returns 2 if no directory's to remove, 1 if ERROR and 0 if successful'''
        if len(self.data)==0: 
            print('No Directories to remove.')
            return 2
        

        for dir in self.data:
            if verbose==True: print (f'Removing Directory {dir}.') 
            try:
                shutil.rmtree(dir)
            except:
                print(f'ERROR: Error removing directory {dir}') 
                return 1 
        return 0
              

if __name__=="__main__":
    print(f'PyRemove_MAC by Jarrett McAlicher ver {ver}.')
    directory=sys.argv[1]
    if len(sys.argv)>2:
        remove=sys.argv[2]
        if remove=='False': remove=False
    
    testfiles=mfiles(directory)
    testfiles.list()
    print(testfiles.checkqty())
    if remove==True:
        testfiles.remove()
    
    