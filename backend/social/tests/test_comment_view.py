from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from social.models import Post, Comment, CommentLike

User = get_user_model()

class TestCommentViews(APITestCase):
    def setUp(self):
        # Users
        self.reviewer = User.objects.create_user(username="reviewer", password="pass", email="reviewer@example.com")
        self.other_user = User.objects.create_user(username="other", password="pass", email="other@example.com")

        # Post
        self.post = Post.objects.create(content="Test Post", author=self.reviewer)

        self.comment_by_other = Comment.objects.create(
                post=self.post, author=self.other_user, content="Other user's comment"
            )

        # Comment by reviewer
        self.comment = Comment.objects.create(
        post=self.post, author=self.reviewer, content="Original comment")

        # Nested URLs for the comment
        self.comment_post_url = reverse("comment-post", args=[self.post.id])
        self.comment_edit_url = reverse("comment-edit", args=[self.post.id, self.comment.id])
        self.comment_delete_url = reverse("comment-delete", args=[self.post.id, self.comment.id])
        self.comment_edit_url_other = reverse("comment-edit", args=[self.post.id, self.comment_by_other.id])
        self.comment_delete_url_other = reverse("comment-delete", args=[self.post.id, self.comment_by_other.id])
      
    def test_user_can_patch_own_comment_success(self):
        self.client.force_authenticate(self.reviewer)
        payload = {"content": "Updated comment"}
        res = self.client.patch(self.comment_edit_url, data=payload, format="json")

        assert res.status_code == 200

        # Refresh from DB
        self.comment.refresh_from_db()
        assert self.comment.content == "Updated comment"

        # Response should include updated comment data (via PostSerializer)
        assert "post" in res.data
  
    def test_post_author_can_delete_comment_on_their_post(self):
        self.client.force_authenticate(self.reviewer)  # post author
        res = self.client.delete(self.comment_delete_url_other)
        assert res.status_code == 200
        assert not Comment.objects.filter(id=self.comment_by_other.id).exists()
  
    def test_user_can_delete_own_comment(self):
        self.client.force_authenticate(self.reviewer)

        res = self.client.delete(self.comment_delete_url)

        assert res.status_code == 200
        assert not Comment.objects.filter(id=self.comment.id).exists()
  
    def test_user_cannot_edit_others_comment(self):
        self.client.force_authenticate(self.other_user)

        payload = {"content": "Hacked content"}
        res = self.client.patch(self.comment_edit_url, data=payload, format="json")

        assert res.status_code == 403
  
    def test_user_cannot_delete_others_comment(self):
        self.client.force_authenticate(self.other_user)

        res = self.client.delete(self.comment_delete_url)
        assert res.status_code == 403
  
    def test_post_author_cannot_edit_comment_by_other_user(self):
        self.client.force_authenticate(self.reviewer)  # post author
        payload = {"content": "Trying to edit"}
        res = self.client.patch(self.comment_edit_url_other, data=payload, format="json")
        assert res.status_code == 403
        # Ensure comment content did not change
        self.comment_by_other.refresh_from_db()
        assert self.comment_by_other.content == "Other user's comment"


    def test_user_can_like_and_unlike_others_comment(self):
        self.client.force_authenticate(self.reviewer)
        # Like other user's comment
        like_url = reverse("like-comment", args=[self.post.id, self.comment_by_other.id])
        res = self.client.post(like_url)
        assert res.status_code == 200

        # Check that like exists
        assert CommentLike.objects.filter(comment=self.comment_by_other, user=self.reviewer).exists()
        assert res.data["comment"]["like_count"] == 1

        # Unlike the same comment
        res = self.client.post(like_url)
        assert res.status_code == 200
        assert not CommentLike.objects.filter(comment=self.comment_by_other, user=self.reviewer).exists()
        assert res.data["comment"]["like_count"] == 0

    def test_user_can_like_and_unlike_own_comment(self):
        self.client.force_authenticate(self.reviewer)
        # Like own comment
        like_url = reverse("like-comment", args=[self.post.id, self.comment.id])
        res = self.client.post(like_url)
        assert res.status_code == 200

        # Check that like exists
        assert CommentLike.objects.filter(comment=self.comment, user=self.reviewer).exists()
        assert res.data["comment"]["like_count"] == 1

        # Unlike own comment
        res = self.client.post(like_url)
        assert res.status_code == 200
        assert not CommentLike.objects.filter(comment=self.comment, user=self.reviewer).exists()
        assert res.data["comment"]["like_count"] == 0
    
    def test_user_cannot_like_nonexistent_comment(self):
        self.client.force_authenticate(self.reviewer)
        # Use a random UUID that doesn't exist
        import uuid
        fake_comment_id = uuid.uuid4()
        like_url = reverse("like-comment", args=[self.post.id, fake_comment_id])
        res = self.client.post(like_url)
        assert res.status_code == 404
        assert res.data["error"] == "Comment not found"

