from statistics import median
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.petri_net.importer import importer as pnml_importer

from data_handling.models import EventLog
from process_handling.models import ProcessModel


def perform_token_replay(event_log_name, process_model_id) -> dict:
    """Function that performs token replay"""

    # Import event log
    event_log = EventLog.objects.get(pk=event_log_name)
    event_log_path = event_log.event_log_file
    event_log_file = xes_importer.apply("media/" + str(event_log_path))

    # Import process model
    process_model = ProcessModel.objects.get(process_model_id=process_model_id)
    process_model_path = process_model.process_model_pnml_file
    process_model_file = pnml_importer.apply("media/" + str(process_model_path))
    net, initial_marking, final_marking = process_model_file

    # Perform token based replay
    replayed_traces = token_replay.apply(event_log_file, net, initial_marking, final_marking)
    print(replayed_traces)
    # Overview replayed_traces

    total_traces = 0
    total_fit_traces = 0
    trace_fitness_list = []
    for trace in replayed_traces:
        # Calculate total traces
        total_traces = total_traces + 1
        if trace["trace_is_fit"]:
            # Calculate fitness
            total_fit_traces = total_fit_traces + 1
        # Extract trace_fitness
        trace_fitness_list.append(trace["trace_fitness"])

    # Calculate median trace fitness
    trace_fitness_median = median(trace_fitness_list)
    # Calculate traces with problems
    total_traces_problem = total_traces - total_fit_traces
    overview = {
        "total_traces": total_traces,
        "total_fit_traces": total_fit_traces,
        "total_traces_problem": total_traces_problem,
        "trace_fitness_median": trace_fitness_median
    }
    results = {
        "replayed_traces": replayed_traces,
        "overview": overview
    }
    return results
