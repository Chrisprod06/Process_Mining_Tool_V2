from django.db import models
from django.conf import settings
from data_handling.models import EventLog


# Create your models here.

class ProcessModel(models.Model):
    """Model to describe process models"""

    # Choices of algorithms for process discovery
    ALPHA_MINER = "alpha_miner"
    INDUCTIVE_MINER = "inductive_miner"
    HEURISTIC_MINER = "heuristic_miner"

    DISCOVERY_ALGORITHMS = [
        (ALPHA_MINER, "Alpha Miner"),
        (INDUCTIVE_MINER, "Inductive Miner"),
        (HEURISTIC_MINER, "Heuristic Miner"),
    ]

    process_model_id = models.AutoField(primary_key=True)
    process_model_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    process_model_log_name = models.ForeignKey(EventLog, on_delete=models.CASCADE)
    process_model_name = models.CharField(max_length=100, default="process_model_name")
    process_model_algorithm = models.CharField(
        max_length=100, choices=DISCOVERY_ALGORITHMS
    )
    process_model_file = models.FileField(upload_to="process_models")
    process_model_image = models.ImageField(
        upload_to="exported_pngs", default="/PMT/media/produced_pngs/default.png"
    )

    def __int__(self):
        return self.process_model_id

    def delete(self, *args, **kwargs):
        self.process_model_file.delete()
        self.process_model_image.delete()
        super().delete(*args, **kwargs)
