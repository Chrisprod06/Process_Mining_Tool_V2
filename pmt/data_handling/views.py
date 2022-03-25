from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy

from .models import EventLog
from .forms import EventLogForm, SelectFilter


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
    context = {"event_log": event_log,
               "event_log_file_content": event_log_file_content}
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
def select_filters(request):
    """View to handle filtering"""
    select_filters_form = SelectFilter()
    template = ""

    context= {"select_filters_form": select_filters_form}
    return render(request,template,context)