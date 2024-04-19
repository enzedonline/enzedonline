import base64
import copy
import logging
import threading

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import sanitize_address
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from site_settings.models import Tokens

class GmailBackend(BaseEmailBackend):
    """
    Django email backend for sending with Google Workspace
    """
    def __init__(self, fail_silently=False, **kwargs):
        self.fail_silently = fail_silently
        self._lock = threading.RLock()
        service_account_key = Tokens.load().gmail_service_account
        # base_credentials used to build user specific credentials in send method
        self.base_credentials = service_account.Credentials.from_service_account_info(
            service_account_key,
            scopes=['https://www.googleapis.com/auth/gmail.send']
        )

    def open(self):
        """ retained for legacy code compaitibility """
        return True
    
    def close(self):
        """ retained for legacy code compaitibility """
        pass

    def send_messages(self, email_messages, thread=False):
        """
        Sends one or more EmailMessage objects and returns the number of email
        messages sent.
        """
        if not email_messages:
            return 0
        with self._lock:
            num_sent = 0
            for message in email_messages:
                sent = self._send(message)
                if sent:
                    num_sent += 1
        return num_sent

    def _send(self, email_message):
        """
        A helper method that does the actual sending.
        """
        if not email_message.recipients():
            return False
        try:
            # sanitize addresses
            sanitized_message = self.sanitize_addresses(email_message)
            message = sanitized_message.message()
            # Gmail api send() requires JSON format base64 string - convert .message() before sending
            raw = {"raw": base64.urlsafe_b64encode(message.as_bytes(linesep="\r\n")).decode("utf-8")}
            # Set delegated credentials according to the sender email address
            delegated_credentials = self.base_credentials.with_subject(email_message.from_email)
            service = build("gmail", "v1", credentials=delegated_credentials )
            # Send email
            service.users().messages().send(userId='me', body=raw).execute()
        except HttpError as e:
            logging.warning(
                f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}"
            )
            if not self.fail_silently:
                raise
            return False
        return True
    
    def sanitize_addresses(self, email_message):
        """ 
        Make a copy of email message, sanitize addresses 
        Ensure that email addresses are properly formatted & without potentially harmful characters
        """
        message_copy = copy.copy(email_message)
        encoding = email_message.encoding or getattr(settings, 'DEFAULT_CHARSET', 'utf-8')
        message_copy.from_email = sanitize_address(email_message.from_email, encoding)
        for field in ['to', 'cc', 'bcc', 'reply_to']:
            setattr(message_copy, field, [sanitize_address(addr, encoding) for addr in getattr(email_message, field)])
        return message_copy
                