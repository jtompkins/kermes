import kermes_infra.models.user
import pytest
import datetime

EMPTY_UUID = "00000000-0000-0000-0000-000000000000"
TEST_EPOCH_DATE = 205286400
TEST_DATE = datetime.datetime.fromtimestamp(TEST_EPOCH_DATE, tz=datetime.timezone.utc)


@pytest.fixture
def mock_now(monkeypatch):
    class testdatetime:
        @classmethod
        def now(cls, tz):
            return TEST_DATE

        @classmethod
        def fromtimestamp(cls, timestamp, tz):
            return datetime.datetime.fromtimestamp(timestamp, tz)

    monkeypatch.setattr(kermes_infra.models.user, "datetime", testdatetime)


def test_user_constructor_makes_well_formed_object(mock_now):
    subject = kermes_infra.models.User(EMPTY_UUID)

    assert subject.user_id == EMPTY_UUID
    assert subject.email is None
    assert subject.delivery_email is None
    assert subject.prefer_kindle is False
    assert subject.send_threshhold is None
    assert subject.send_day is None
    assert subject.created_date == TEST_DATE


def test_user_to_dynamo_makes_well_formed_dict(mock_now):
    subject = kermes_infra.models.User(EMPTY_UUID)
    subject.email = "test@test.com"
    subject.delivery_email = "test@test.com"
    subject.prefer_kindle = True
    subject.send_threshhold = 5
    subject.send_day = 5

    dynamo_dict = subject.to_dynamo()

    assert dynamo_dict["user_id"] == EMPTY_UUID
    assert dynamo_dict["email"] == "test@test.com"
    assert dynamo_dict["delivery_email"] == "test@test.com"
    assert dynamo_dict["prefer_kindle"] == "True"
    assert dynamo_dict["send_threshhold"] == 5
    assert dynamo_dict["send_day"] == 5
    assert dynamo_dict["created_date"] == str(float(TEST_EPOCH_DATE))


def test_user_to_dynamo_properly_handles_missing_fields(mock_now):
    subject = kermes_infra.models.User(EMPTY_UUID)

    dynamo_dict = subject.to_dynamo()

    assert dynamo_dict["user_id"] == EMPTY_UUID
    assert dynamo_dict["prefer_kindle"] == "False"
    assert dynamo_dict["created_date"] == str(float(TEST_EPOCH_DATE))

    assert "email" not in dynamo_dict
    assert "delivery_email" not in dynamo_dict
    assert "send_threshhold" not in dynamo_dict
    assert "send_day" not in dynamo_dict


def test_user_from_dynamo_properly_converts_to_model(mock_now):
    dynamo_dict = {
        "user_id": EMPTY_UUID,
        "email": "test@test.com",
        "delivery_email": "test@test.com",
        "prefer_kindle": "True",
        "send_threshhold": 5,
        "send_day": 5,
        "created_date": str(float(TEST_EPOCH_DATE)),
    }

    subject = kermes_infra.models.User.from_dynamo(dynamo_dict)

    assert subject.user_id == EMPTY_UUID
    assert subject.email == "test@test.com"
    assert subject.delivery_email == "test@test.com"
    assert subject.prefer_kindle is True
    assert subject.send_threshhold == 5
    assert subject.send_day == 5
    assert subject.created_date == TEST_DATE


def test_user_from_dynamo_properly_handles_missing_fields(mock_now):
    dynamo_dict = {
        "user_id": EMPTY_UUID,
        "prefer_kindle": "True",
        "created_date": str(float(TEST_EPOCH_DATE)),
    }

    subject = kermes_infra.models.User.from_dynamo(dynamo_dict)

    assert subject.user_id == EMPTY_UUID
    assert subject.email is None
    assert subject.delivery_email is None
    assert subject.prefer_kindle is True
    assert subject.send_threshhold is None
    assert subject.send_day is None
    assert subject.created_date == TEST_DATE
