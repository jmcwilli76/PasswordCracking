#!/usr/bin/python

import os
import sys
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
MIMETYPE = ''
APISCOPES = 'https://www.googleapis.com/auth/drive'


def readConfigFile(ConfigurationFile):
    retDic = {}
    try:
        print('Reading configuration from file.')
        print('File:  ' + ConfigurationFile)
        with open(ConfigurationFile, 'r') as CF:
            #print('Opened file for reading.  Reading lines.')
            for line in CF.readlines():
                #print('Reding Line.')
                #print('Line:  ' + str(line))
                line = line.strip('\n')
                if line != '':
                    key, value = line.split('=')
                    retDic[key] = value

    except:
        print('Failed to read the configuration file.')
        print('File:  ' + ConfigurationFile)
        exit(100)

    return retDic


def setParameters(ConfigDictionary):
    global SOURCEFOLDER, SOURCEFILE, TARGETFOLDER, TARGETFILE, APITOKEN, APICRED, APIAPPNAME, MIMETYPE

    for key in ConfigDictionary:
        if (key == 'SourceFolder'):
            SOURCEFOLDER = ConfigDictionary['SourceFolder']

        elif (key == 'SourceFile'):
            SOURCEFILE = ConfigDictionary['SourceFile']

        elif (key == 'TargetFolder'):
            TARGETFOLDER = ConfigDictionary['TargetFolder']

        elif (key == 'TargetFile'):
            TARGETFILE = ConfigDictionary['TargetFile']

        elif (key == 'APIToken'):
            APITOKEN = ConfigDictionary['APIToken']

        elif (key == 'APICred'):
            APICRED = ConfigDictionary['APICred']

        elif (key == 'APPName'):
            APIAPPNAME = ConfigDictionary['APPName']

        elif (key == 'mimeType'):
            MIMETYPE = ConfigDictionary['mimeType']

    if SOURCEFOLDER == '' or SOURCEFILE == '' or TARGETFOLDER == '' or TARGETFILE == '' or APITOKEN == ''\
            or APICRED == '' or APIAPPNAME == '' or MIMETYPE == '':
        print('Missing configuration variables!')
        exit(200)

    return


def startProcess(ConfigFile):
    print('********************  Starting  ********************')

    # This is the file that holds the configuration settings.
    dicConfig = readConfigFile(ConfigFile)

    # Set global variables with the dictionary returned.
    setParameters(dicConfig)

    # Check for source file.
    print('Checking if the source file exists.')
    print('File:  ' + str(os.path.join(SOURCEFOLDER, SOURCEFILE)))

    if os.path.isfile(os.path.join(SOURCEFOLDER, SOURCEFILE)):
        # Remove system argument
        if len(sys.argv) > 1:
            sys.argv.pop(1)

        # Create GDrive object
        print('Building GDrive object.')
        gdrive = GDriveAPI.GDrive(APPName=APIAPPNAME, APPScope=APISCOPES, APIToken=APITOKEN, APICred=APICRED)

        print('Uploading file.')
        result = gdrive.uploadFile(os.path.join(SOURCEFOLDER, SOURCEFILE), TARGETFOLDER, TARGETFILE, MIMETYPE)
        print('Upload Result:  ')
        print(result)


    else:
        print('No source file found!  ' + str(os.path.join(SOURCEFOLDER, SOURCEFILE)))

    print('********************  Starting  ********************')


def main():
    if len(sys.argv) > 1:
        startProcess(sys.argv[1])

    else:
        startProcess('/Temp/CrackUpload.config')
    return

if __name__ == '__main__':
    main()