from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .forms import ProcessModelForm, DiscoverProcessModelForm
from .models import ProcessModel

# Create your views here.

from core import pm4py_discovery


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
