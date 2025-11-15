import uuid

import pytest
from django.urls import reverse, resolve


@pytest.mark.django_db
def test_core_url_includes_exist(client):
    # Ensure books app routes are included
    fake_uuid = uuid.uuid4()
    assert resolve(f"/library/books/{fake_uuid}/toggle-barter/")
    assert resolve(f"/library/books/{fake_uuid}/wishlist/")

    # Ensure barter app routes are included
    assert resolve("/barter/requests/create/")
    # We can't resolve dynamic UUID here without an actual object; just verify pattern exists
    # The following resolve checks will raise Resolver404 if not found
    assert resolve(f"/barter/requests/{uuid.uuid4()}/accept/")
    assert resolve(f"/barter/requests/{uuid.uuid4()}/reject/")

    # Ensure social app routes are included (Post.id is now integer, not UUID)
    fake_post_id = 99999  # Use a fake integer ID - resolve only checks URL pattern, not existence
    assert resolve("/home/")
    assert resolve("/posts/create/")
    assert resolve(f"/posts/{fake_post_id}/like/")
    assert resolve(f"/posts/{fake_post_id}/comments/")
    assert resolve(f"/posts/{fake_post_id}/barter/")
