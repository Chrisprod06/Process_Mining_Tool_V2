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
    CHOICES = [('containing','contained'),('intersect','intersecting')]
    choice = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect,label='')
    file_name = forms.CharField(label="file name")


class SelectFiltersFormDuration(forms.Form):
    min_duration = forms.CharField(label="Minimum Duration", required=False)
    max_duration = forms.CharField(label="Maximum Duration", required=False)
    CHOICES=[('days','days'),('hours','hours'),('minutes','minutes'),('seconds','seconds')]
    choice = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect,label='Type of input')
    file_name = forms.CharField(label="file name:")


class SelectFiltersFormStartEnd(forms.Form):
    CHOICES=[('start_act','start activity'),('end_act','end activity')]
    activity = forms.CharField(label="Activity")
    choice = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect,label='')
    frequent_box = forms.BooleanField(label="Frequent", required=False)
    file_name = forms.CharField(label="file name:")


class SelectFiltersFormAttributes(forms.Form):
    selected_attribute = forms.CharField(label="Attribute")
    CHOICE_ACT = [('activity','activity'),('resource','resource')]
    CHOICE_CONT = [('contain_act','containing'),('not_contain_act','not containing')]
    choice_act = forms.ChoiceField(choices=CHOICE_ACT, widget=forms.RadioSelect ,label='Type of input')
    choice_cont = forms.ChoiceField(choices=CHOICE_CONT, widget=forms.RadioSelect,label='')
    file_name = forms.CharField(label="file name:")


class SelectFiltersFormVariant(forms.Form):
    CHOICES=[('contain','containing'),('not_contain','not containing')]
    selected_variant = forms.CharField()
    choice = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect, label='')
    file_name = forms.CharField(label="file name:")



class SelectFiltersFormCaseSize(forms.Form):
    minimum_size = forms.CharField(label="minimum size:")
    maximum_size = forms.CharField(label="maximum size:")
    file_name = forms.CharField(label="file name:")


class SelectFiltersFormRework(forms.Form):
    reworked_activity = forms.CharField(label="rework activity:")
    occur_count = forms.CharField(label="occurrences:")
    file_name = forms.CharField(label="file name:")