from django.db import models
from django.conf import settings


# Create your models here.
class EventLog(models.Model):
    """Model to describe event logs"""

    event_log_id = models.AutoField(primary_key=True)
    event_log_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    event_log_name = models.CharField(max_length=100, default="event_log_name")
    event_log_file = models.FileField(upload_to="event_logs")

    def __str__(self):
        return self.event_log_name

    def delete(self, *args, **kwargs):
        self.event_log_file.delete()
        super().delete(*args, **kwargs)


