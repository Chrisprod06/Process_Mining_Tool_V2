# Data Handling libraries
import pm4py
from django.conf import settings

# Alpha miner imports
from pm4py.algo.discovery.alpha import algorithm as alpha_miner

# Inductive mine imports
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.petri_net.exporter import exporter as pnml_exporter
from pm4py.visualization.petri_net import visualizer as pn_visualizer

from data_handling.models import EventLog


# Process discovery algorithms

# Petri net


def petri_net_discovery(event_log_name, process_model_name, algorithm):
    """Function to discover a process model using alpha miner"""
    event_log = None
    event_log_path = None
    log = None

    event_log = EventLog.objects.get(event_log_name=event_log_name)
    event_log_path = event_log.event_log_file
    log = xes_importer.apply("media/" + str(event_log_path))

    if event_log is None or event_log_path is None or log is None:
        return False

    # Need to add more controls
    if algorithm is settings.ALPHA_MINER:
        net, initial_marking, final_marking = alpha_miner.apply(log)
    elif algorithm is settings.INDUCTIVE_MINER:
        net, initial_marking, final_marking = inductive_miner.apply(log)

    gviz = pn_visualizer.apply(net, initial_marking, final_marking)
    pn_visualizer.save(
        gviz, output_file_path="media/exported_pngs/" + process_model_name + ".png"
    )
    pnml_exporter.apply(
        net, initial_marking, "media/process_models/" + process_model_name + ".pnml"
    )
    return True


def petri_net_to_bpmn(net, im, fm, process_model_name) -> bool:
    """Function to convert petri net into bpmn"""
    pass
