#!/usr/bin/Python

import subprocess
import gnupg
import GMailAPI




#https://pythonhosted.org/python-gnupg/

SENDERADDRESS = "str.somecoolname@gmail.com"
SENDERPRIVATEKEY = ""
SENDERPUBLICKEY = "725386DA"
GMAIL = GMailAPI.GMailAPI(SENDERADDRESS, '/Temp/GMail.API.token.json', '/Temp/GMAIL.API.credentials.json')


def GPGMail(SMTPGateway, SenderAddress, SenderUsername,):
    return

def SendMail(DestinationAddress, DestinationPubKey, Subject, Body):

    return

def main():
    print("Sending email.")
    myMessage = GMAIL.create_message(SENDERADDRESS, 'jmcwilli76@gmail.com', 'Testing 1', 'Test Body')
    result = GMAIL.send_message(SENDERADDRESS, myMessage)
    print(result)
    return

if __name__ == "__main__":
    main()