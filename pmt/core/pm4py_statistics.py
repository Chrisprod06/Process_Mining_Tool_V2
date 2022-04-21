import datetime
import json

import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.statistics.traces.generic.log import case_statistics
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.algo.filtering.log.variants import variants_filter

from pm4py.visualization.sna import visualizer as sna_visualizer
from pm4py.util import constants
from pm4py.statistics.rework.cases.log import get as get_rework_cases
from pm4py.algo.organizational_mining.sna import algorithm as sna
from pm4py.algo.organizational_mining.roles import algorithm as roles_discovery
from pm4py.statistics.sojourn_time.log import get as soj_time_get
from pm4py.statistics.concurrent_activities.log import get as conc_act_get
from pm4py.algo.discovery.batches import algorithm as discover_batches
from data_handling.models import EventLog

from statistics import median


def calculate_social_network_analysis(event_log_id) -> dict:
    """Function that calculates the social network analysis of an event log"""

    # Find log file path
    selected_event_log = EventLog.objects.get(pk=event_log_id)
    selected_event_log_file = selected_event_log.event_log_file
    selected_event_log_name = selected_event_log.event_log_name
    selected_event_log_path = "media/" + str(selected_event_log_file)

    # Import event log
    event_log = xes_importer.apply(selected_event_log_path)

    # Calculate handover of work
    handover_work_values = sna.apply(event_log, variant=sna.Variants.HANDOVER_LOG)
    gviz_handover_work = sna_visualizer.apply(
        handover_work_values, variant=sna_visualizer.Variants.PYVIS,
    )
    # sna_visualizer.view(gviz_handover_work,
    #                    variant=sna_visualizer.Variants.PYVIS)

    # Calculate subcontracting
    subcontracting_values = sna.apply(
        event_log, variant=sna.Variants.SUBCONTRACTING_LOG
    )
    gviz_subcontracting = sna_visualizer.apply(
        subcontracting_values, variant=sna_visualizer.Variants.PYVIS
    )
    # sna_visualizer.view(gviz_subcontracting, variant=sna_visualizer.Variants.PYVIS)

    # Calculate working together
    working_together_values = sna.apply(
        event_log, variant=sna.Variants.WORKING_TOGETHER_LOG
    )
    gviz_working_together = sna_visualizer.apply(
        working_together_values, variant=sna_visualizer.Variants.PYVIS
    )
    # sna_visualizer.view(gviz_working_together, variant=sna_visualizer.Variants.PYVIS)

    # Calculate similar activities
    similar_activities_values = sna.apply(
        event_log, variant=sna.Variants.JOINTACTIVITIES_LOG
    )
    gviz_similar_activities_values = sna_visualizer.apply(
        similar_activities_values, variant=sna_visualizer.Variants.PYVIS
    )
    # sna_visualizer.view(
    #    gviz_similar_activities_values, variant=sna_visualizer.Variants.PYVIS)

    # Discover roles
    roles = roles_discovery.apply(event_log)

    # Group working together ( clustering )

    # Group similar activities ( clustering )
    similar_activities_metric = sna.apply(event_log, variant=sna.Variants.JOINTACTIVITIES_LOG)

    social_network_analysis_results = {
        "handover_work_values": handover_work_values,
        "subcontracting_values": subcontracting_values,
        "working_together_values": working_together_values,
        "similar_activities_values": similar_activities_values,
        "roles": roles
    }
    return social_network_analysis_results


def calculate_statistics(event_log_id) -> dict:
    """Function that calculates different statistics available in pm4py"""

    # Find log file path
    selected_event_log = EventLog.objects.get(pk=event_log_id)
    selected_event_log_file = selected_event_log.event_log_file
    selected_event_log_path = "media/" + str(selected_event_log_file)

    # Import xes file
    event_log = xes_importer.apply(selected_event_log_path)

    # Calculate cases duration
    all_cases_duration = case_statistics.get_all_case_durations(
        event_log,
        parameters={case_statistics.Parameters.TIMESTAMP_KEY: "time:timestamp"},
    )
    # Calculate number of cases
    count_cases = len(all_cases_duration)
    # Calculate case variants
    case_variants = case_statistics.get_variant_statistics(event_log)

    # Calculate number of case variants
    count_variants = 0
    for variant in case_variants:
        count_variants += variant["count"]

    # Calculate Rework activities
    rework_activities = pm4py.get_rework_cases_per_activity(event_log)
    rework_activities_counter = 0
    for activity, count in rework_activities.items():
        rework_activities_counter = rework_activities_counter + count
    # Calculate Rework cases
    rework_cases = get_rework_cases.apply(event_log)
    rework_cases_counter = 0
    for case, activities in rework_cases.items():
        for activity, count in activities.items():
            rework_cases_counter = rework_cases_counter + count

    print(rework_activities)
    print(rework_cases)
    # Calculate case duration
    # Min
    min_case_duration = min(all_cases_duration)
    min_case_duration = round(min_case_duration / 3600, 1)
    # Median
    median_case_duration = median(all_cases_duration)
    median_case_duration = round(median_case_duration / 3600, 1)
    # Average
    average_case_duration = sum(all_cases_duration) / len(all_cases_duration)
    average_case_duration = round(average_case_duration / 3600, 1)
    # Max
    max_case_duration = max(all_cases_duration)
    max_case_duration = round(max_case_duration / 3600, 1)

    # Calculate Log timeframe
    # Start
    # End

    # Case duration distribution
    x, y = case_statistics.get_kde_caseduration(event_log, parameters={
        constants.PARAMETER_CONSTANT_TIMESTAMP_KEY: "time:timestamp"})
    case_duration_graph_data = {
        "x": x,
        "y": y
    }
    # Get 2 lists of coordinates
    x = case_duration_graph_data["x"]
    y = case_duration_graph_data["y"]
    # Parse into a list of tuples which represent points
    points_case_duration_graph_tuples = list(zip(x, y))
    # Convert them into a list of dictionaries for chart.js data
    points_case_duration_graph = []
    for index, point in enumerate(points_case_duration_graph_tuples):
        points_case_duration_graph.append({
            "x": point[0],
            "y": point[1]
        })
    points_case_duration_graph = json.dumps(points_case_duration_graph)

    # Events over time distribution
    x, y = attributes_filter.get_kde_date_attribute(event_log, attribute="time:timestamp")
    events_over_time_graph_data = {
        "x": x,
        "y": y
    }
    # Get 2 lists of coordinates
    x = events_over_time_graph_data["x"]
    y = events_over_time_graph_data["y"]
    # Parse into a list of tuples which represent points
    points_events_over_time_graph_tuples = list(zip(x, y))
    # Convert them into a list of dictionaries for chart.js data
    points_events_over_time_graph = []
    for index, point in enumerate(points_case_duration_graph_tuples):
        points_events_over_time_graph.append({
            "x": point[0],
            "y": point[1]
        })
    points_events_over_time_graph = json.dumps(points_events_over_time_graph)

    statistics_results = {
        "all_cases_durations": all_cases_duration,
        "count_case": count_cases,
        "case_variants": case_variants,
        "count_variants": count_variants,
        "min_case_duration": min_case_duration,
        "median_case_duration": median_case_duration,
        "average_case_duration": average_case_duration,
        "max_case_duration": max_case_duration,
        "points_case_duration_graph": points_case_duration_graph,
        "points_events_over_time_graph": points_events_over_time_graph,
        "rework_activities": rework_activities,
        "rework_cases": rework_cases,
        "rework_activities_counter": rework_activities_counter,
        "rework_cases_counter": rework_cases_counter

    }

    return statistics_results


def calculate_interval_statistics(event_log_pk) -> dict:
    """Function to calculate interval statistics"""
    # Find log file path
    selected_event_log = EventLog.objects.get(pk=event_log_pk)
    selected_event_log_file = selected_event_log.event_log_file
    selected_event_log_path = "media/" + str(selected_event_log_file)

    # Import xes file
    event_log = xes_importer.apply(selected_event_log_path)

    # Calculate sojourn time
    sojourn_time = soj_time_get.apply(event_log, parameters={soj_time_get.Parameters.TIMESTAMP_KEY: "time:timestamp",
                                                             soj_time_get.Parameters.START_TIMESTAMP_KEY: "start_timestamp"})

    # Calculate concurrent activities
    concurrent_activities = conc_act_get.apply(event_log,
                                               parameters={conc_act_get.Parameters.TIMESTAMP_KEY: "time:timestamp",
                                                           conc_act_get.Parameters.START_TIMESTAMP_KEY: "start_timestamp"})

    # Calculate batches
    batches = discover_batches.apply(event_log)

    statistics_results = {
        "sojourn_time": sojourn_time,
        "concurrent_activities": concurrent_activities,
        "batches": batches
    }

    return statistics_results
