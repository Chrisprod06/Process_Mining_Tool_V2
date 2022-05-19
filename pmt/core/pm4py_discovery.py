# Data Handling libraries
import pm4py
from django.conf import settings

# Alpha miner imports
from pm4py.algo.discovery.alpha import algorithm as alpha_miner

# Inductive mine imports
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.petri_net.exporter import exporter as pnml_exporter
from pm4py.objects.bpmn.exporter import exporter as bpmn_exporter
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.visualization.bpmn import visualizer as bpmn_visualizer
from pm4py.objects.conversion.process_tree import converter as pt_converter
from pm4py.objects.conversion.wf_net import converter as wf_net_converter
from data_handling.models import EventLog


# Process discovery algorithms

# Petri net


def process_model_discovery(event_log_name, process_model_name):
    """Function to discover a process model using inductive miner"""
    # Import event log
    event_log = EventLog.objects.get(event_log_name=event_log_name)
    event_log_path = event_log.event_log_file
    event_log_file = xes_importer.apply("media/" + str(event_log_path))

    if event_log is None or event_log_path is None or event_log_file is None:
        return False

    # Discover petri net using inductive miner and save it
    net, im, fm = inductive_miner.apply(event_log_file)
    petri_net_path = "media/process_models/pnml/" + process_model_name + ".pnml"
    pnml_exporter.apply(net, im, petri_net_path, final_marking=fm)
    # Convert petri into process tree
    tree = wf_net_converter.apply(net, im, fm)
    # Convert process tree into bpmn and save it
    bpmn_graph = pt_converter.apply(tree, variant=pt_converter.Variants.TO_BPMN)
    bpmn_path = "media/process_models/bpmn/" + process_model_name + ".bpmn"
    bpmn_exporter.apply(bpmn_graph, bpmn_path)
    # Export petri net png
    petri_net_gviz = pn_visualizer.apply(net, im, fm)
    petri_net_png_path = "media/exported_pngs/pnml/" + process_model_name + ".png"
    pn_visualizer.save(petri_net_gviz, output_file_path=petri_net_png_path)
    # Export bpmn png
    bpmn_graph_gviz = bpmn_visualizer.apply(bpmn_graph)
    bpmn_png_path = "media/exported_pngs/bpmn/" + process_model_name + ".png"
    bpmn_visualizer.save(bpmn_graph_gviz, output_file_path=bpmn_png_path)
    # Export Petri net png with frequency
    petri_net_frequency_gviz = pn_visualizer.apply(net, im, fm, parameters={
        pn_visualizer.Variants.FREQUENCY.value.Parameters.FORMAT: "png"},
                                                   variant=pn_visualizer.Variants.FREQUENCY, log=event_log_file)
    petri_net_frequency_png_path = "media/exported_pngs/pnml/" + process_model_name + "_frequency.png"
    pn_visualizer.save(petri_net_frequency_gviz, output_file_path=petri_net_frequency_png_path)
    # Export Petri net png with performance
    petri_net_performance_gviz = pn_visualizer.apply(net, im, fm, parameters={
        pn_visualizer.Variants.PERFORMANCE.value.Parameters.FORMAT: "png"},
                                                     variant=pn_visualizer.Variants.PERFORMANCE, log=event_log_file)
    petri_net_performance_png_path = "media/exported_pngs/pnml/" + process_model_name + "_performance.png"
    pn_visualizer.save(petri_net_performance_gviz, output_file_path=petri_net_performance_png_path)

    return True
