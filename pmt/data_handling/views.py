from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.dateparse import parse_datetime
from pm4py.algo.filtering.log.timestamp import timestamp_filter

# imports for import/export
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.algo.filtering.log.cases import case_filter
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.algo.filtering.log.start_activities import start_activities_filter
from pm4py.algo.filtering.log.end_activities import end_activities_filter

from .models import EventLog
from .forms import EventLogForm, SelectFiltersFormDate, SelectFiltersFormDuration, SelectFiltersFormStartEnd, \
    SelectFiltersFormAttributes, SelectFiltersFormVariant


@login_required(login_url="/accounts/login")
def event_log_list(request):
    """View for displaying event logs and actions"""
    event_logs = EventLog.objects.all()
    template = "data_handling/event_log_list.html"
    context = {"event_logs": event_logs}
    return render(request, template, context)


@login_required(login_url="/accounts/login")
def event_log_detail(request, pk):
    """View to handle providing details for a single event log"""
    event_log = EventLog.objects.get(pk=pk)
    template = "data_handling/event_log_detail.html"
    file_path = "media/" + str(event_log.event_log_file)
    file = open(file_path, "r")
    event_log_file_content = file.read()
    context = {"event_log": event_log, "event_log_file_content": event_log_file_content}
    return render(request, template, context)


@login_required(login_url="/accounts/login")
def event_log_create(request):
    """View to handle upload of an event log"""
    template = "data_handling/event_log_form.html"
    upload_event_log_form = EventLogForm()

    if request.method == "POST":
        upload_event_log_form = EventLogForm(request.POST, request.FILES)
        if upload_event_log_form.is_valid():
            if upload_event_log_form.save():
                messages.success(request, "Event log added successfully!")
            else:
                messages.error(request, "Something went wrong! Please try again.")
            return redirect(reverse_lazy("data_handling:event_log_list"))
    context = {"form": upload_event_log_form}
    return render(request, template, context)


@login_required(login_url="/accounts/login")
def event_log_update(request, pk):
    """View to handle update of a certain event log"""
    event_log = EventLog.objects.get(pk=pk)
    template = "data_handling/event_log_form.html"
    update_event_log_form = EventLogForm(instance=event_log)
    if request.method == "POST":
        update_event_log_form = EventLogForm(request.POST, request.FILES)
        if update_event_log_form.is_valid():
            if update_event_log_form.save():
                messages.success(request, "Event log updated successfully!")
            else:
                messages.error(request, "Something went wrong! Please try again.")
            return redirect(reverse_lazy("data_handling:event_log_list"))
    context = {"form": update_event_log_form}
    return render(request, template, context)


@login_required(login_url="/accounts/login")
def event_log_delete(request, pk):
    """View to handle deletion of event logs"""
    if request.method == "POST":
        event_log = EventLog.objects.get(pk=pk)
        if event_log is None:
            messages.error(request, "Event Log not found!")
        else:
            event_log.delete()
            messages.success(request, "Event Log deleted successfully!")
    return redirect(reverse_lazy("data_handling:event_log_list"))


@login_required(login_url="/accounts/login")
def event_log_filter(request, pk):
    """View to handle providing details for a single event log"""
    event_log = EventLog.objects.get(pk=pk)
    template = "data_handling/event_log_filter.html"
    form_date = SelectFiltersFormDate()
    formDuration = SelectFiltersFormDuration()
    formStartEnd = SelectFiltersFormStartEnd()
    formAttribute = SelectFiltersFormAttributes()
    formVariant = SelectFiltersFormVariant()
    if request.method == "POST":
        if "submitFilterDate" in request.POST:
            form_date = SelectFiltersFormDate(request.POST)
            if form_date.is_valid():
                start = form_date.cleaned_data.get("start_time")
                end = form_date.cleaned_data.get("end_time")

                start = start.replace(tzinfo=None)
                end = end.replace(tzinfo=None)
                file_name = form_date.cleaned_data.get("file_name")

                event_log_path = event_log.event_log_file
                log = xes_importer.apply("media/" + str(event_log_path))

                filtered_log = timestamp_filter.filter_traces_contained(log, start, end)
                xes_exporter.apply(filtered_log, "media/event_logs/" + file_name + ".xes")

                event_log_file = "event_logs/" + file_name + ".xes"

                new_filtered_event_log = EventLog()
                new_filtered_event_log.event_log_owner = event_log.event_log_owner
                new_filtered_event_log.event_log_name = file_name
                new_filtered_event_log.event_log_file = event_log_file
                new_filtered_event_log.save()

                return redirect(reverse_lazy("data_handling:event_log_list"))
    context = {"event_log": event_log, "formDate": form_date, "formDuration": formDuration,
               "formStartEnd": formStartEnd, "formAttribute": formAttribute, "formVariant": formVariant}
    return render(request, template, context)


@login_required(login_url="/accounts/login")
def filter_timestamp(request, pk):
    """View to filter a log with given timestamp"""
    event_log = EventLog.objects.get(pk=pk)
    form = SelectFiltersFormDate(request.POST)
    if form.is_valid():
        start = form.cleaned_data.get("start_time")
        end = form.cleaned_data.get("end_time")
        file_name = form.cleaned_data.get("file_name")
        log = xes_importer.apply(event_log)
        filtered_log = timestamp_filter.filter_traces_contained(log, start, end)
        xes_exporter.apply(filtered_log, "media/" + file_name + ".xes")


@login_required(login_url="/accounts/login")
def filter_case_start_end_activity(request, pk):
    """View to filter a log with a given case variant"""
    event_log = EventLog.objects.get(pk=pk)
    submitbutton = request.POST.get("submit")
    form = SelectFiltersFormStartEnd(request.POST)
    if form.is_valid():
        activity = form.cleaned_data.get("activity")
        start_checkbox = form.cleaned_data.get("start_checkbox")
        end_checkbox = form.cleaned_data.get("end_checkbox")
        frequent_checkbox = form.cleaned_data.get("frequent_checkbox")
        file_name = form.cleaned_data.get("file_name")
        log = xes_importer.apply(event_log)
        if start_checkbox.equals(True):
            if frequent_checkbox.equals(False):
                # log_start = start_activities_filter.get_start_activities(log)
                filtered_log = start_activities_filter.apply(log, [activity])
                xes_exporter.apply(filtered_log, "media/" + file_name + ".xes")
            else:
                log_af_sa = start_activities_filter.apply_auto_filter(log, parameters={
                    start_activities_filter.Parameters.DECREASING_FACTOR: 0.6})
                xes_exporter.apply(log_af_sa, "media" + file_name + ".xes")
        elif end_checkbox.equals(True):
            # end_activities = end_activities_filter.get_end_activities(log)
            filtered_log = end_activities_filter.apply(log, [activity])
            xes_exporter.apply(filtered_log, "media" + file_name + ".xes")


@login_required(login_url="/accounts/login")
def filter_case_variant(request, pk):
    """View to filter a log with a given case variant"""
    event_log = EventLog.objects.get(pk=pk)
    submitbutton = request.POST.get("submit")
    form = SelectFiltersFormVariant(request.POST)


@login_required(login_url="/accounts/login")
def filter_duration(request, pk):
    """View to filter a log given the duration of a case"""
    event_log = EventLog.objects.get(pk=pk)
    submitbutton = request.POST.get("submit")
    form = SelectFiltersFormDuration(request.POST)
    if form.isvalid():
        min_duration = form.cleaned_data.get("min_duration")
        max_duration = form.cleaned_data.get("max_duration")
        file_name = form.cleaned_data.get("file_name")
        log = xes_importer.apply(event_log)
        filtered_log = case_filter.filter_case_performance(log, min_duration, max_duration)
        xes_exporter.apply(log, "media/" + file_name + ".xes")


@login_required(login_url="/accounts/login")
def filter_attributes(request, pk):
    """View to filter a log given the duration of a case"""
    event_log = EventLog.objects.get(pk=pk)
    submitbutton = request.POST.get("submit")
    form = SelectFiltersFormAttributes(request.POST)
    if form.isvalid():
        selected_attribute = form.cleaned_data.get("selected_attribute")
        file_name = form.cleaned_data.get("file_name")
        containing_box = form.cleaned_data.get("activity_containing")
        not_containing_box = form.cleaned_data.get("activity_not_containing")
        if containing_box.equals(True):
            activities = attributes_filter.get_attribute_values(event_log, "concept:name")
            resources = attributes_filter.get_attribute_values(event_log, "org:resource")
            tracefilter_log_pos = attributes_filter.apply(event_log, [selected_attribute],
                                                          parameters={
                                                              attributes_filter.Parameters.ATTRIBUTE_KEY: "org:resource",
                                                              attributes_filter.Parameters.POSITIVE: True})
            xes_exporter.apply(tracefilter_log_pos, "media/" + file_name + ".xes")
        elif not_containing_box.equals(True):
            tracefilter_log_neg = attributes_filter.apply(event_log, [selected_attribute],
                                                          parameters={
                                                              attributes_filter.Parameters.ATTRIBUTE_KEY: "org:resource",
                                                              attributes_filter.Parameters.POSITIVE: False})
            xes_exporter.apply(tracefilter_log_neg, "media/" + file_name + ".xes")
