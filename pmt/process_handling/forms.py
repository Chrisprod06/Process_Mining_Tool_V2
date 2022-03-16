from django.forms import ModelForm
from django import forms

from .models import ProcessModel


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
