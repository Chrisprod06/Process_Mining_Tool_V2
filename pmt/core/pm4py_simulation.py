from pm4py.algo.simulation.playout.petri_net import algorithm as simulator
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.exporter.xes import exporter as xes_exporter

from pm4py.objects.petri_net.importer import importer as pnml_importer
from data_handling.models import EventLog
from process_handling.models import ProcessModel


def playout_petri_net(process_model_pk, type_playout, num_traces):
    """Function to handle playout of petri net model"""
    # Import process model
    process_model = ProcessModel.objects.get(process_model_id=process_model_pk)
    process_model_path = process_model.process_model_pnml_file
    process_model_file = pnml_importer.apply("media/" + str(process_model_path))
    net, initial_marking, final_marking = process_model_file

    if type_playout == "basic":
        simulated_log = simulator.apply(net, initial_marking, variant=simulator.Variants.BASIC_PLAYOUT,
                                        parameters={
                                            simulator.Variants.BASIC_PLAYOUT.value.Parameters.NO_TRACES: num_traces})
    elif type_playout == "extensive":
        simulated_log = simulator.apply(net, initial_marking, variant=simulator.Variants.EXTENSIVE,
                                        parameters={
                                            simulator.Variants.EXTENSIVE.value.Parameters.MAX_TRACE_LENGTH: num_traces})
    simulated_log_name = process_model.process_model_name + "_simulated_event_log"
    xes_exporter.apply(simulated_log, "media/event_logs/" + simulated_log_name + ".xes")

    return
