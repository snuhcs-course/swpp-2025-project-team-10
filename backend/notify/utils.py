from accounts.models import Follow
from barter.models import BarterCounter, BarterRequest
from books.models import BookReview
from social.models import Post

from .models import Notification


def create_notification(
    request,
    type_of_notification,
    post_id=None,
    follow_id=None,
    barter_id=None,
    review_id=None,
):
    """
    Create a notification object aligned with the Notification model.
    """
    recipient = None
    sender = request.user
    title = ""
    message = ""
    content_object = None

    # --- Post Like ---
    if type_of_notification == "post_like" and post_id:
        post = Post.objects.get(pk=post_id)
        recipient = post.author
        title = "Post Liked"
        message = f"{sender.first_name} liked one of your posts!"
        content_object = post

    # --- Post Comment ---
    elif type_of_notification == "post_comment" and post_id:
        post = Post.objects.get(pk=post_id)
        recipient = post.author
        title = "Comment Received"
        message = f"{sender.first_name} commented on one of your posts!"
        content_object = post

    # --- Review Like ---
    elif type_of_notification == "review_like" and review_id:
        review = BookReview.objects.get(pk=review_id)
        recipient = review.reviewer
        title = "Review Liked"
        message = f"{request.user.first_name} liked your review!"
        content_object = review

    # --- New Follow ---
    elif type_of_notification == "new_follow" and follow_id:
        follow = Follow.objects.get(pk=follow_id)
        recipient = follow.following
        title = "User Followed"
        message = f"{sender.first_name} started following you!"
        content_object = follow

    # --- Barter Request ---
    elif type_of_notification == "barter_request" and barter_id:
        barter = BarterRequest.objects.get(pk=barter_id)
        recipient = barter.recipient
        title = "Barter Request"
        message = f"{sender.first_name} sent you a barter request!"
        content_object = barter

    # --- Barter Request Sent ---
    elif type_of_notification == 'barter_request_sent' and barter_id:
        barter = BarterRequest.objects.get(pk=barter_id)
        recipient = barter.requester
        title = "Barter Request Sent"
        message = f"You sent a barter request to {barter.recipient.first_name}."
        content_object = barter

    # --- Barter Accepted ---
    elif type_of_notification == "barter_accepted" and barter_id:
        barter = BarterRequest.objects.get(pk=barter_id)
        recipient = barter.requester
        title = "Barter Accepted"
        message = f"{sender.first_name} accepted your barter request!"
        content_object = barter

    # --- Barter Rejected ---
    elif type_of_notification == "barter_rejected" and barter_id:
        barter = BarterRequest.objects.get(pk=barter_id)
        recipient = barter.requester
        title = "Barter Rejected"
        message = f"{sender.first_name} rejected your barter request!"
        content_object = barter

    # --- Barter Counter Offer ---
    elif type_of_notification == "barter_counter" and barter_id:
        counter_offer = BarterCounter.objects.get(pk=barter_id)
        recipient = counter_offer.original_request.requester
        title = "Barter Counter Offered"
        message = f"{sender.first_name} made a counter offer!"
        content_object = counter_offer

    # --- Barter Completed ---
    elif type_of_notification == "barter_completed" and barter_id:
        barter = BarterRequest.objects.get(pk=barter_id)
        # Notify the other participant
        if sender == barter.requester:
            recipient = barter.recipient
        elif sender == barter.recipient:
            recipient = barter.requester
        else:
            return None  # safety check
        title = "Barter Completed"
        message = f"{sender.first_name} completed the barter with you!"
        content_object = barter

    # Safety check
    if recipient is None:
        return None

    # Create the Notification object
    notification = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=type_of_notification,
        title=title,
        message=message,
        content_object=content_object,
    )

    return notification
