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
gui=False
testing=False

def printsettings():
    print (f'gui: {gui}')
    print (f'testing: {testing}')
    print (f'remove_MAC: {remove_MAC}')
    print (f'fsync: {fsync}')
    print (f'recurse: {recurse}')
    print (f'destdir: {testdir}')
    
