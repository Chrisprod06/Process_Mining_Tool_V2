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
import pm4py
from .models import EventLog

from .forms import EventLogForm, SelectFiltersFormDate, SelectFiltersFormDuration, SelectFiltersFormStartEnd, \
    SelectFiltersFormAttributes, SelectFiltersFormVariant, SelectFiltersFormCaseSize, SelectFiltersFormRework


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
    event_log_path = event_log.event_log_file
    log = xes_importer.apply("media/" + str(event_log_path))
    # for start end
    log_start = start_activities_filter.get_start_activities(log)
    # for attributes
    activities_atrr = attributes_filter.get_attribute_values(log, "concept:name")
    resources_atrr = attributes_filter.get_attribute_values(log, "org:resource")
    # for variants
    variants_dict = case_statistics.get_variant_statistics(log)
    variants_dict = sorted(variants_dict, key=lambda x: x['count'], reverse=True)
    template = "data_handling/event_log_filter.html"
    form_date = SelectFiltersFormDate()
    form_duration = SelectFiltersFormDuration()
    form_start_end = SelectFiltersFormStartEnd()
    form_attributes = SelectFiltersFormAttributes()
    form_variant = SelectFiltersFormVariant()
    form_case_size = SelectFiltersFormCaseSize()
    form_rework = SelectFiltersFormRework()
    submit_active = ""
    variants_count = []
    log_start_end = {}
    activities_resources = []
    if request.method == "POST":
        if "submitFilterDate" in request.POST:
            form_date = SelectFiltersFormDate(request.POST)
            if form_date.is_valid():
                start = form_date.cleaned_data.get("start_time")
                end = form_date.cleaned_data.get("end_time")
                start = start.strftime("%Y-%m-%d %H:%M:%S")
                end = end.strftime("%Y-%m-%d %H:%M:%S")
                file_name = form_date.cleaned_data.get("file_name")
                choice = form_date.cleaned_data.get("choice")
                if choice == 'containing':
                    filtered_log = timestamp_filter.filter_traces_contained(log, start, end)
                if choice == 'intersect':
                    filtered_log = timestamp_filter.filter_traces_intersecting(log, start, end)
                submit_active = "date"
                messages.success(request, "Event log created successfully!")
        if "submitFilterDuration" in request.POST:
            form_duration = SelectFiltersFormDuration(request.POST)
            if form_duration.is_valid():
                choice = form_duration.cleaned_data.get("choice")
                min = int(form_duration.cleaned_data.get("min_duration"))
                max = int(form_duration.cleaned_data.get("max_duration"))
                file_name = form_duration.cleaned_data.get("file_name")
                min_duration = 0
                max_duration = 0
                if choice == 'days':
                    min_duration = 24 * 60 * 60 * min
                    max_duration = 24 * 60 * 60 * max
                if choice == 'hours':
                    min_duration = 60 * 60 * min
                    max_duration = 60 * 60 * max
                if choice == 'minutes':
                    min_duration = 60 * min
                    max_duration = 60 * max
                if choice == 'seconds':
                    min_duration = min
                    max_duration = max
                filtered_log = case_filter.filter_case_performance(log, min_duration, max_duration)
                submit_active = "duration"
        if "submitFilterStartEnd" in request.POST:
            form_start_end = SelectFiltersFormStartEnd(request.POST)
            if form_start_end.is_valid():
                activity = form_start_end.cleaned_data.get("activity")
                choice = form_start_end.cleaned_data.get("choice")
                frequent_checkbox = form_start_end.cleaned_data.get("frequent_box")
                file_name = form_start_end.cleaned_data.get("file_name")
                if choice == 'start_act':
                    if frequent_checkbox == False:
                        filtered_log = start_activities_filter.apply(log, [activity])
                        log_start_end = start_activities_filter.get_start_activities(filtered_log)
                    else:
                        filtered_log = start_activities_filter.apply_auto_filter(log, parameters={
                            start_activities_filter.Parameters.DECREASING_FACTOR: 0.5})
                elif choice == 'end_act':
                    filtered_log = end_activities_filter.apply(log, [activity])
                    log_start_end = end_activities_filter.get_end_activities(filtered_log)
                    submit_active = "start_end"
        if "submitFilterAttributes" in request.POST:
            form_attributes = SelectFiltersFormAttributes(request.POST)
            if form_attributes.is_valid():
                selected_attribute = form_attributes.cleaned_data.get("selected_attribute")
                li = list(selected_attribute.split(","))
                file_name = form_attributes.cleaned_data.get("file_name")
                choice_act = form_attributes.cleaned_data.get("choice_act")
                choice_cont = form_attributes.cleaned_data.get("choice_cont")
                if choice_cont == 'contain_act':
                    # tracefilter_log_pos
                    if choice_act == 'activity':
                        filtered_log = attributes_filter.apply(log, li, parameters={
                            attributes_filter.Parameters.ATTRIBUTE_KEY: "concept:name",
                            attributes_filter.Parameters.POSITIVE: True})
                        activities_resources = attributes_filter.get_attribute_values(filtered_log, "concept:name")
                    if choice_act == 'resource':
                        filtered_log = attributes_filter.apply(log, li, parameters={
                            attributes_filter.Parameters.ATTRIBUTE_KEY: "org:resource",
                            attributes_filter.Parameters.POSITIVE: True})
                        activities_resources = attributes_filter.get_attribute_values(filtered_log, "org:resource")
                elif choice_cont == 'not_contain_act':
                    # tracefilter_log_neg
                    if choice_act == 'activity':
                        filtered_log = attributes_filter.apply(log, li, parameters={
                            attributes_filter.Parameters.ATTRIBUTE_KEY: "concept:name",
                            attributes_filter.Parameters.POSITIVE: False})
                        activities_resources = attributes_filter.get_attribute_values(filtered_log, "concept:name")
                    if choice_act == 'resource':
                        # tracefilter_log_neg
                        filtered_log = attributes_filter.apply(log, li, parameters={
                            attributes_filter.Parameters.ATTRIBUTE_KEY: "org:resource",
                            attributes_filter.Parameters.POSITIVE: False})
                        activities_resources = attributes_filter.get_attribute_values(filtered_log, "org:resource")
                submit_active = "attributes"
        if "submitFilterVariants" in request.POST:
            form_variant = SelectFiltersFormVariant(request.POST)
            context = {}
            if form_variant.is_valid():
                choice = form_variant.cleaned_data.get("choice")
                contain_var_box = form_variant.cleaned_data.get("contain_var_box")
                selected_variant = form_variant.cleaned_data.get("selected_variant")
                li = list(selected_variant.split(";"))
                file_name = form_variant.cleaned_data.get("file_name")
                if choice == 'contain':
                    filtered_log = variants_filter.apply(log, li)
                else:
                    filtered_log = variants_filter.apply(log, li,
                                                         parameters={variants_filter.Parameters.POSITIVE: False})
                variants_count = case_statistics.get_variant_statistics(filtered_log)
                variants_count = sorted(variants_count, key=lambda x: x['count'], reverse=True)
                submit_active = "variants"
        if "submitFiltersCaseSize" in request.POST:
            form_case_size = SelectFiltersFormCaseSize(request.POST)
            if form_case_size.is_valid():
                minimum_size = int(form_case_size.cleaned_data.get("minimum_size"))
                maximum_size = int(form_case_size.cleaned_data.get("maximum_size"))
                file_name = form_case_size.cleaned_data.get("file_name")
                filtered_log = pm4py.filter_case_size(log, minimum_size, maximum_size)
                submit_active = "case_size"
        if "submitFiltersFormRework" in request.POST:
            form_rework = SelectFiltersFormRework(request.POST)
            if form_rework.is_valid():
                reworked = form_rework.cleaned_data.get("reworked_activity")
                occur_count = int(form_rework.cleaned_data.get("occur_count"))
                file_name = form_rework.cleaned_data.get("file_name")
                filtered_log = pm4py.filter_activities_rework(log, reworked, occur_count)
                submit_active = "rework"
        xes_exporter.apply(filtered_log, "media/event_logs/" + file_name + ".xes")
        event_log_file = "event_logs/" + file_name + ".xes"
        new_filtered_event_log = EventLog()
        new_filtered_event_log.event_log_owner = event_log.event_log_owner
        new_filtered_event_log.event_log_name = file_name
        new_filtered_event_log.event_log_file = event_log_file
        new_filtered_event_log.save()
    context = {"event_log": event_log, "form_date": form_date, "form_duration": form_duration,
               "form_start_end": form_start_end, "form_attributes": form_attributes, "form_variant": form_variant,
               "form_case_size": form_case_size, "form_rework": form_rework, "submit_active": submit_active,
               "variants_count": variants_count,
               "activities_resources": activities_resources, "log_start_end": log_start_end,
               "variants_dict": variants_dict, "log_start": log_start, "activities_atrr": activities_atrr,
               "resources_atrr": resources_atrr}
    print(submit_active)
    return render(request, template, context)
