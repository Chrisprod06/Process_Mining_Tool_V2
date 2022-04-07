from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .forms import ProcessModelForm, DiscoverProcessModelForm, SelectEventLogAndProcessModelForm
from .models import ProcessModel
from core import pm4py_discovery, pm4py_statistics, pm4py_conformance
from data_handling.forms import SelectEventLogForm
from data_handling.models import EventLog


# Create your views here.


@login_required(login_url="/accounts/login")
def process_model_list(request):
    """View for displaying process models and actions"""
    process_models = ProcessModel.objects.all()
    template = "process_handling/process_model_list.html"
    context = {"process_models": process_models}
    return render(request, template, context)


@login_required(login_url="/accounts/login")
def process_model_detail(request, pk):
    """View to handle providing details for a single process model"""
    process_model = ProcessModel.objects.get(pk=pk)
    template = "process_handling/process_model_detail.html"
    context = {"process_model": process_model}
    return render(request, template, context)


@login_required(login_url="/accounts/login")
def process_model_create(request):
    """View to handle upload of a process model"""
    template = "process_handling/process_model_form.html"
    upload_process_model_form = ProcessModelForm()

    if request.method == "POST":
        upload_process_model_form = ProcessModelForm(request.POST, request.FILES)
        if upload_process_model_form.is_valid():
            if upload_process_model_form.save():
                messages.success(request, "Process Model added successfully!")
            else:
                messages.error(request, "Something went wrong! Please try again.")
            return redirect(reverse_lazy("process_handling:process_model_list"))
    context = {"form": upload_process_model_form}
    return render(request, template, context)


@login_required(login_url="/accounts/login")
def process_model_update(request, pk):
    """View to handle update of a certain process models"""
    process_model = ProcessModel.objects.get(pk=pk)
    template = "data_handling/event_log_form.html"
    update_process_model_form = ProcessModelForm(instance=process_model)
    if request.method == "POST":
        update_process_model_form = ProcessModelForm(request.POST, request.FILES)
        if update_process_model_form.is_valid():
            if update_process_model_form.save():
                messages.success(request, "Process Model updated successfully!")
            else:
                messages.error(request, "Something went wrong! Please try again.")
            return redirect(reverse_lazy("process_handling:process_model_list"))
    context = {"form": update_process_model_form}
    return render(request, template, context)


@login_required(login_url="/accounts/login")
def process_model_delete(request, pk):
    """View to handle deletion of process models"""
    if request.method == "POST":
        process_model = ProcessModel.objects.get(pk=pk)
        if process_model is None:
            messages.error(request, "Process Model not found!")
        else:
            process_model.delete()
            messages.success(request, "Process Model deleted successfully!")
    return redirect(reverse_lazy("process_handling:process_model_list"))


@login_required(login_url="/accounts/login")
def process_model_discover(request):
    """View for handling process model discovery"""
    template = "process_handling/process_model_discover.html"
    discover_process_model_form = DiscoverProcessModelForm()

    if request.method == "POST":
        discover_process_model_form = DiscoverProcessModelForm(request.POST)
        if discover_process_model_form.is_valid():
            # Get process model details
            new_process_model = discover_process_model_form.save(commit=False)
            event_log_name = str(new_process_model.process_model_log_name)
            process_model_name = new_process_model.process_model_name
            # Process model discovery

            pm4py_discovery.process_model_discovery(event_log_name, process_model_name)
            # Save new model
            new_process_model.process_model_pnml_file = (
                    "process_models/pnml/" + process_model_name + ".pnml"
            )
            new_process_model.process_model_bpmn_file = (
                    "process_models/bpmn/" + process_model_name + ".bpmn"
            )
            new_process_model.process_model_pnml_image = (
                    "exported_pngs/pnml/" + process_model_name + ".png"
            )
            new_process_model.process_model_bmpn_image = (
                    "exported_pngs/bpmn/" + process_model_name + ".png"
            )
            # Save the process model
            new_process_model.save()
            discover_process_model_form.save_m2m()
            return redirect(reverse_lazy("process_handling:process_model_list"))
    context = {"form": discover_process_model_form}
    return render(request, template, context)


def performance_dashboard(request, pk):
    """View to handle the render of performance dashboard"""
    template = "process_handling/performance_dashboard.html"
    selected_event_log = EventLog.objects.get(pk=pk)
    selected_event_log_id = selected_event_log.event_log_id
    statistics_results = pm4py_statistics.calculate_statistics(selected_event_log_id)

    context = {"statistics_results": statistics_results}
    return render(request, template, context)


def performance_dashboard_select(request):
    """View to handle the selection of event log for performance dashboard"""
    template = "process_handling/performance_dashboard_form.html"
    select_event_log_form = SelectEventLogForm()

    context = {"select_event_log_form": select_event_log_form}

    if request.method == "POST":
        select_event_log_form = SelectEventLogForm(request.POST)
        if select_event_log_form.is_valid():
            event_log_name = select_event_log_form.cleaned_data["event_log"]
            event_log = EventLog.objects.get(event_log_name=event_log_name)
            selected_event_log_id = event_log.event_log_id
            return redirect(
                reverse_lazy(
                    "process_handling:performance_dashboard",
                    kwargs={"pk": selected_event_log_id},
                )
            )

    return render(request, template, context)


def social_network_analysis(request, pk):
    """View to handle the render of social network analysis"""
    template = "process_handling/social_network_analysis.html"
    selected_event_log = EventLog.objects.get(pk=pk)
    selected_event_log_id = selected_event_log.event_log_id
    social_network_analysis_results = pm4py_statistics.calculate_social_network_analysis(selected_event_log_id)
    context = {
        "social_network_analysis_results": social_network_analysis_results
    }
    return render(request, template, context)


def social_network_analysis_select(request):
    """View to handle the selection of event log for social network analysis"""
    template = "process_handling/performance_dashboard_form.html"
    select_event_log_form = SelectEventLogForm()

    context = {"select_event_log_form": select_event_log_form}

    if request.method == "POST":
        select_event_log_form = SelectEventLogForm(request.POST)
        if select_event_log_form.is_valid():
            event_log_name = select_event_log_form.cleaned_data["event_log"]
            event_log = EventLog.objects.get(event_log_name=event_log_name)
            selected_event_log_id = event_log.event_log_id
            return redirect(
                reverse_lazy(
                    "process_handling:social_network_analysis",
                    kwargs={"pk": selected_event_log_id},
                )
            )

    return render(request, template, context)


def conformance_check(request, event_log_pk, process_model_pk):
    """View to handle te conformance check of an event log and process model"""
    template = "process_handling/conformance_check.html"
    token_replay_results = pm4py_conformance.perform_token_replay(event_log_pk, process_model_pk)
    context = {"token_replay_results": token_replay_results}
    return render(request, template, context)


def conformance_check_select(request):
    """View to handle the selection of an event log and process model for conformance checking"""
    template = "process_handling/conformance_check_form.html"
    select_event_log_process_model_form = SelectEventLogAndProcessModelForm()

    context = {
        "select_event_log_process_model_form": select_event_log_process_model_form
    }

    if request.method == "POST":
        select_event_log_process_model_form = SelectEventLogAndProcessModelForm(request.POST)
        if select_event_log_process_model_form.is_valid():
            event_log_name = select_event_log_process_model_form.cleaned_data["event_log"]
            process_model_id = select_event_log_process_model_form.cleaned_data["process_model"]
            event_log = EventLog.objects.get(event_log_name=event_log_name)
            process_model = ProcessModel.objects.get(process_model_id=process_model_id)
            selected_event_log_id = event_log.event_log_id
            selected_process_model_id = process_model.process_model_id
            return redirect(
                reverse_lazy(
                    "process_handling:conformance_check",
                    kwargs={"event_log_pk": selected_event_log_id,
                            "process_model_pk": selected_process_model_id}
                )
            )

    return render(request, template, context)
