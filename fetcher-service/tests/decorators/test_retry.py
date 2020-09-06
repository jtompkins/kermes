from decorators.retry import retry
from unittest.mock import Mock
from unittest.mock import patch
import pytest


def test_does_not_retry_on_successful_invocation():
    with patch("time.sleep"):
        test_func = Mock()
        subject = retry()(test_func)

        subject()

        test_func.assert_called_once()


def test_retries_on_failed_invocation():
    with patch("time.sleep"), pytest.raises(Exception):
        test_func = Mock(side_effect=Exception())
        subject = retry()(test_func)

        subject()

    assert test_func.call_count == 3
