#!/usr/bin/Python

import gnupg
import GMailAPI
import os

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
                key, value = line.split(':')
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
            GNUPGHOME = ''
        elif (key == 'Sender'):
            SENDERADDRESS = ''
        elif (key == 'SignFingerprint'):
            SIGNFINGERPRINT = ''

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

def main():
    # This is the file that holds the configuration settings.
    dicConfig = readConfigFile('/Temp/EmailConfig.config')

    # Set global variables with the dictionary returned.
    setParameters(dicConfig)

    # Build the GMail object
    GMAIL = GMailAPI.GMailAPI(SENDERADDRESS, dicConfig['APIToken'], dicConfig['APICred'])

    subject = dicConfig['Subject']
    recipient = dicConfig['To']
    TargetFile = dicConfig['TargetFile']
    TempFile = dicConfig['TempFile']
    SignerPassPhrase = dicConfig['SignerPhraseFile']

    # Encrypt the file.
    encrypted_data = encryptData(TargetFile, recipient, True, getSingerPhrase(SignerPassPhrase))

    # Save the encrypted file.
    saveFile = open(TempFile, 'w')
    saveFile.write(str(encrypted_data))
    saveFile.close()

    # Build the email.
    myMessage = GMAIL.create_message_with_attachment(SENDERADDRESS, recipient, subject,
                                                     'See attachment.', TempFile)

    # Send the email.
    result = GMAIL.send_message(SENDERADDRESS, myMessage)

    # Delete temp file.
    os.remove(TempFile)

    print("Done")

if __name__ == "__main__":
    main()