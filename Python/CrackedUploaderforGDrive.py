#!/usr/bin/python

import os
import GDriveAPI


"""
    This script will look at the configured folder and upload the file
    specified to a GDrive folder.
"""

# Global Variables
SOURCEFOLDER = ''
SOURCEFILE = ''
TARGETFOLDER = ''
TARGETFILE = ''
APITOKEN = ''
APICRED = ''
APIAPPNAME = ''


def readConfigFile(ConfigurationFile):
    retDic = {}
    try:
        print('Reading configuration file.')
        print('File:  ' + ConfigurationFile)
        with open(ConfigurationFile, 'r') as CF:
            for line in CF.readlines():
                line = line.strip('\n')
                key, value = line.split('=')
                retDic[key] = value

    except:
        print('Failed to read the configuration file.')
        print('File:  ' + ConfigurationFile)
        exit(100)

    return retDic


def setParameters(ConfigDictionary):
    global SOURCEFOLDER, SOURCEFILE, TARGETFOLDER, TARGETFILE, APITOKEN, APICRED, APIAPPNAME

    for key in ConfigDictionary:
        if (key == 'GNUPGHome'):
            GNUPGHOME = ConfigDictionary['GNUPGHome']
        elif (key == 'Sender'):
            SENDERADDRESS = ConfigDictionary['Sender']
        elif (key == 'SignFingerprint'):
            SIGNFINGERPRINT = ConfigDictionary['SignFingerprint']

    return


def startProcess():
    # This is the file that holds the configuration settings.
    dicConfig = readConfigFile('/Temp/EmailConfig.config')

    # Set global variables with the dictionary returned.
    setParameters(dicConfig)

    FileName = ''
    TempFolder = dicConfig['TempFolder']
    ConsolidationFile = dicConfig['ConsolidatedFile']
    FileToUpload = dicConfig['FileToUpload']

    # Get the files waiting to be processed
    print("Get awaiting files.")
    GDrive.ARGS.Action = 'List'
    GDrive.ARGS.Folder = dicConfig['GDriveSource']
    files = GDrive.main()
    if (len(files) > 0):
        for file in files:
            # Loop through the files.
            print("Downloading file:  " + file)
            GDrive.ARGS.Action = 'Download'
            GDrive.ARGS.File = file
            GDrive.ARGS.Folder = TempFolder
            result = GDrive.main()
            print("Downloaded file to:  " + str(result))

            # Move the downloaded file on the GDrive.
            print("Moving file between GDrive folders.")
            GDrive.ARGS.Action = 'Move'
            GDrive.ARGS.File = file
            result = GDrive.main()
            print("Finished moving file.")


def main():
    return

if __name__ == '__main__':
    main()