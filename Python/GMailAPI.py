from __future__ import print_function
import base64
import os
import mimetypes
from email import errors
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from urllib2 import HTTPError


# If modifying these scopes, delete the file token.json.

# Create, read, update, and delete drafts. Send messages and drafts.
#SCOPES = 'https://www.googleapis.com/auth/gmail.compose'

# Send messages only. No read or modify privileges on mailbox.
SCOPES = 'https://www.googleapis.com/auth/gmail.send'

class GMailAPI():
    def __init__(self, SenderAddress, TokenLocation, CredentialLocation):

        if (TokenLocation == ""):
            self.TOKEN = '/Temp/GMail.API.token.json'
        else:
            self.TOKEN = TokenLocation

        if (CredentialLocation == ""):
            self.CRED = '/Temp/GMAIL.API.credentials.json'
        else:
            self.CRED = CredentialLocation

        self.SENDERADDRESS = SenderAddress
        self.SERVICE = ""


    def create_message(self, sender, to, subject, message_text):
      """Create a message for an email.

      Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.

      Returns:
        An object containing a base64url encoded email object.
      """
      message = MIMEText(message_text)
      message['to'] = to
      message['from'] = sender
      message['subject'] = subject
      return {'raw': base64.urlsafe_b64encode(message.as_string())}


    def create_message_with_attachment(self,
        sender, to, subject, message_text, file):
      """Create a message for an email.

      Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.
        file: The path to the file to be attached.

      Returns:
        An object containing a base64url encoded email object.
      """
      message = MIMEMultipart()
      message['to'] = to
      message['from'] = sender
      message['subject'] = subject

      msg = MIMEText(message_text)
      message.attach(msg)

      content_type, encoding = mimetypes.guess_type(file)

      if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
      main_type, sub_type = content_type.split('/', 1)
      if main_type == 'text':
        fp = open(file, 'rb')
        msg = MIMEText(fp.read(), _subtype=sub_type)
        fp.close()
      elif main_type == 'image':
        fp = open(file, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
      elif main_type == 'audio':
        fp = open(file, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
      else:
        fp = open(file, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
      filename = os.path.basename(file)
      msg.add_header('Content-Disposition', 'attachment', filename=filename)
      message.attach(msg)

      return {'raw': base64.urlsafe_b64encode(message.as_string())}


    def send_message(self, user_id, message):
      """Send an email message.

      Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

      Returns:
        Sent Message.
      """
      if (self.SERVICE == ""):
          self.authenticate()

      try:
        message = (self.SERVICE.users().messages().send(userId=user_id, body=message)
                   .execute())
        print ('Message Id: %s' % message['id'])
        return message

      except errors.HttpError, error:
        print ('An error occurred: %s' % error)
        exit(300)


    def authenticate(self):
        store = file.Storage(self.TOKEN)
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(self.CRED, self.SCOPES)
            creds = tools.run_flow(flow, store)

        self.SERVICE = build('gmail', 'v1', http=creds.authorize(Http()))
        return

def main():
        print("This is the GMail API.")
        return


if __name__ == '__main__':
    main()