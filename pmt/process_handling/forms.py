from django.forms import ModelForm
from django import forms

from .models import ProcessModel

from data_handling.models import EventLog
from data_handling.forms import CustomEventLogModelChoiceField


class ProcessModelForm(ModelForm):
    """Form used for upload/modify process models"""

    class Meta:
        model = ProcessModel
        fields = "__all__"


class DiscoverProcessModelForm(ModelForm):
    """Form used for discovering process models"""

    class Meta:
        model = ProcessModel
        fields = [
            "process_model_id",
            "process_model_owner",
            "process_model_log_name",
            "process_model_name",
        ]


class CustomProcessModelModelChoiceField(forms.ModelChoiceField):
    """Class to return text the name but value the id"""

    def label_from_instance(self, object):
        return object.process_model_name


class SelectProcessModelForm(forms.Form):
    """Form used for selecting process model"""

    process_model = CustomProcessModelModelChoiceField(
        queryset=ProcessModel.objects.all()
    )


class SelectEventLogAndProcessModelForm(forms.Form):
    """Form used for selecting event log and process model"""
    event_log = CustomEventLogModelChoiceField(queryset=EventLog.objects.all())
    process_model = CustomProcessModelModelChoiceField(
        queryset=ProcessModel.objects.all()
    )


class PlayoutDetailsForm(forms.Form):
    """Form used for filling details required for play out"""

    playouts = [
        ("basic", "Basic"),
        ("extensive", "Extensive")
    ]

    process_model = CustomProcessModelModelChoiceField(
        queryset=ProcessModel.objects.all()
    )
    type_of_playout = forms.ChoiceField(choices=playouts)

    number_of_traces = forms.IntegerField()

class MonteCarloDetailsForm(forms.Form):
    """Form used for filling details required for montecarlo"""
    event_log = CustomEventLogModelChoiceField(queryset=EventLog.objects.all())
    case_arrival_ratio = forms.IntegerField()