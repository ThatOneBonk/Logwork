import io

from stream import stream_file

def test_stream_file(monkeypatch):
    """
    Should stream the file contents one by one.
    """
    fake_file_content = "Alpha\nBeta\nGamma\n"
    fake_file = io.StringIO(fake_file_content)

    def mock_open(*args, **kwargs):
        return fake_file

    monkeypatch.setattr("builtins.open", mock_open)

    result = list(stream_file("dummy/path.txt"))
    assert result == ["Alpha", "Beta", "Gamma"]
