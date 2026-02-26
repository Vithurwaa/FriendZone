from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
class Interest(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

# ================= PROFILE =================

class Profile(models.Model):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("na", "Prefer not to say"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    age = models.IntegerField(
    null=True,
    blank=True,
    validators=[MinValueValidator(13), MaxValueValidator(80)])
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="na")
    city = models.CharField(max_length=100, blank=True)
    interests = models.ManyToManyField(Interest, blank=True)

    def __str__(self):
        return self.user.username


# ================= CONNECTION =================

class Connection(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
    ]

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_requests")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_requests")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    class Meta:constraints = [
        models.UniqueConstraint(
            fields=['sender', 'receiver'],
            name='unique_connection'
        )
    ]
    def __str__(self):
        return f"{self.sender} → {self.receiver} ({self.status})"


# ================= ACTIVITY =================

class Activity(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("closed", "Closed"),
        ("completed", "Completed"),
    ]

    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()

    max_participants = models.IntegerField(default=5)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="open")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# ================= ACTIVITY JOIN =================

class ActivityJoin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} joined {self.activity.title}"
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
class Report(models.Model):
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    reported_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reports_received"
    )
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reporter} reported {self.reported_user}"