from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .forms import ProcessModelForm, DiscoverProcessModelForm, SelectEventLogAndProcessModelForm, PlayoutDetailsForm, \
    MonteCarloDetailsForm
from .models import ProcessModel, StatisticsData
from core import pm4py_discovery, pm4py_statistics, pm4py_conformance, pm4py_simulation
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
    event_log = process_model.process_model_log_name
    file_path = "media/" + str(event_log.event_log_file)
    file = open(file_path, "r")
    event_log_file_content = file.read()
    template = "process_handling/process_model_detail.html"
    context = {"process_model": process_model,
               "event_log_file_content": event_log_file_content}
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
    template = "process_handling/process_model_discover_form.html"
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
            new_process_model.process_model_pnml_png = (
                    "exported_pngs/pnml/" + process_model_name + ".png"
            )
            new_process_model.process_model_pnml_frequency_png = (
                    "exported_pngs/pnml/" + process_model_name + "_frequency.png"
            )
            new_process_model.process_model_pnml_performance_png = (
                    "exported_pngs/pnml/" + process_model_name + "_performance.png"
            )
            new_process_model.process_model_bpmn_png = (
                    "exported_pngs/bpmn/" + process_model_name + ".png"
            )
            # Save the process model
            new_process_model.save()
            discover_process_model_form.save_m2m()
            return redirect(reverse_lazy("process_handling:process_model_list"))
    context = {"form": discover_process_model_form}
    return render(request, template, context)


@login_required(login_url="/accounts/login")
def performance_dashboard(request, pk):
    """View to handle the render of performance dashboard"""
    template = "process_handling/performance_dashboard.html"
    selected_event_log = EventLog.objects.get(pk=pk)
    selected_event_log_id = selected_event_log.event_log_id
    selected_event_log_type = selected_event_log.event_log_type
    selected_event_log_name = selected_event_log.event_log_name

    statistics_interval_results = {}

    statistics_single_results = pm4py_statistics.calculate_statistics(selected_event_log_id)
    if selected_event_log_type == "interval":
        statistics_interval_results = pm4py_statistics.calculate_interval_statistics(selected_event_log_id)

    statistics_data = StatisticsData()
    statistics_data.event_log_id = selected_event_log_id
    statistics_data.distribution_case_duration_graph = "statistics/graphs/" + selected_event_log_name + "_case_duration_graph.png"
    statistics_data.distribution_events_time = "statistics/graphs/" + selected_event_log_name + "_events_time_graph.png"
    statistics_data.save()

    statistics_results = statistics_single_results | statistics_interval_results
    context = {
        "statistics": statistics_data,
        "statistics_results": statistics_results,
        "selected_event_log_name": selected_event_log_name}
    return render(request, template, context)


@login_required(login_url="/accounts/login")
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


@login_required(login_url="/accounts/login")
def social_network_analysis(request, pk):
    """View to handle the render of social network analysis"""
    template = "process_handling/social_network_analysis.html"
    selected_event_log = EventLog.objects.get(pk=pk)
    selected_event_log_id = selected_event_log.event_log_id
    selected_event_log_name = selected_event_log.event_log_name
    social_network_analysis_results = pm4py_statistics.calculate_social_network_analysis(selected_event_log_id)
    context = {
        "social_network_analysis_results": social_network_analysis_results,
        "selected_event_log_name": selected_event_log_name
    }
    return render(request, template, context)


@login_required(login_url="/accounts/login")
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


@login_required(login_url="/accounts/login")
def conformance_check(request, event_log_pk, process_model_pk):
    """View to handle te conformance check of an event log and process model"""
    template = "process_handling/conformance_check.html"
    selected_event_log = EventLog.objects.get(pk=event_log_pk)
    selected_process_model = ProcessModel.objects.get(pk=process_model_pk)
    selected_event_log_name = selected_event_log.event_log_name
    selected_process_model_name = selected_process_model.process_model_name
    token_replay_results = pm4py_conformance.perform_token_replay(event_log_pk, process_model_pk)
    diagnostics_results = pm4py_conformance.perform_diagnostics(event_log_pk, process_model_pk)
    aligned_traces = pm4py_conformance.perform_alignment(event_log_pk, process_model_pk)
    context = {
        "token_replay_results": token_replay_results,
        "diagnostics_results": diagnostics_results,
        "aligned_traces": aligned_traces,
        "selected_event_log_name": selected_event_log_name,
        "selected_process_model_name": selected_process_model_name}
    return render(request, template, context)


@login_required(login_url="/accounts/login")
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


@login_required(login_url="/accounts/login")
def playout_simulation(request, pk, type_playout, num_traces):
    """View to handle the presentation of result of playout simulation"""
    template = "process_handling/playout_simulation.html"
    simulated_event_log = EventLog.objects.get(pk=pk)
    file_path = "media/" + str(simulated_event_log.event_log_file)
    file = open(file_path, "r")
    event_log_file_content = file.read()
    context = {
        "simulated_event_log": simulated_event_log,
        "type_playout": type_playout,
        "num_traces": num_traces,
        "event_log_file_content": event_log_file_content
    }
    return render(request, template, context)


def playout_simulation_select(request):
    """View to handle playout simulation of a process model"""
    template = "process_handling/playout_simulation_form.html"
    playout_details_form = PlayoutDetailsForm()

    if request.method == "POST":
        playout_details_form = PlayoutDetailsForm(request.POST)
        if playout_details_form.is_valid():
            playout = playout_details_form.cleaned_data["type_of_playout"]
            process_model_pk = playout_details_form.cleaned_data["process_model"]
            num_traces = playout_details_form.cleaned_data["number_of_traces"]
            pm4py_simulation.playout_petri_net(process_model_pk, playout, num_traces)

            process_model = ProcessModel.objects.get(process_model_id=process_model_pk)
            simulated_event_log = EventLog()
            simulated_event_log.event_log_owner = process_model.process_model_owner
            simulated_event_log.event_log_name = process_model.process_model_name + "_simulated_event_log"
            simulated_log_name = process_model.process_model_name + "_simulated_event_log"
            simulated_event_log.event_log_file = "event_logs/" + simulated_log_name + ".xes"
            simulated_event_log.save()

            messages.success(request, "Playout process model successful!")
            return redirect(
                reverse_lazy("process_handling:playout_simulation", kwargs={"pk": simulated_event_log.pk,
                                                                            "type_playout": playout,
                                                                            "num_traces": num_traces}))

    context = {"playout_details_form": playout_details_form}
    return render(request, template, context)


@login_required(login_url="/accounts/login")
def monte_carlo_simulation_select(request):
    """View to handle preparation of simulation"""
    template = "process_handling/monte_carlo_simulation_form.html"
    select_event_log_form = MonteCarloDetailsForm()
    if request.method == "POST":
        select_event_log_form = MonteCarloDetailsForm(request.POST)
        if select_event_log_form.is_valid():
            event_log_name = select_event_log_form.cleaned_data["event_log"]
            case_arrival_ratio = select_event_log_form.cleaned_data["case_arrival_ratio"]
            event_log = EventLog.objects.get(event_log_name=event_log_name)
            selected_event_log_id = event_log.event_log_id

            return redirect(
                reverse_lazy(
                    "process_handling:monte_carlo_simulation",
                    kwargs={"event_log_pk": selected_event_log_id,
                            "case_arrival_ratio": case_arrival_ratio}
                )
            )
    context = {
        "select_event_log_form": select_event_log_form
    }
    return render(request, template, context)


@login_required(login_url="/accounts/login")
def monte_carlo_simulation(request, event_log_pk, case_arrival_ratio):
    """View to handle monte carlo simulation"""
    template = "process_handling/monte_carlo_simulation.html"
    selected_event_log = EventLog.objects.get(pk=event_log_pk)
    simulation_results = pm4py_simulation.perform_monte_carlo_simulation(event_log_pk, case_arrival_ratio)

    simulated_event_log = EventLog()
    simulated_event_log.event_log_owner = selected_event_log.event_log_owner
    simulated_event_log.event_log_name = selected_event_log.event_log_name + "_simulated_monte_carlo_event_log"

    simulated_event_log.event_log_file = "event_logs/" + simulated_event_log.event_log_name + ".xes"
    simulated_event_log.save()

    file_path = "media/" + str(simulated_event_log.event_log_file)
    file = open(file_path, "r")
    event_log_file_content = file.read()

    context = {
        "event_log_file_content": event_log_file_content,
        "simulated_event_log": simulated_event_log,
        "simulation_results": simulation_results
    }
    return render(request, template, context)
