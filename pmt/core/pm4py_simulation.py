from pm4py.algo.simulation.playout.petri_net import algorithm as simulator
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.statistics.start_activities.log import get as start_activities
from pm4py.statistics.end_activities.log import get as end_activities
from pm4py.statistics.traces.generic.log import case_arrival
from pm4py.objects.conversion.dfg import converter
from pm4py.algo.simulation.montecarlo import simulator as montecarlo_simulation
from pm4py.algo.conformance.tokenreplay.algorithm import Variants
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


def perform_monte_carlo_simulation(event_log_pk) -> dict:
    """Function to perform monte carlo simulation"""
    # Import event log
    event_log = EventLog.objects.get(pk=event_log_pk)
    event_log_path = event_log.event_log_file
    event_log_file = xes_importer.apply("media/" + str(event_log_path))

    # Discover performance DFG
    dfg_perf = dfg_discovery.apply(event_log_file, variant=dfg_discovery.Variants.PERFORMANCE)

    # Calculate start and end activities
    sa = start_activities.get_start_activities(event_log_file)
    ea = end_activities.get_end_activities(event_log_file)

    # Calculate case arrival ratio
    ratio = case_arrival.get_case_arrival_avg(event_log_file)

    # Convert DFG to petri net
    net, im, fm = converter.apply(dfg_perf, variant=converter.Variants.VERSION_TO_PETRI_NET_ACTIVITY_DEFINES_PLACE,
                                  parameters={
                                      converter.Variants.VERSION_TO_PETRI_NET_ACTIVITY_DEFINES_PLACE.value.Parameters.START_ACTIVITIES: sa,
                                      converter.Variants.VERSION_TO_PETRI_NET_ACTIVITY_DEFINES_PLACE.value.Parameters.END_ACTIVITIES: ea})
    # Perform monte carlo simulation
    parameters = {}
    parameters[
        montecarlo_simulation.Variants.PETRI_SEMAPH_FIFO.value.Parameters.TOKEN_REPLAY_VARIANT] = Variants.BACKWARDS
    parameters[montecarlo_simulation.Variants.PETRI_SEMAPH_FIFO.value.Parameters.PARAM_CASE_ARRIVAL_RATIO] = 10800
    simulated_log, res = montecarlo_simulation.apply(event_log_file, net, im, fm, parameters=parameters)

    simulated_log_name = event_log.event_log_name + "_simulated_monte_carlo_event_log"
    xes_exporter.apply(simulated_log, "media/event_logs/" + simulated_log_name + ".xes")

    return res
