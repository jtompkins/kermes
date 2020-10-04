import logging
from pathlib import Path
import subprocess
from io import BytesIO

from kermes_infra.queues import SQSProducer
from kermes_infra.messages import ConvertEBookMessage, DeliverEBookMessage
from kermes_infra.models import User, EBook
from kermes_infra.repositories import UserRepository, EBookRepository, FileRepository


class Converter:
    def __init__(
        self,
        user_repository: UserRepository,
        ebook_repository: EBookRepository,
        file_repository: FileRepository,
        postmaster_queue_producer: SQSProducer,
        logger: logging.Logger,
    ) -> None:
        self.user_repository = user_repository
        self.ebook_repository = ebook_repository
        self.file_repository = file_repository
        self.postmaster_queue_producer = postmaster_queue_producer
        self.logger = logger

    def process_message(self, message_json: str) -> bool:
        self.logger.debug(f"processing message {message_json}")

        # parse the message
        convert_msg = ConvertEBookMessage.from_json(message_json)

        # fetch the user record to verify kindle preference
        user = self.user_repository.get(convert_msg.user_id)

        if user is None:
            self.logger.error(f"couldn't fetch user with id {convert_msg.user_id}")
            return False

        # if the user doesn't prefer kindle, just repackage the message into a delivery message, send it, and return
        if not user.prefer_kindle:
            self.postmaster_queue_producer.send_message(
                DeliverEBookMessage(user.user_id, convert_msg.ebook_id).to_json()
            )
            return True

        # fetch the ebook record
        ebook = self.ebook_repository.get(user.user_id, convert_msg.ebook_id)

        if ebook is None:
            self.logger.error(f"couldn't fetch ebook with id {convert_msg.ebook_id} for user {user.user_id}")
            return False

        # fetch the ebook file from S3 and write it to the local filesystem
        ebook_content = self.file_repository.get(ebook.content_key)

        if ebook_content is None:
            self.logger.error(f"couldn't fetch ebook content for key {ebook.content_key}")
            return False

        epub_path = Path.cwd() / f"{ebook.ebook_id}.epub"
        mobi_path = Path.cwd() / f"{ebook.ebook_id}.mobi"

        try:
            epub_path.write_bytes(ebook_content.read())
        except Exception as err:
            self.logger.exception("unable to write epub content to local filesystem")
            return False

        # invoke calibre to convert the ebook to mobi
        result = subprocess.run(["ebook-convert", str(epub_path), str(mobi_path)], capture_output=True)

        if result.returncode != 0:
            self.looger.error(
                f"unable to convert ebook {ebook.ebook_id} to MOBI format - out: {result.stdout}, err: {result.stderr}"
            )
            return False

        # write the mobi to S3
        kindle_content_key = f"{ebook.user_id}/books/{ebook.ebook_id}.mobi"

        with mobi_path.open(mode="rb") as f:
            # write the bytestream to S3 and update the content_key on the ebook model
            if not self.file_repository.put(kindle_content_key, f):
                self.logger.exception("unable to push ebook content to S3")
                return False

        # update the ebook record with the mobi content key
        ebook.kindle_content_key = kindle_content_key

        if not self.ebook_repository.put(ebook):
            self.logger.error(f"couldn't write updated ebook to Dynamo - ebook_id {ebook.ebook_id}")
            return False

        # send the delivery message
        self.postmaster_queue_producer.send_message(DeliverEBookMessage(user.user_id, convert_msg.ebook_id).to_json())

        return True
