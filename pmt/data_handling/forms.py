from django.forms import ModelForm
from django import forms

from .models import EventLog


class EventLogForm(ModelForm):
    """Form used for handling event logs"""

    class Meta:
        model = EventLog
        fields = "__all__"


class CustomEventLogModelChoiceField(forms.ModelChoiceField):
    """Class to return text the name but value the id"""

    def label_from_instance(self, object):
        return object.event_log_name


class SelectEventLogForm(forms.Form):
    """Form used for selecting event log"""

    event_log = CustomEventLogModelChoiceField(queryset=EventLog.objects.all())

class SelectFiltersFormDate(forms.Form):
    """Form to select filters"""

    # filter_time = forms.BooleanField(label='filter by time')
    # filter_date = forms.BooleanField(label='filter by date')

    start_time = forms.DateTimeField(label="starting time: ", required=False)
    end_time = forms.DateTimeField(label="ending time: ", required=False)
    file_name = forms.CharField(label="file name")


class SelectFiltersFormDuration(forms.Form):
    min_duration = forms.CharField(label="Minimum Duration", required=False)
    max_duration = forms.CharField(label="Maximum Duration", required=False)
    days = forms.BooleanField(label="Days", required=False)
    hours = forms.BooleanField(label="Hours", required=False)
    minutes = forms.BooleanField(label="Minutes", required=False)
    seconds = forms.BooleanField(label="Seconds", required=False)
    file_name = forms.CharField(label="file name:")


class SelectFiltersFormStartEnd(forms.Form):
    activity = forms.CharField(label="Activity")
    start_checkbox = forms.BooleanField(label="start activity", required=False)
    end_checkbox = forms.BooleanField(label="end activity", required=False)
    frequent_checkbox = forms.BooleanField(label="most frequent", required=False)
    file_name = forms.CharField(label="file name:")


class SelectFiltersFormAttributes(forms.Form):
    selected_attribute = forms.CharField(label="Attribute")
    activity_name = forms.BooleanField(label="activity", required=False)
    activity_resource = forms.BooleanField(label="resource", required=False)
    activity_containing = forms.BooleanField(label="Containing", required=False)
    activity_not_containing = forms.BooleanField(label="Not Containing", required=False)
    file_name = forms.CharField(label="file name:")


class SelectFiltersFormVariant(forms.Form):
    selected_variant = forms.CharField()
    file_name = forms.CharField(label="file name:")


class SelectFiltersFormNumeric(forms.Form):
    selected_number = forms.CharField(label="number:")
    file_name = forms.CharField(label="file name:")
