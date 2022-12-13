import pytest
from download import validate_url


def test_validate_url():
    with pytest.raises(SystemExit):
        assert validate_url("cat")
    with pytest.raises(SystemExit):
        assert validate_url("http://foobar.d")
    assert validate_url(
        "https://www.wikipedia.org"
        ) == "https://www.wikipedia.org"
    assert validate_url("http://10.0.0.1") == "http://10.0.0.1"


