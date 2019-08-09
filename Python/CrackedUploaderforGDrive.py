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
MIMETYPE = ''
APISCOPES = 'https://www.googleapis.com/auth/drive'


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

    return


def startProcess():
    print('********************  Starting  ********************')

    # This is the file that holds the configuration settings.
    print('Reading Configuration File.')
    dicConfig = readConfigFile('/Temp/EmailConfig.config')

    # Set global variables with the dictionary returned.
    setParameters(dicConfig)

    # Check for source file.
    print('Checking if the source file exists.')
    print('File:  ' + str(os.path.join(SOURCEFOLDER, SOURCEFILE)))

    if os.path.isfile(os.path.join(SOURCEFOLDER, SOURCEFILE)):
        # Create GDrive object
        print('Building GDrive object.')
        gdrive = GDriveAPI.GDrive(APPName=APIAPPNAME, APPScope=APISCOPES, APIToken=APITOKEN, APICred=APICRED)

        print('Uploading file.')
        result = gdrive.uploadFile(TARGETFOLDER, TARGETFILE, MIMETYPE)
        print('Upload Result:  ')
        print(result)


    else:
        print('No source file found!  ' + str(os.path.join(SOURCEFOLDER, SOURCEFILE)))

    print('********************  Starting  ********************')


def main():
    return

if __name__ == '__main__':
    main()