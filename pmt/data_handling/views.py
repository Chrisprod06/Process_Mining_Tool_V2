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
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.statistics.traces.generic.log import case_statistics

from .models import EventLog

from .forms import EventLogForm, SelectFiltersFormDate, SelectFiltersFormDuration, SelectFiltersFormStartEnd, \
    SelectFiltersFormNumeric, SelectFiltersFormAttributes, SelectFiltersFormVariant


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
    form_duration = SelectFiltersFormDuration()
    form_start_end = SelectFiltersFormStartEnd()
    form_attributes = SelectFiltersFormAttributes()
    form_variant = SelectFiltersFormVariant()
    form_numeric = SelectFiltersFormNumeric()
    if request.method == "POST":
        event_log_path = event_log.event_log_file
        log = xes_importer.apply("media/" + str(event_log_path))
        if "submitFilterDate" in request.POST:
            form_date = SelectFiltersFormDate(request.POST)
            if form_date.is_valid():
                start = form_date.cleaned_data.get("start_time")
                end = form_date.cleaned_data.get("end_time")
                start = start.replace(tzinfo=None)
                end = end.replace(tzinfo=None)
                file_name = form_date.cleaned_data.get("file_name")
                filtered_log = timestamp_filter.filter_traces_contained(log, start, end)
        if "submitFilterDuration" in request.POST:
            form_duration = SelectFiltersFormDuration(request.POST)
            print("first if = success")
            if form_duration.is_valid():
                print("form is valid")
                days = form_duration.cleaned_data.get("days")
                hours = form_duration.cleaned_data.get("hours")
                minutes = form_duration.cleaned_data.get("minutes")
                seconds = form_duration.cleaned_data.get("seconds")
                min = int(form_duration.cleaned_data.get("min_duration"))
                max = int(form_duration.cleaned_data.get("max_duration"))
                file_name = form_duration.cleaned_data.get("file_name")
                min_duration = 0
                max_duration = 0
                if days == True:
                    min_duration = 24 * 60 * 60 * min
                    max_duration = 24 * 60 * 60 * max
                if hours == True:
                    min_duration = 60 * 60 * min
                    max_duration = 60 * 60 * max
                if minutes == True:
                    min_duration = 60 * min
                    max_duration = 60 * max
                if seconds == True:
                    min_duration = min
                    max_duration = max
                filtered_log = case_filter.filter_case_performance(log, min_duration, max_duration)
                print("inner if = success")
        if "submitFilterStartEnd" in request.POST:
            form_start_end = SelectFiltersFormStartEnd(request.POST)
            if form_start_end.is_valid():
                activity = form_start_end.cleaned_data.get("activity")
                start_checkbox = form_start_end.cleaned_data.get("start_checkbox")
                end_checkbox = form_start_end.cleaned_data.get("end_checkbox")
                frequent_checkbox = form_start_end.cleaned_data.get("frequent_checkbox")
                file_name = form_start_end.cleaned_data.get("file_name")
                activity = " " + activity
                if start_checkbox == True:
                    if frequent_checkbox == False:
                        log_start = start_activities_filter.get_start_activities(log)
                        filtered_log = start_activities_filter.apply(log, [activity])
                        print(log_start)
                        print(activity)
                        # xes_exporter.apply(filtered_log, "media/" + file_name + ".xes")
                    else:
                        # log_af_sa
                        filtered_log = start_activities_filter.apply_auto_filter(log, parameters={
                            start_activities_filter.Parameters.DECREASING_FACTOR: 0.5})
                        # xes_exporter.apply(log_af_sa, "media" + file_name + ".xes")
                elif end_checkbox == True:
                    end_activities = end_activities_filter.get_end_activities(log)
                    filtered_log = end_activities_filter.apply(log, [activity])
                    print(end_activities)
        if "submitFilterAttributes" in request.POST:
            form_attributes = SelectFiltersFormAttributes(request.POST)
            if form_attributes.is_valid():
                selected_attribute = form_attributes.cleaned_data.get("selected_attribute")
                selected_attribute = " " + selected_attribute
                li = list(selected_attribute.split(","))
                file_name = form_attributes.cleaned_data.get("file_name")
                activity_name_box = form_attributes.cleaned_data.get("activity_name")
                activity_resource_box = form_attributes.cleaned_data.get("activity_resource")
                containing_box = form_attributes.cleaned_data.get("activity_containing")
                not_containing_box = form_attributes.cleaned_data.get("activity_not_containing")
                activities = attributes_filter.get_attribute_values(log, "concept:name")
                resources = attributes_filter.get_attribute_values(log, "org:resource")
                if containing_box == True:
                    # tracefilter_log_pos
                    if activity_name_box == True:
                        filtered_log = attributes_filter.apply(log, li, parameters={
                            attributes_filter.Parameters.ATTRIBUTE_KEY: "concept:name",
                            attributes_filter.Parameters.POSITIVE: True})
                        print(activities)
                        print(resources)
                        print(li)
                    if activity_resource_box == True:
                        filtered_log = attributes_filter.apply(log, li, parameters={
                            attributes_filter.Parameters.ATTRIBUTE_KEY: "org:resource",
                            attributes_filter.Parameters.POSITIVE: True})
                        print(activities)
                        print(resources)
                        print(li)
                elif not_containing_box == True:
                    # tracefilter_log_neg
                    if activity_name_box == True:
                        filtered_log = attributes_filter.apply(log, li, parameters={
                            attributes_filter.Parameters.ATTRIBUTE_KEY: "concept:name",
                            attributes_filter.Parameters.POSITIVE: False})
                        print(activities)
                        print(resources)
                        print(li)
                    if activity_resource_box == True:
                        # tracefilter_log_neg
                        filtered_log = attributes_filter.apply(log, li, parameters={
                            attributes_filter.Parameters.ATTRIBUTE_KEY: "org:resource",
                            attributes_filter.Parameters.POSITIVE: False})
        if "submitFilterVariants" in request.POST:
            form_variant = SelectFiltersFormVariant(request.POST)
            context = {}
            if form_variant.is_valid():
                selected_variant = form_variant.cleaned_data.get("selected_variant")
                selected_variant = " " + selected_variant
                li = list(selected_variant.split(","))
                file_name = form_variant.cleaned_data.get("file_name")
                variants = variants_filter.get_variants(log)
                print(variants)
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                variants_count = case_statistics.get_variant_statistics(log)
                variants_count = sorted(variants_count, key=lambda x: x['count'], reverse=True)
                print(variants_count)
                print("---------------------------------------------------------------------------------------")
                for i in range(len(variants_count)):
                    for j in variants_count[i]:
                        print(j, variants_count[i][j])
                    # print(variants_count[i])
                print(li)
                # list from input not workling
                # filtered_log = variants_filter.apply(log,  [[li]], parameters={variants_filter.Parameters.POSITIVE: False})
                filtered_log = variants_filter.apply(log, [li])
                if variants_count:
                    context["variants_count"] = variants_count
        if "submitFilterNumeric" in request.POST:
            form_numeric = SelectFiltersFormNumeric(request.POST)
            if form_numeric.is_valid():
                selected_number = form_numeric.cleaned_data.get("selected_number")
                file_name = form_variant.cleaned_data.get("file_name")
        xes_exporter.apply(filtered_log, "media/event_logs/" + file_name + ".xes")
        event_log_file = "event_logs/" + file_name + ".xes"
        new_filtered_event_log = EventLog()
        new_filtered_event_log.event_log_owner = event_log.event_log_owner
        new_filtered_event_log.event_log_name = file_name
        new_filtered_event_log.event_log_file = event_log_file
        new_filtered_event_log.save()
    context = {"event_log": event_log, "form_date": form_date, "form_duration": form_duration,
               "form_start_end": form_start_end, "form_attributes": form_attributes, "form_variant": form_variant}
    return render(request, template, context)
