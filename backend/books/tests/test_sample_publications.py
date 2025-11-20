import pytest
from books import sample_publications


def test_sample_publications_have_required_fields():
    assert sample_publications.SAMPLE_PUBLICATIONS

    for entry in sample_publications.SAMPLE_PUBLICATIONS:
        assert entry["identifier"]
        assert entry["title"]
        assert isinstance(entry["authors"], list)
        assert isinstance(entry["genres"], list)
        assert isinstance(entry["description"], str)
