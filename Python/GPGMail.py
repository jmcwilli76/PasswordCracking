#!/usr/bin/Python

import subprocess


#https://pythonhosted.org/python-gnupg/
SMTPGATEWAY = ""
SENDERADDRESS = ""
SENDERUSERNAME = ""
SENDERPASSWORD = ""
SENDERPRIVATEKEY = ""
SENDERPUBLICKEY = ""
SMTPCONNECTION = ""

def GPGMail(SMTPGateway, SenderAddress, SenderUsername,):
    return

def SendMail(DestinationAddress, DestinationPubKey, Subject, Body):

    return






def main():
    print("Hello World")
    theOutput = subprocess.check_output(['ls', '-lah'])
    print(theOutput)
    return

if __name__ == "__main__":
    main()