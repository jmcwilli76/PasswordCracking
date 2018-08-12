#!/usr/bin/Python

import gnupg
import GMailAPI
import os
import GDrive

GNUPGHOME = ''
SENDERADDRESS = ''
SIGNFINGERPRINT = ''

def encryptData(TargetFile, Recipient, SignAlso = True, SignerPassPhrase = ''):
    gpg = gnupg.GPG(gnupghome=GNUPGHOME)

    stream = ""

    with open(TargetFile, 'rb') as data:
        text = data.read()
        if(SignAlso):
            stream = gpg.encrypt(text, Recipient, always_trust=True, sign=SIGNFINGERPRINT, passphrase=SignerPassPhrase)
        else:
            stream = gpg.encrypt(text, Recipient, always_trust=True)

    return stream

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
    global GNUPGHOME, SENDERADDRESS, SIGNFINGERPRINT

    for key in ConfigDictionary:
        if (key == 'GNUPGHome'):
            GNUPGHOME = ConfigDictionary['GNUPGHome']
        elif (key == 'Sender'):
            SENDERADDRESS = ConfigDictionary['Sender']
        elif (key == 'SignFingerprint'):
            SIGNFINGERPRINT = ConfigDictionary['SignFingerprint']

    return

def getSingerPhrase(File):
    retString = ''
    try:
        with open(File, 'r') as f:
            retString = f.readline()
    except:
        print('Failed to read the signing phrase!')
        exit(200)

    return retString


def processFile(dicConfig, FileName):
    # Assign variables from configuration dictionary.
    subject = dicConfig['Subject']
    recipient = dicConfig['To']
    TempFolder = dicConfig['TempFolder']
    TempFile = dicConfig['TempFile']
    SignerPassPhrase = dicConfig['SignerPhraseFile']
    Scopes = dicConfig['Scopes']

    # Build the GMail object
    GMAIL = GMailAPI.GMailAPI(SENDERADDRESS, dicConfig['APIToken'], dicConfig['APICred'], Scopes)

    # Build qualified file
    if (len(FileName.split('/')) > 1):
        TARGET = FileName
    else:
        TARGET = os.path.join(TempFolder, FileName)

    # Encrypt the file.
    encrypted_data = encryptData(TARGET, recipient, True, getSingerPhrase(SignerPassPhrase))

    # Save the encrypted file.
    saveFile = open(TempFile, 'w')
    saveFile.write(str(encrypted_data))
    saveFile.close()

    # Print all
    ipa = False
    if (GNUPGHOME == ''):
        ipa = True
    if (SENDERADDRESS == ''):
        ipa = True
    if (SIGNFINGERPRINT == ''):
        ipa = True
    if (recipient == ''):
        ipa = True
    if (subject == ''):
        ipa = True
    if (TempFile == ''):
        ipa = True

    if (ipa):
        print('Variables')
        print('GNUPGHOME      :  ' + GNUPGHOME)
        print('SENDERADDRESS  :  ' + SENDERADDRESS)
        print('SIGNFINGERPRINT:  ' + SIGNFINGERPRINT)
        print('recipient      :  ' + recipient)
        print('subject        :  ' + subject)
        print('TempFile       :  ' + TempFile)
        print("A needed variable is blank!")
        exit(400)

    # Build the email.
    myMessage = GMAIL.create_message_with_attachment(SENDERADDRESS, recipient, subject,
                                                     'See attachment.', TempFile)

    # Send the email.
    result = GMAIL.send_message(SENDERADDRESS, myMessage)

    # Delete temp file.
    os.remove(TempFile)

    print("Done")

    return True


def main():
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

            #Move the downloaded file on the GDrive.
            print("Moving file between GDrive folders.")
            GDrive.ARGS.Action = 'Move'
            GDrive.ARGS.File = file
            result = GDrive.main()
            print("Finished moving file.")

    # Consolidate the files to one file.
    print("Consolidating files.")
    items = os.listdir(TempFolder)
    Files = []
    if (len(items) > 0):
        for item in items:
            target = os.path.join(TempFolder, item)
            if (os.path.isfile(target)):
                Files.append(target)

    if (len(Files) > 0):
        with open(ConsolidationFile, 'w+') as outfile:
            for fname in Files:
                with open(fname) as infile:
                    for line in infile:
                        outfile.write(line)
                os.remove(fname)
    print("Finished consolidating files to:  " + ConsolidationFile)

    # Dedupelicate file.
    print("De-Duplicating file.")
    if (os.path.exists(ConsolidationFile)):
        uniqlines = set(open(ConsolidationFile, 'r').readlines())
        with open(FileToUpload, 'w+') as CF:
            CF.writelines(set(uniqlines))
        os.remove(ConsolidationFile)

    # Encrypt Sign and Send
    print("Sign / Encrypt / Send")
    if (os.path.exists(FileToUpload)):
        processFile(dicConfig, FileToUpload)
        os.remove(FileToUpload)
    else:
        print("No Hashes to Upload.")




if __name__ == "__main__":
    main()