import pytest
from io import StringIO
from download import validate_url, get_url_data, get_soup_image, choice


def test_validate_url():
    with pytest.raises(SystemExit):
        assert validate_url('cat')
    with pytest.raises(SystemExit):
        assert validate_url('http://foobar.d')
    assert validate_url(
        'https://www.wikipedia.org'
        ) == 'https://www.wikipedia.org'
    assert validate_url('http://10.0.0.1') == 'http://10.0.0.1'


def test_get_url_data_HTTPError():
    with pytest.raises(SystemExit):
        assert get_url_data('http://httpbin.org/status/403')


def test_get_url_data_timeout():
    with pytest.raises(SystemExit):
        assert get_url_data('http://httpbin.org/status/408')


def test_get_url_data_soup():
    url = 'https://www.google.com'
    test = get_url_data(url)
    assert get_url_data(url) == test


def test_get_soup_image():
    url = 'https://www.google.com'
    test = get_url_data(url)
    check = get_soup_image(test)
    assert get_soup_image(test) == check


def test_choice_no(monkeypatch):
    user_prompt = StringIO('n\n')
    monkeypatch.setattr('sys.stdin', user_prompt)
    with pytest.raises(SystemExit):
        assert choice(50)
