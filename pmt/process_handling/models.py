from django.db import models
from django.conf import settings
from data_handling.models import EventLog


# Create your models here.


class ProcessModel(models.Model):
    """Model to describe process models"""

    process_model_id = models.AutoField(primary_key=True)
    process_model_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    process_model_log_name = models.ForeignKey(EventLog, on_delete=models.CASCADE)
    process_model_name = models.CharField(max_length=100, default="process_model_name")
    process_model_pnml_file = models.FileField(
        upload_to="process_models/pnml", null=True
    )
    process_model_bpmn_file = models.FileField(
        upload_to="process_models/bpmn", null=True
    )
    process_model_pnml_png = models.ImageField(
        upload_to="exported_pngs/pnml", null=True
    )
    process_model_pnml_frequency_png = models.ImageField(
        upload_to="exported_pngs/pnml", null=True
    )
    process_model_pnml_performance_png = models.ImageField(
        upload_to="exported_pngs/pnml", null=True
    )
    process_model_bpmn_png = models.ImageField(
        upload_to="exported_pngs/bpmn", null=True
    )

    def __int__(self):
        return self.process_model_id

    def delete(self, *args, **kwargs):
        self.process_model_pnml_file.delete()
        self.process_model_bpmn_file.delete()
        self.process_model_pnml_png.delete()
        self.process_model_bpmn_png.delete()
        self.process_model_pnml_frequency_png.delete()
        self.process_model_pnml_performance_png.delete()
        super().delete(*args, **kwargs)


class StatisticsData(models.Model):
    """Model to describe saved data"""
    statistics_id = models.AutoField(primary_key=True)
    event_log_id = models.IntegerField(null=True)
    distribution_case_duration_graph = models.FileField(
        upload_to="statistics/graphs/", null=True
    )
    distribution_events_time = models.FileField(
        upload_to="statistics/graphs/", null=True
    )
