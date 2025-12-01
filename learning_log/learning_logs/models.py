from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Topic(models.Model):
    """A topic the user is learning about."""
    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topics')


    def __str__(self):
        """Return a string representation of the model."""
        return self.text
    
class Entry(models.Model):
    """Something specific learned about a topic."""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    date_worked = models.DateField(null=True, blank=True)
    hours_spent = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    exam_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name_plural = "entries"
        ordering = ['-date_added']

    def __str__(self):
        """Return a string representation of the model."""
        return f"{self.text[:50]}..."


