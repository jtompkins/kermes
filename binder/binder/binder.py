import logging
from pathlib import Path

from ebooklib import epub

from kermes_infra.repositories import UserRepository, ArticleRepository, EBookRepository, FileRepository
from kermes_infra.models import User, Article, RelatedContent, EBook
from kermes_infra.messages import DeliverEBookMessage, BindEBookMessage, ConvertEBookMessage
from kermes_infra.queues import SQSProducer


class Binder:
    def __init__(
        self,
        user_repository: UserRepository,
        article_repository: ArticleRepository,
        ebook_repository: EBookRepository,
        file_repository: FileRepository,
        converter_queue_producer: SQSProducer,
        postmaster_queue_producer: SQSProducer,
        logger: logging.Logger,
    ) -> None:
        self.user_repository = user_repository
        self.article_repository = article_repository
        self.ebook_repository = ebook_repository
        self.file_repository = file_repository
        self.converter_queue_producer = converter_queue_producer
        self.postmaster_queue_producer = postmaster_queue_producer
        self.logger = logger

    def process_message(self, message_json: str) -> bool:
        self.logger.debug(f"processing message {message_json}")

        # parse the message
        bind_ebook_msg = BindEBookMessage.from_json(message_json)

        # fetch the user record
        user = self.user_repository.get(bind_ebook_msg.user_id)

        # fetch the articles for the user
        articles = self.article_repository.get_all(user.user_id)

        # create the ebook model
        ebook_model = EBook(user.user_id)

        # create an ebooklib ebook
        ebook = epub.EpubBook()

        chapters = []
        related_items = []

        # for each article:
        for i, article in enumerate(articles):
            # add the article ID to the ebook model
            ebook_model.article_ids.append(article.article_id)

            # fetch the content from S3
            article_content = self.file_repository.get(article.content_key)

            # create an ebooklib chapter
            chapter = epub.EpubHtml(title=article.title, file_name=f"chapter_{i}.xhtml", lang="en")

            # add the content to the chapter
            chapter.set_content(article_content.read())

            # for each related content:
            for j, related_content in enumerate(article.related_content):
                # fetch the related content from S3
                item_content = self.file_repository.get(related_content.content_key)

                # create the ebooklib item
                related_item = epub.EpubItem(
                    uid=f"related_item{i}",
                    file_name=related_content.content_key,
                    media_type=related_content.mime_type,
                    content=item_content.read(),
                )

                related_items.append(related_item)

            chapters.append(chapter)

        # add the chapters to the ebook
        for chapter in chapters:
            ebook.add_item(chapter)

        # add the images to the ebook as linked content
        for item in related_items:
            ebook.add_item(item)

        # add ebook metadata
        ebook.set_identifier("")  # TODO: Find a value for this
        ebook.set_title("")  # TODO: Find a value for this
        ebook.add_author("")  # TODO: Find a value for this
        ebook.set_language("en")

        # create the ebook nav structure
        ebook.spine = chapters
        ebook.toc = chapters

        epub_path = Path.cwd() / f"{ebook_model.ebook_id}.epub"

        # render the ebook and write it to a local file
        epub.write_epub(str(epub_path), ebook)

        content_key = f"{ebook_model.user_id}/books/{ebook_model.ebook_id}.epub"

        # read the local file into a bytestream
        with epub_path.open(mode="rb") as f:
            # write the bytestream to S3 and update the content_key on the ebook model
            self.file_repository.put(content_key, f)

        # remove the temporary ePub file
        epub_path.unlink()

        ebook_model.content_key = content_key

        # write the ebook model to Dynamo
        self.ebook_repository.put(ebook_model)

        if user.prefer_kindle:
            self.converter_queue_producer.send_message(
                ConvertEBookMessage(ebook_model.user_id, ebook_model.ebook_id).to_json()
            )
        else:
            self.postmaster_queue_producer.send_message(
                DeliverEBookMessage(ebook_model.user_id, ebook_model.ebook_id).to_json()
            )

        return True
