#!/usr/bin/python
from __future__ import print_function
import httplib2
import os
import io
import argparse
from apiclient import discovery, http
from oauth2client import file, client, tools
from oauth2client.file import Storage


# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = ''
APPLICATION_NAME = ''
TOKEN_SECRET_FILE = ''
TEMP_FOLDER = ''

# Setup parser
parser = argparse.ArgumentParser(description='Upload file to GDrive')

# Required positional argument
parser.add_argument('--File', type=str,
                    help='The fully qualified path to the file to action')
parser.add_argument('--Action', type=str,
                    help='The Action to take with the file.')
parser.add_argument('--Folder', type=str,
                    help='The folder to get a list of files from.')
# Read in arguments
ARGS = parser.parse_args()

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """

    store = Storage(TOKEN_SECRET_FILE)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)

    return credentials


def buildService():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    return discovery.build('drive', 'v3', http=http)


def readConfigFile(ConfigurationFile):
    retDic = {}
    try:
        #print('Reading configuration file.')
        #print('File:  ' + ConfigurationFile)
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
    global CLIENT_SECRET_FILE, APPLICATION_NAME, TOKEN_SECRET_FILE, TEMP_FOLDER

    for key in ConfigDictionary:
        if (key == 'APICred'):
            CLIENT_SECRET_FILE = ConfigDictionary['APICred']
        elif (key == 'APPName'):
            APPLICATION_NAME = ConfigDictionary['APPName']
        elif (key == 'APIToken'):
            TOKEN_SECRET_FILE = ConfigDictionary['APIToken']
        elif (key == 'TempFolder'):
            TEMP_FOLDER = ConfigDictionary['TempFolder']
    return


def countItems(service, Folder, IsFolder = False):
    """
       This will return the count of the files found unless IsFolder is true.
       You can specify a base folder to start in.
       You can specify if you only want a count of folders.
       service : This is the Google API object
       Folder  : This is the base folder to search in.
       IsFolder: This is to specify the count of folders and not files.
       Returns : An integer.
    """
    # Initialize the return value.
    retInt = 0
    # Get the list of files and folders.
    results = getItems(service)
    # Get the files dictionary from the array.
    items = results.get('files', [])
    # Test the dictionary to see if it is null.
    if not items:
        # No Files or Folders found!
        print('No files or folders found.')
    else:
        # Get Count of specified items.
        if (IsFolder):
            # Count only folders.
            print("Counting Folders.")
            retInt = countType("application/vnd.google-apps.folder", items, False)

        else:
            # Count only files.
            print("Counting Files.")
            retInt = countType("application/vnd.google-apps.folder", items, True)

    return retInt


def countType(mimeType, Items, IsNot = False):
    """
    Returns the count of items found.
    :param mimeType: The Google mimeType
    :param Items: The dictionary of items from the Google API.
    :param IsNot: If true counts all items that is not equal to the mimeType.
    :return: An integer.
    """
    retInt = 0
    for item in Items:
        if (not IsNot):
            # Count all items that are not of the supplied mimeType.
            if (item['mimeType'] == mimeType):
                retInt += 1
        else:
            # Count all items that are of the supplied mimeType.
            if (item['mimeType'] != mimeType):
                retInt += 1
    # Return the result.
    return retInt


def getItems(service):
    retObj = ''

    # Get the list of files and folders.
    retObj = service.files().list(pageSize=10,
                                   fields="nextPageToken, files(id, name, parents, properties, trashed, mimeType)"
                                   ).execute()
    # Return the object
    return retObj


def deleteFile(service, id):
    retObj = ''
    # Get the list of files and folders.
    retObj = service.files().list(pageSize=10,
                                  fields="nextPageToken, files(id, name, parents, properties, trashed, mimeType)"
                                  ).execute()
    return retObj


def moveFile(service, SourceFolder, TargetFolder, FileName):
    print("Moving file ({0}) from ({1}) to ({2})".format(FileName, SourceFolder, TargetFolder))
    fileID = getFileID(service, FileName)
    curParID = getFolderID(service, SourceFolder)
    newParID = getFolderID(service, TargetFolder)
    addParID = "'{0}'".format(newParID)
    remParID = "'{0}'".format(curParID)

    if not fileID:
        print("Failed to find the file ID for {0}".format(FileName))
    else:
        try:
            # Retrieve the existing parents to remove
            result = service.files().get(fileId=fileID,
                                             fields='parents').execute()
            previous_parents = ",".join(result.get('parents'))
            # Move the file to the new folder
            result = service.files().update(fileId=fileID,
                                                addParents=newParID,
                                                removeParents=previous_parents,
                                                fields='id, parents').execute()

        except Exception as error:
            print("An error has occured!")
            print(error)
            print("FileID ({0}) : Add Parents ({1}) : Remove Parents ({2})".format(fileID, addParID, remParID))
            # Get file details
            getFileDetails(service, FileName)
            # Get folder details
            getFolderDetails(service, SourceFolder)
            getFolderDetails(service, TargetFolder)

            exit(500)
    return


def uploadFile(service, Folder, FileName, mimeType):
    retObj = ''
    print("Uploading file ({0}) to ({1}) as ({2})".format(FileName, Folder, mimeType))

    if (os.path.exists(FileName)):
        try:
            # Get the ID of the folder.
            folderID = getFolderID(service, Folder)
            # Build the metadata for the file.
            body = {'name': os.path.split(FileName)[1], 'mimeType': mimeType, 'parents': [folderID]}
            # Upload the file and get the ID.
            results = service.files().create(body=body, media_body=FileName,
                                 supportsTeamDrives=True, fields='id').execute().get('id')

            print("File was successfully uploaded.  ID:  {0}".format(results))
        except Exception as error:
            print("An error has occured!")
            print(error)
            exit(409)
    else:
        print("File not found!  File:  {0}".format(FileName))

    return retObj


def getFile(service, FileName):
    retObj = ''
    fileId = getFileID(service, FileName)
    try:
        request = service.files().get_media(fileId=fileId)
        fh = io.BytesIO()
        downloader = http.MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))
        retObj = fh.getvalue()

    except Exception as error:
        print("An error has occured!")
        print(error)
        exit(409)

    return retObj

def listItems(service):
    results = getItems(service)
    items = results['files']
    if not items:
        print("No items found!")
    else:
        for item in items:
            for key in item:
                print("{0}: {1}".format(key, str(item[key])))

    return


def listFiles(service, Folder):
    retFiles = []

    # query = "trashed = False"
    # query = "name = '" + Folder + "'"
    query = "trashed = False and mimeType != 'application/vnd.google-apps.folder'"
    query += " and parents in '" + getFolderID(service, Folder) + "'"
    #print("Query:  " + query)
    results = service.files().list(pageSize=10, q=query,
                                   fields="nextPageToken, files(name)"
                                   ).execute()
    # Assign the dictionary entry of files to items.  Items is an array.
    items = results['files']

    # Check the array.
    if not items:
        print("No files found!")

    # Make returned array
    for item in items:
        retFiles.append(item['name'])

    return retFiles


def getFileID(service, FileName):
    retID = ""
    #query = "trashed = False"
    #query = "name = '" + Folder + "'"
    query = "trashed = False and mimeType != 'application/vnd.google-apps.folder'"
    query += " and name = '" + FileName + "'"
    #print("Query:  " + query)
    results = service.files().list(pageSize=10,q=query,
                                  fields="nextPageToken, files(id, name, parents, properties, trashed, mimeType)"
                                   ).execute()
    # Assign the dictionary entry of files to items.  Items is an array.
    items = results['files']

    # Check the array.
    if not items:
        print("No ")

    # Check the number of folders found.
    if (len(items) == 1):
        #print("Found 1 result!")
        result = items[0]
        if not result:
            print("Found result not found!")
        else:
            retID = result['id']
    elif (len(items) == 0):
        print("Found 0 results!")
    elif (len(items) >= 2):
        print("Found more than 1 result!")
        exit(500)

    return retID


def getFolderID(service, Folder):
    retID = ""
    #query = "trashed = False"
    #query = "name = '" + Folder + "'"
    query = "trashed = False and mimeType = 'application/vnd.google-apps.folder'"
    query += " and name = '" + Folder + "'"
    #print("Query:  " + query)
    results = service.files().list(pageSize=10,q=query,
                                  fields="nextPageToken, files(id, name, parents, properties, trashed, mimeType)"
                                   ).execute()
    # Assign the dictionary entry of files to items.  Items is an array.
    items = results['files']

    # Check the array.
    if not items:
        print("No ")

    # Check the number of folders found.
    if (len(items) == 1):
        #print("Found 1 result!")
        result = items[0]
        if not result:
            print("Found result not found!")
        else:
            retID = result['id']
    elif (len(items) == 0):
        print("Found 0 results!")
    elif (len(items) >= 2):
        print("Found more than 1 result!")
        exit(500)

    return retID


def getFileDetails(service, FileName):
    retResult = ''
    fileID = getFileID(service, FileName)
    result = service.files().get(fileId=fileID, fields='id,mimeType,name,parents,trashed').execute()
    #print(result)
    return retResult

def getFolderDetails(service, FolderName):
    retResult = ''
    fileID = getFolderID(service, FolderName)
    result = service.files().get(fileId=fileID, fields='id,mimeType,name,parents,trashed').execute()
    #print(result)
    return retResult


def main():
    retObj = None
    # This is the file that holds the configuration settings.
    dicConfig = readConfigFile('/Temp/GDrive.config')

    # Set global variables with the dictionary returned.
    setParameters(dicConfig)

    # Set local variables
    SourceFolder = dicConfig['SourceFolder']
    TargetFolder = dicConfig['TargetFolder']
    TempPath = dicConfig['TempFolder']
    mimeType = dicConfig['mimeType']

    ## Get the credential and build the service.
    service = buildService()

    # Assign arguments
    Action = ARGS.Action
    File = ARGS.File
    Folder = ARGS.Folder

    # Take action
    if (Action.lower() == "upload"):
        # Upload file
        retObj = uploadFile(service, SourceFolder, File, mimeType)

    elif (Action.lower() == "download" or Action.lower() == "get"):
        # Get file
        PathFile = os.path.join(Folder, File)
        if (len(File.split('/')) > 1):
            file = getFile(service, os.path.split(File)[1])
        else:
            file = getFile(service, File)
        try:
            f = open(PathFile, 'w')

            f.writelines(file)
            retObj = PathFile
        except Exception as error:
            print("An error has occured!")
            print(error)

    elif (Action.lower() == "move"):
        # Move file
        retObj = moveFile(service, SourceFolder, TargetFolder, os.path.split(File)[1])

    elif (Action.lower() == "list"):
        # Move file
        retObj = listFiles(service, Folder)

    #print("Returning:  " + str(retObj))
    return retObj

if __name__ == '__main__':
    main()