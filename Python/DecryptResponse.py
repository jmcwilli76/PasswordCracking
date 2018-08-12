#!/usr/bin/Python

import gnupg
import GMailAPI
import base64

GNUPGHOME = ''
SENDERADDRESS = ''
SIGNFINGERPRINT = ''


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


def getLastResponse(GMAIL, UserID, Subject, From, AdditionalQuery):
    retObj = ""
    result = GMAIL.list_messages(UserID, From, Subject, AdditionalQuery)
    rSize = result['resultSizeEstimate']
    if (rSize == 0):
        print("No messages found!")
        exit(404)
    messages = result['messages']
    if not messages:
        print("No messages found!")
        exit(404)
    else:
        print("Found ({0}) messages.".format(str(len(messages))))

    maxDate = 0
    datedMessages = {}
    for message in messages:
        # Get the email.
        mes = GMAIL.get_message(UserID, message['id'])
        # Get the date and body
        internalDate = mes['internalDate']
        # Add the body to the dictionary with the date as the key.
        datedMessages[internalDate] = mes['payload']

        if (internalDate > maxDate):
            maxDate = internalDate
    # Assign the newest email to internalPayload
    internalPayload = datedMessages[maxDate]
    # Check to make sure it isn't null.
    if not internalPayload:
        print("Newest email failed to be retrieved!")
    else:
        body = internalPayload['body']

    if not body:
        print("Failed to get email body!")
    else:
        body = body['data']
        retObj = base64.decodestring(body)

    return retObj


def decryptMessage(SignerPhraseFile, EncryptedMessage):
    retString = ""
    gpg = gnupg.GPG(gnupghome=GNUPGHOME)
    retString = gpg.decrypt(EncryptedMessage, always_trust=True, passphrase=getSingerPhrase(SignerPhraseFile))
    return retString


def main():
    # This is the file that holds the configuration settings.
    dicConfig = readConfigFile('/Temp/EmailConfig.config')

    # Set global variables with the dictionary returned.
    setParameters(dicConfig)

    # Set variables with the dictionary returned.
    recipient = dicConfig['To']
    SignerPhraseFile = dicConfig['SignerPhraseFile']
    Scopes = dicConfig['Scopes']
    Subject = dicConfig['ResponseSubject']
    AdditionalQuery = "in:unread in:inbox"
    #AdditionalQuery = ""

    # Build the GMail object
    GMAIL = GMailAPI.GMailAPI(SENDERADDRESS, dicConfig['APIToken'], dicConfig['APICred'], Scopes)

    # Get the last email received.
    lastEmail = getLastResponse(GMAIL, SENDERADDRESS, Subject, recipient, AdditionalQuery)

    # Decrypt the email.
    message = decryptMessage(SignerPhraseFile, lastEmail)

    print(message)


if __name__ == "__main__":
    main()