import logging
from io import BytesIO

from kermes_infra.mail import MailService
from kermes_infra.repositories import FileRepository, UserRepository, EBookRepository
from kermes_infra.queues import SQSConsumer

from kermes_infra.messages import DeliverEBookMessage, CleanUpMessage


class Postmaster:
    def __init__(
        self,
        user_repository: UserRepository,
        ebook_repository: EBookRepository,
        file_repository: FileRepository,
        mail_service: MailService,
        housekeeper_queue_producer: SQSConsumer,
        logger: logging.Logger,
    ) -> None:
        self.user_repository = user_repository
        self.ebook_repository = ebook_repository
        self.file_repository = file_repository
        self.mail_service = mail_service
        self.housekeeper_queue_producer = housekeeper_queue_producer
        self.logger = logger

    def process_message(self, message_json: str) -> bool:
        self.logger.debug(f"processing message {message_json}")

        # parse the message
        deliver_msg = DeliverEBookMessage.from_json(message_json)

        # fetch the user record
        user = self.user_repository.get(deliver_msg.user_id)

        if user is None:
            self.logger.error(f"couldn't fetch user with id {deliver_msg.user_id}")
            return False

        # fetch the ebook record
        ebook = self.ebook_repository.get(user.user_id, deliver_msg.ebook_id)

        if ebook is None:
            self.logger.error(f"couldn't fetch ebook with id {deliver_msg.ebook_id} for user {user.user_id}")
            return False

        # fetch the ebook file from S3
        content_key = ebook.kindle_content_key if user.prefer_kindle else ebook.content_key

        ebook_content = self.file_repository.get(content_key)

        if ebook_content is None:
            self.logger.error(f"couldn't fetch ebook content for key {content_key}")
            return False

        # send the ebook message
        attachment_filename = "ebook.mobi" if user.prefer_kindle else "ebook.epub"

        if not self.mail_service.send_message(
            user.prefer_kindle,
            user.delivery_email,
            "Kermes delivery!",
            "This is your ebook!",
            BytesIO(ebook_content.read()),
            attachment_filename,
        ):
            self.logger.error(f"couldn't deliver ebook {ebook.ebook_id} for user {user.user_id}")
            return False

        self.housekeeper_queue_producer.send_message(CleanUpMessage(user.user_id, ebook.ebook_id).to_json())

        return True
