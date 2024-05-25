## PyJsyncGUI is a front end GUI for PyJsync and will be kept in sync with it's updates.
## 

ver='v1.0a'
psver='1.8.1'

import PyJsync as pj
if pj.ver!=psver:
    print('PyJsyncGUI is not campatible with the version of PyJsync')
    exit()

import tkinter as tk 
from tkinter import filedialog
import PyRemove_MAC as prMAC
import PyJsync as pjs
from cnfg import *

class dialog():
    def __init__(self,dtitle,dmessage):
        self.dbox=tk.Tk()
        self.dbox.title(dtitle)
        tk.Label(master=self.dbox,text=dmessage,padx=10,pady=10).grid(row=1,column=1)
        tk.Button(master=self.dbox, text='OK',command=self.closediag).grid(row=2,column=1)
        self.dbox.mainloop()

    def closediag(self):
        self.dbox.destroy()


class mainwindow():
    def __init__(self):
        ## Main Window
        self.window=tk.Tk()
        self.window.title(f'PyJsyncGUI ver {ver} for PyJsync {pj.ver}')

        #Initialize variables to StringVar() ** Requirement for Tkinter
        self.cb_sync=tk.StringVar()
        self.source_text=tk.StringVar()
        self.source_folder=tk.StringVar()
        self.dest_text=tk.StringVar()
        self.dest_folder=tk.StringVar()

        #Menu Bar
        self.menubar = tk.Menu(self.window)
        self.window['menu'] = self.menubar

        self.menu_file=tk.Menu(self.menubar,tearoff=0)
        self.menubar.add_cascade(menu=self.menu_file,label='File')
        self.menu_file.add_command(label='Exit',command=self.exitProgram)

        self.menu_utility = tk.Menu(self.menubar,tearoff=0)
        self.menubar.add_cascade(menu=self.menu_utility, label='Utility')
        self.menu_utility.add_command(label='Remove __OSXMAC in Source', command=self.removeMACs)
        self.menu_utility.add_command(label='Remove __OSXMAC in Destination', command=self.removeMACd)


        self.menu_help = tk.Menu(self.menubar,tearoff=0)
        self.menubar.add_cascade(menu=self.menu_help, label='Help')
        self.menu_help.add_command(label='Help',command=self.help)
        self.menu_help.add_command(label='About', command=self.about)

        #Content of the window

        self.content=tk.Frame(self.window)
        self.source_button=tk.Button(text="Source Folder",command=self.browse_source).grid(row=1,column=1)
        self.source_text=tk.Entry(master=self.window,textvariable=self.source_folder,width=50).grid(row=1,column=2,columnspan=4)

        self.dest_button=tk.Button(text='Destination Folder',command=self.browse_dest).grid(row=2,column=1)
        self.dest_text=tk.Entry(master=self.window, textvariable=self.dest_folder,width=50).grid(row=2,column=2,columnspan=4)

        tk.Label(text='Action Arguments:').grid(row=4,column=1,sticky='w')

        self.sync=tk.StringVar()
        self.cb_sync=tk.Radiobutton(text='Sync',value='sync',variable=self.sync).grid(row=5,column=2, sticky='w')
        self.cb_replicate=tk.Radiobutton(text='Copy',value='copy',variable=self.sync).grid(row=5, column=3, sticky='w')
        self.cb_test=tk.Radiobutton(text='Test',value='test',variable=self.sync).grid(row=5, column=4, sticky='w')

        tk.Label(text='Action Modifiers:').grid(row=6,column=1,sticky='w')

        self.recurse=tk.StringVar()
        self.cb_recurse=tk.Checkbutton(text='Recurse',variable=self.recurse).grid(row=7,column=2,sticky='w')
        self.dndelete=tk.StringVar()
        self.cb_dndelete=tk.Checkbutton(text='Do Not Delete',variable=self.dndelete).grid(row=7,column=3,sticky='w')
        self.chksum=tk.StringVar()
        self.cb_chksum=tk.Checkbutton(text='Checksum',variable=self.chksum).grid(row=7,column=4,sticky='w')
        self.delosx=tk.StringVar()
        self.cb_delosx=tk.Checkbutton(text='Del __OSXMAC',variable=self.delosx).grid(row=8,column=2,sticky='w')

        self.ok_button=tk.Button(text='Do Sync',command=self.dosync).grid(row=10,column=2)
        self.cancel_button=tk.Button(text='Cancel / Close',command=self.exitProgram).grid(row=10,column=3)

        self.window.mainloop()

    # functions for GUI commands
    def about(self):
        dialog('About...',f'PyJsyncGui {ver} by Jarrett McAlicher.\n\nFrontend for PyJsync v{psver}.')

    def removeMACf(self,cmdtxt,folder):
        self.files=prMAC.mfiles(folder)
        results=self.files.remove()
        if results==0:
            dialog('Completed',f'Removed __MACOSX files from the {cmdtxt} folder')
        elif results==2:
            dialog('Completed',f'Completed. No Folders found in the {cmdtxt} to be removed.')
        else:
            dialog('Error!','There was an error while deleting folders in the {cmdtxt} folders.')
    
    def removeMACs(self):
        if verbose==True: print(self.source_folder.get())
        self.removeMACf('source',self.source_folder.get())


    def removeMACd(self):
        self.removeMACf('destination',self.dest_folder.get())

    def exitProgram(self):
        self.window.destroy()
        exit()

    def help(self):
        print('help')

    def browse_source(self):
        self.source = filedialog.askdirectory()
        self.source_folder.set(self.source)
        self.window.update()
        
    def browse_dest(self):
        self.dest = filedialog.askdirectory()
        self.dest_folder.set(self.dest)
        self.window.update()

    def dosync(self):
        args='-yg' #g for GUI and y to automatically create directories.
        command=self.sync.get()
        if command=='sync':
            args=args+'s'
        elif command=='test':
            args=args+'t'
        elif command=='copy':
            args=args+'C'
        else:
            dialog('Error...','Must specify 1 Action Argument')
            return
        
        if self.recurse.get()=='1':
            args=args+'r'
        if self.dndelete.get()=='1':
            args=args+'d'
        if self.chksum.get()=='1':
            args=args+'c'
        if self.delosx.get()=='1':
            args=args+'x'
        if cverbose==True: print (args)
        
        sDirectory=self.source_folder.get()
        dDirectory=self.dest_folder.get()

        if sDirectory=='' or dDirectory=='':
            dialog('Error..','Must specify a Source and Destination Folder')
            return
        if sDirectory==dDirectory:
            dialog('Error...','Source Folder and  Destination Folder must be different')
            return
        
        if cverbose==True: print(sDirectory)
        if cverbose==True: print(dDirectory)

        #These are the variables to pass to PyJsync
        global gui
        gui=True
        ''' 
        --Other Variables from above
        args
        sDirectory
        dDirectory
        '''
        
        if testing==False:
            print (f'gui {gui}')
            printsettings()
            pjs.pyjsync(args,sDirectory,dDirectory)


if __name__=='__main__':
    
    mainwindow()
    


