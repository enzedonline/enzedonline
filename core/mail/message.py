import logging
import threading

from bs4 import BeautifulSoup
from django.core.mail import EmailMultiAlternatives

class GmailMessage(EmailMultiAlternatives):
    """
    Builds on EmailMultiAlternatives
    Add html directly in onbject instantiation
    Create plain text part from html_body if no body passed
    Call .send() with wait_for_completion=False for async sending
    async sending assumes no result back is required
    """
    def __init__(
        self,
        subject="",
        body="",
        from_email=None,
        to=None,
        bcc=None,
        connection=None,
        attachments=None,
        headers=None,
        alternatives=None,
        cc=None,
        reply_to=None,
        html_body=None
    ):
        super().__init__(
            subject=subject,
            body=body,
            from_email=from_email,
            to=to,
            bcc=bcc,
            connection=None,
            attachments=attachments,
            headers=headers,
            cc=cc,
            reply_to=reply_to,
        )
        self.alternatives = alternatives or []
        if html_body:
            self.attach_alternative(html_body, "text/html")
            if not self.body:
                self.body = self.plain_text_from_html(html_body)
        
    def _send(self, fail_silently: bool = False):
        try:
            return super().send(fail_silently=fail_silently)
        except Exception as e:
            logging.warning(
                f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}"
            )
            if not fail_silently:
                raise
            return False

    def send(self, fail_silently: bool = False, wait_for_completion: bool = True):
        if not wait_for_completion:
            # Using threading.Thread without daemon=True can lead to the
            # thread not being terminated if the main program exits.
            # By setting daemon=True, the thread will be terminated when
            # the main program exits.
            thread = threading.Thread(target=self._send, args=(fail_silently,))
            thread.daemon = True
            thread.start()
        else:
            return self._send(fail_silently)

    def plain_text_from_html(self, html_body):
        try:
            return BeautifulSoup(
                html_body, features="html5lib"
            ).get_text(separator="\r\n\r\n")
        except Exception as e:
            logging.warning(
                f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}"
            )
            return html_body
              