import kermes_infra.models.ebook
import pytest
import datetime
import uuid

EMPTY_UUID = "00000000-0000-0000-0000-000000000000"
TEST_EPOCH_DATE = 205286400
TEST_DATE = datetime.datetime.fromtimestamp(TEST_EPOCH_DATE, tz=datetime.timezone.utc)


@pytest.fixture
def mock_uuid(mocker):
    mocker.patch("kermes_infra.models.ebook.uuid4", return_value=uuid.UUID(EMPTY_UUID))


@pytest.fixture
def mock_now(monkeypatch):
    class testdatetime:
        @classmethod
        def now(cls, tz):
            return TEST_DATE

        @classmethod
        def fromtimestamp(cls, timestamp, tz):
            return datetime.datetime.fromtimestamp(timestamp, tz)

    monkeypatch.setattr(kermes_infra.models.ebook, "datetime", testdatetime)


def test_ebook_constructor_makes_well_formed_object(mock_now, mock_uuid):
    subject = kermes_infra.models.EBook(EMPTY_UUID)

    assert subject.user_id == EMPTY_UUID
    assert subject.ebook_id == EMPTY_UUID
    assert subject.article_ids == []
    assert subject.content_key is None
    assert subject.created_date == TEST_DATE


def test_ebook_to_dynamo_makes_well_formed_dict(mock_now, mock_uuid):
    subject = kermes_infra.models.EBook(EMPTY_UUID)
    subject.ebook_id = EMPTY_UUID
    subject.content_key = "test"
    subject.created_date = TEST_DATE

    dynamo_dict = subject.to_dynamo()

    assert dynamo_dict["user_id"] == EMPTY_UUID
    assert dynamo_dict["ebook_id"] == EMPTY_UUID
    assert dynamo_dict["content_key"] == "test"
    assert dynamo_dict["article_ids"] == []
    assert dynamo_dict["created_date"] == str(float(TEST_EPOCH_DATE))


def test_ebook_to_dynamo_properly_handles_missing_fields(mock_now, mock_uuid):
    subject = kermes_infra.models.EBook(EMPTY_UUID)

    dynamo_dict = subject.to_dynamo()

    assert "content_key" not in dynamo_dict


def test_ebook_from_dynamo_properly_converts_to_model(mock_now, mock_uuid):
    dynamo_dict = {
        "user_id": EMPTY_UUID,
        "ebook_id": EMPTY_UUID,
        "content_key": "test",
        "article_ids": ["test1", "test2"],
        "created_date": str(float(TEST_EPOCH_DATE)),
    }

    subject = kermes_infra.models.EBook.from_dynamo(dynamo_dict)

    assert subject.user_id == EMPTY_UUID
    assert subject.ebook_id == EMPTY_UUID
    assert subject.article_ids == ["test1", "test2"]
    assert subject.content_key == "test"
    assert subject.created_date == TEST_DATE


def test_ebook_from_dynamo_properly_handles_missing_fields(mock_now, mock_uuid):
    dynamo_dict = {
        "user_id": EMPTY_UUID,
        "ebook_id": EMPTY_UUID,
        "article_ids": [],
        "created_date": str(float(TEST_EPOCH_DATE)),
    }

    subject = kermes_infra.models.EBook.from_dynamo(dynamo_dict)

    assert subject.content_key is None
