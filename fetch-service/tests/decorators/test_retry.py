import time
from unittest.mock import Mock, call

import pytest

from decorators.retry import retry


@pytest.fixture
def mock_sleep(mocker):
    mocker.patch("time.sleep")


@pytest.fixture
def make_mock_function():
    def _make_mock_function(succeed_after=None, raise_exception=Exception):
        def _mock():
            if raise_exception is None:
                return None

            if succeed_after is None:
                raise raise_exception

            _mock.attempts += 1

            if _mock.attempts > succeed_after:
                return None

            raise raise_exception

        _mock.attempts = 0

        return Mock(side_effect=_mock)

    return _make_mock_function


def test_does_not_retry_on_successful_invocation(mock_sleep, make_mock_function):
    test_func = make_mock_function(raise_exception=None)
    subject = retry()(test_func)

    subject()

    test_func.assert_called_once()


def test_retries_on_failed_invocation(mock_sleep, make_mock_function):
    with pytest.raises(Exception):
        test_func = make_mock_function()
        subject = retry()(test_func)

        subject()

    # we call the mock 4 times - the first call, and then 3 retries
    assert test_func.call_count == 4


def test_stops_retries_on_later_successful_invocation(mock_sleep, make_mock_function):
    test_func = make_mock_function(succeed_after=1)
    subject = retry()(test_func)

    subject()

    assert test_func.call_count == 2


def test_respects_max_attempts_parameter(mock_sleep, make_mock_function):
    with pytest.raises(Exception):
        test_func = make_mock_function()
        subject = retry(max_attempts=1)(test_func)

        subject()

    assert test_func.call_count == 2


def test_respects_fallback_secs_parameter(mock_sleep, make_mock_function):
    test_func = make_mock_function(succeed_after=1)
    subject = retry(fallback_secs=1)(test_func)

    subject()

    time.sleep.assert_any_call(1)


def test_falls_back_exponentially(mock_sleep, make_mock_function):
    test_func = make_mock_function(succeed_after=2)
    subject = retry()(test_func)

    subject()

    time.sleep.assert_has_calls([call(3), call(9)])


def test_does_not_fall_back_exponentially_when_specified(
    mock_sleep, make_mock_function
):
    test_func = make_mock_function(succeed_after=2)
    subject = retry(exponential=False)(test_func)

    subject()

    time.sleep.assert_has_calls([call(3), call(3)])


def test_retries_only_specified_exceptions(mock_sleep, make_mock_function):
    test_func = make_mock_function(succeed_after=1, raise_exception=RuntimeError)
    subject = retry(exceptions=[RuntimeError])(test_func)

    subject()

    assert test_func.call_count == 2


def test_raises_other_exceptions(mock_sleep, make_mock_function):
    with pytest.raises(RuntimeError):
        test_func = make_mock_function(succeed_after=1, raise_exception=RuntimeError)
        subject = retry(exceptions=[RuntimeWarning])(test_func)

        subject()

    # we should only call the test func once - the first invocation always happens
    assert test_func.call_count == 1
