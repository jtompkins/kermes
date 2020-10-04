from email.message import EmailMessage
from io import BytesIO
from logging import Logger

import boto3


class MailService:
    def __init__(self, endpoint_url: str, sender_email: str, logger: Logger):
        self.ses = boto3.client("ses", endpoint_url=endpoint_url)
        self.sender_email = sender_email
        self.logger = logger

    def send_message(
        self, kindle_ebook: bool, recipient: str, title: str, text: str, attachment: BytesIO, file_name: str
    ) -> bool:
        msg = EmailMessage()
        msg["Subject"] = title
        msg["From"] = self.sender_email
        msg["To"] = recipient
        msg.set_content(text)
        data = attachment.read()

        sub_mimetype = "x-mobipocket-ebook" if kindle_ebook is True else "epub+zip"

        msg.add_attachment(data, maintype="application", subtype=sub_mimetype, filename=file_name)

        try:
            self.ses.send_raw_email(
                Source=self.sender_email, Destinations=[recipient], RawMessage={"Data": msg.as_string()}
            )
        except Exception as err:
            self.logger.exception(f"Unable to send mail to receipient {recipient}")
            return False

        return True
