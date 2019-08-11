#!/usr/bin/python

import os
import shutil

# Global Variables
NEWFILENAME = '/home/jesse/2019_CMIYC/Street Hashes/01_2019-CMIYC-Street-Hashes.txt'
OLDFILENAME = '/home/jesse/2019_CMIYC/Street Hashes/2019-CMIYC-Street-Hashes.txt'
UPDATEFILEFOLDER = '/home/jesse/2019_CMIYC/Street Hashes/Updates'
OLDUPDATEFOLDER = '/home/jesse/2019_CMIYC/Street Hashes/Updates/Old'


def processupdatefolder(UpdateFolderName, OldFileName, NewFileName):
    print('Checking if the update folder exists.')

    if os.path.exists(UpdateFolderName) and os.path.isdir(UpdateFolderName):
        print('Folder exists.')

        items = os.listdir(UpdateFolderName)
        files = []

        for item in items:
            if os.path.isfile(os.path.join(UpdateFolderName, item)):
                files.append(os.path.join(UpdateFolderName, item))

        print('Found ({0}) files.'.format(len(files)))

        if len(files) > 0:
            processupdatefiles(files, OldFileName, NewFileName)

        else:
            print('No Files found!')

    else:
        print('Path does not exist or path is not a directory.')

    return


def processupdatefiles(UpdateFiles, OldFileName, NewFileName):
    print('Opening old file:  ' + OldFileName)

    with open(OldFileName, 'r') as ofn:
        print('Old file opened.')
        print('Opening new file:  ' + NewFileName)

        with open(NewFileName, 'w') as nfn:
            print('New file opened.')

            hashes = {}

            for line in ofn.readlines():
                user,hash = line.split(':')
                hashes[user] = hash

            UpdateFiles.sort(key=lambda x: os.path.getmtime(x))

            for file in UpdateFiles:
                if os.path.getsize(file) > 0:
                    print('Opening update file:  ' + file)

                    with open(file, 'r') as ufn:
                        print('Update file opened.')

                        for line in ufn.readlines():
                            if ':' in line:
                                user, hash = line.split(':')
                                hashes[user] = hash

                else:
                    print('Update file too small.')

                movefile(file.replace(os.path.basename(file), '')[:-1], OLDUPDATEFOLDER, os.path.basename(file))

            if len(hashes) > 0:
                lines = []
                for hash in hashes:
                    line = hash + ':' + hashes[hash]
                    lines.append(line)

                print('Line Count:  ' + str(len(lines)))
                #print(lines)

                for line in sorted(lines):
                    nfn.write(line)

            else:
                print('Combined hashes empty.')

    return


def movefile(CurrentLocation, NewLocation, Filename):
    print('Moving file :  ' + Filename)
    print('Old Location:  ' + CurrentLocation)
    print('New Location:  ' + NewLocation)
    shutil.move(os.path.join(CurrentLocation, Filename), os.path.join(NewLocation, Filename))
    print('Move completed.')

    return


def main():
    print('**********  Starting  **********')
    processupdatefolder(UPDATEFILEFOLDER, OLDFILENAME, NEWFILENAME)
    print('**********  Finished  **********')
    return

if __name__ == "__main__":
    main()