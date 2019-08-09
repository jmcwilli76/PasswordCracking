#!/usr/bin/python

import os
import io
import httplib2
from apiclient import discovery, http
from oauth2client import file, client, tools
from oauth2client.file import Storage


"""
    This script will make accessing the GDrive easier
"""



class GDrive:
    # Class Variables
    APPNAME = ''
    APPTOKEN = ''
    APPCRED = ''
    APPSCOPE = ''
    # Declare the class with the required authentication attributes
    def __init__ (self, APPName, APIToken, APICred, APPScope):
        self.APPNAME = APPName
        self.APPTOKEN = APIToken
        self.APPCRED = APICred
        self.APPSCOPE = APPScope
        return

    def get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        # If the token has expired just delete it for the Drive and GMail.
        # It will then be recreated.  A link will be generated or a web page will
        # be opened that you will need to login and grant access to this application.

        store = Storage(self.APPTOKEN)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.APPCRED, self.APPSCOPE)
            flow.user_agent = self.APPNAME
            credentials = tools.run_flow(flow, store)

        return credentials

    def buildService(self):
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        return discovery.build('drive', 'v3', http=http)


    def countItems(self, service, Folder, IsFolder=False):
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
        results = self.getItems(service)
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
                retInt = self.countType("application/vnd.google-apps.folder", items, False)

            else:
                # Count only files.
                print("Counting Files.")
                retInt = self.countType("application/vnd.google-apps.folder", items, True)

        return retInt


    def countType(self, mimeType, Items, IsNot=False):
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


    def getItems(self, service):
        retObj = ''

        # Get the list of files and folders.
        retObj = service.files().list(pageSize=10,
                                      fields="nextPageToken, files(id, name, parents, properties, trashed, mimeType)"
                                      ).execute()
        # Return the object
        return retObj


    def deleteFile(self, service, id):
        retObj = ''
        # Get the list of files and folders.
        retObj = service.files().list(pageSize=10,
                                      fields="nextPageToken, files(id, name, parents, properties, trashed, mimeType)"
                                      ).execute()
        return retObj


    def moveFile(self, service, SourceFolder, TargetFolder, FileName):
        print("Moving file ({0}) from ({1}) to ({2})".format(FileName, SourceFolder, TargetFolder))
        fileID = self.getFileID(service, FileName)
        curParID = self.getFolderID(service, SourceFolder)
        newParID = self.getFolderID(service, TargetFolder)
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
                self.getFileDetails(service, FileName)
                # Get folder details
                self.getFolderDetails(service, SourceFolder)
                self.getFolderDetails(service, TargetFolder)

                exit(500)
        return


    def uploadFile(self, service, Folder, FileName, mimeType):
        retObj = ''
        print("Uploading file ({0}) to ({1}) as ({2})".format(FileName, Folder, mimeType))

        if (os.path.exists(FileName)):
            try:
                # Get the ID of the folder.
                folderID = self.getFolderID(service, Folder)
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


    def getFile(self, service, FileName):
        retObj = ''
        fileId = self.getFileID(service, FileName)
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


    def listItems(self, service):
        results = self.getItems(service)
        items = results['files']
        if not items:
            print("No items found!")
        else:
            for item in items:
                for key in item:
                    print("{0}: {1}".format(key, str(item[key])))

        return


    def listFiles(self, service, Folder):
        retFiles = []

        # query = "trashed = False"
        # query = "name = '" + Folder + "'"
        query = "trashed = False and mimeType != 'application/vnd.google-apps.folder'"
        query += " and parents in '" + self.getFolderID(service, Folder) + "'"
        # print("Query:  " + query)
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


    def getFileID(self, service, FileName):
        retID = ""
        # query = "trashed = False"
        # query = "name = '" + Folder + "'"
        query = "trashed = False and mimeType != 'application/vnd.google-apps.folder'"
        query += " and name = '" + FileName + "'"
        # print("Query:  " + query)
        results = service.files().list(pageSize=10, q=query,
                                       fields="nextPageToken, files(id, name, parents, properties, trashed, mimeType)"
                                       ).execute()
        # Assign the dictionary entry of files to items.  Items is an array.
        items = results['files']

        # Check the array.
        if not items:
            print("No ")

        # Check the number of folders found.
        if (len(items) == 1):
            # print("Found 1 result!")
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


    def getFolderID(self, service, Folder):
        retID = ""
        # query = "trashed = False"
        # query = "name = '" + Folder + "'"
        query = "trashed = False and mimeType = 'application/vnd.google-apps.folder'"
        query += " and name = '" + Folder + "'"
        # print("Query:  " + query)
        results = service.files().list(pageSize=10, q=query,
                                       fields="nextPageToken, files(id, name, parents, properties, trashed, mimeType)"
                                       ).execute()
        # Assign the dictionary entry of files to items.  Items is an array.
        items = results['files']

        # Check the array.
        if not items:
            print("No ")

        # Check the number of folders found.
        if (len(items) == 1):
            # print("Found 1 result!")
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


    def getFileDetails(self, service, FileName):
        retResult = ''
        fileID = self.getFileID(service, FileName)
        result = service.files().get(fileId=fileID, fields='id,mimeType,name,parents,trashed').execute()
        # print(result)
        return retResult


    def getFolderDetails(self, service, FolderName):
        retResult = ''
        fileID = self.getFolderID(service, FolderName)
        result = service.files().get(fileId=fileID, fields='id,mimeType,name,parents,trashed').execute()
        # print(result)
        return retResult


def main():
    return

if __name__ == '__main__':
    main()