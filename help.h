********** Help File **********
    --Three(3) parameters are required:
      PyJsync.py -arguments "Source Folder" "Destination Folder"

    --Action Arguments: 1 is required
         -s do the (S)ync. This checks to see if size and date are different
            default is sync to destination and only checks if the file size and
            date are different (does not compare if date is newer/older)
            by defult this does not recurse sub directories.
         -t (T)est do not sync, this overrides the -s and will not perform the.
            actual sync, but uses all other arguments to "test" the outcome.
         -f Replicate (F)older structure. Respects additional arguments (-vdry)  
            cancels -s (sync) for files. Without -r not much will happen except  
            creating the initial destination directory if it does not exist  
         -M Uses a (M)acro file M.m with a single line file with the arguments
            to set as defaults. The dash - is not required in the file

    --Additional Arguments. These can be added to the above action arguments.      
         -v (v)erbose listing is displayed
         -d (D)o not (D)elete files or folders in destination if not in source 
         -r (R)ecurse sub directories 
         -c (C)heck with MD5 Hash after file has been copied. Will provide error
            if file does not match. Not this could significantly slow operation.
         -y Automatically input (Y)es to create root directory if it does not exist.
         -x Remove __MACOS(X) files from source before sync

    --These arguments can not be mixed
         --help    Prints this help file
         -h        This help file is displayed (is ignored if mixed)
         --version Prints the Version number.

    NOTES: If Source Directory does not exist, Program will terminate.
           If Destination directory does not exist, user will be prompted to create directory.
           This is over ridden with the -y argument.