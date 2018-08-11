#!/usr/bin/Python

import gnupg
import GMailAPI
import os



#https://pythonhosted.org/python-gnupg/

SENDERADDRESS = "str.somecoolname@gmail.com"
SIGNFINGERPRINT = '609703532579DBB2C2C2B769044643E3725386DA'
GNUPGHOME = '/home/jesse/.gnupg'
GMAIL = GMailAPI.GMailAPI(SENDERADDRESS, '/Temp/GMail.API.token.json', '/Temp/GMAIL.API.credentials.json')


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

def main():

    print("Sending email.")

    subject = 'Registration Submission'
    recipient = 'sub-2018@contest.korelogic.com'
    #recipient = 'jmcwilli76@gmail.com'
    SignerPassPhrase = 'DoNotCrackMe!'
    TargetFile = '/home/jesse/Git/PasswordCracking/2018-CrackMeIfYouCan/teamclass.txt'
    TempFile = '/home/jesse/Git/PasswordCracking/2018-CrackMeIfYouCan/keySubmission.pgp'

    # Encrypt the file.
    encrypted_data = encryptData(TargetFile, recipient, True, SignerPassPhrase)

    # Save the encrypted file.
    saveFile = open(TempFile, 'w')
    saveFile.write(str(encrypted_data))
    saveFile.close()

    # Check file
    newFile = open(TempFile, 'r')
    newText = newFile.readlines()
    print("Checking new file:  ")
    print(newText)

    # Build the email.
    myMessage = GMAIL.create_message_with_attachment(SENDERADDRESS, recipient, subject,
                                                     'See attachment.', TempFile)

    # Send the email.
    result = GMAIL.send_message(SENDERADDRESS, myMessage)
    #result = ""

    # Delete temp file.
    os.remove(TempFile)

    print(result)


    return

if __name__ == "__main__":
    main()