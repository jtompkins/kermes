import models.article
import uuid
import datetime
import pytest

EMPTY_UUID = "00000000-0000-0000-0000-000000000000"
TEST_EPOCH_DATE = 205286400
TEST_DATE = datetime.datetime.fromtimestamp(TEST_EPOCH_DATE, tz=datetime.timezone.utc)


@pytest.fixture
def mock_uuid(mocker):
    mocker.patch("models.article.uuid4", return_value=uuid.UUID(EMPTY_UUID))


@pytest.fixture
def mock_now(monkeypatch):
    class testdatetime:
        @classmethod
        def now(cls, tz):
            return TEST_DATE

        @classmethod
        def fromtimestamp(cls, timestamp, tz):
            return datetime.datetime.fromtimestamp(timestamp, tz)

    monkeypatch.setattr(models.article, "datetime", testdatetime)


def test_article_constructor_makes_well_formed_object(mock_uuid, mock_now):
    subject = models.Article(EMPTY_UUID)

    assert subject.article_id == EMPTY_UUID
    assert subject.content_key is None
    assert subject.related_content == []
    assert subject.created_date == TEST_DATE


def test_article_to_dynamo_makes_well_formed_dict(mock_uuid, mock_now):
    subject = models.Article(EMPTY_UUID)

    dynamo_dict = subject.to_dynamo()

    assert dynamo_dict == {
        "user_id": EMPTY_UUID,
        "article_id": EMPTY_UUID,
        "related_content": [],
        "created_date": str(float(TEST_EPOCH_DATE)),
    }


def test_article_to_dynamo_properly_handles_related_content(mock_uuid, mock_now):
    subject = models.Article(EMPTY_UUID)
    subject.related_content.append(models.article.RelatedContent("test_mime", "test_key"))
    dynamo_dict = subject.to_dynamo()

    assert dynamo_dict["related_content"] == [{"mime_type": "test_mime", "content_key": "test_key"}]


def test_article_to_dynamo_properly_handles_missing_fields(mock_uuid, mock_now):
    subject = models.Article(EMPTY_UUID)

    dynamo_dict = subject.to_dynamo()

    assert dynamo_dict["user_id"] == EMPTY_UUID
    assert dynamo_dict["article_id"] == EMPTY_UUID
    assert dynamo_dict["related_content"] == []
    assert dynamo_dict["created_date"] == str(float(TEST_EPOCH_DATE))

    assert "content_key" not in dynamo_dict


def test_article_from_dynamo_properly_converts_to_model(mock_uuid, mock_now):
    dynamo_dict = {
        "user_id": EMPTY_UUID,
        "article_id": EMPTY_UUID,
        "related_content": [{"mime_type": "test_mime", "content_key": "test_key"}],
        "created_date": str(float(TEST_EPOCH_DATE)),
    }

    subject = models.Article.from_dynamo(dynamo_dict)

    assert subject.user_id == EMPTY_UUID
    assert subject.article_id == EMPTY_UUID
    assert subject.content_key is None
    assert len(subject.related_content) == 1
    assert subject.related_content[0].mime_type == "test_mime"
    assert subject.related_content[0].content_key == "test_key"
    assert subject.created_date == TEST_DATE


def test_article_from_dynamo_properly_handles_missing_fields(mock_now):
    dynamo_dict = {
        "user_id": EMPTY_UUID,
        "article_id": EMPTY_UUID,
        "related_content": [],
        "created_date": str(float(TEST_EPOCH_DATE)),
    }

    subject = models.Article.from_dynamo(dynamo_dict)

    assert subject.user_id == EMPTY_UUID
    assert subject.article_id == EMPTY_UUID
    assert subject.content_key is None
    assert subject.related_content == []
    assert subject.created_date == TEST_DATE
