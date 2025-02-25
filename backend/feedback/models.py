from django.db import models
from django.conf import settings
from boards.models import Board

class Tag(models.Model):
    
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default="#6c757d")  
    
    def __str__(self):
        return self.name

class Feedback(models.Model):
    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
        PLANNED = 'PLANNED', 'Planned'
        COMPLETED = 'COMPLETED', 'Completed'
        CLOSED = 'CLOSED', 'Closed'
    
    class Type(models.TextChoices):
        FEATURE_REQUEST = 'FEATURE_REQUEST', 'Feature Request'
        BUG_REPORT = 'BUG_REPORT', 'Bug Report'
        IMPROVEMENT = 'IMPROVEMENT', 'Improvement'
        QUESTION = 'QUESTION', 'Question'
        OTHER = 'OTHER', 'Other'
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='feedback_items'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_feedback'
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.OPEN
    )
    feedback_type = models.CharField(
        max_length=15,
        choices=Type.choices,
        default=Type.FEATURE_REQUEST
    )
    tags = models.ManyToManyField(Tag, related_name='feedback_items', blank=True)
    priority = models.PositiveSmallIntegerField(default=0)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Upvote(models.Model):
    
    feedback = models.ForeignKey(
        Feedback,
        on_delete=models.CASCADE,
        related_name='upvotes'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='upvoted_feedback'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('feedback', 'user')

    def __str__(self):
        return f"{self.user.username} upvoted {self.feedback.title}"