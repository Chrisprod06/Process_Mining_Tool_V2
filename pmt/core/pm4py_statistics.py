from datetime import datetime

from django.conf import settings

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.util import interval_lifecycle

from pm4py.statistics.sojourn_time.log import get as soj_time_get
from pm4py.statistics.traces.generic.log import case_arrival, case_statistics
from pm4py.statistics.concurrent_activities.log import get as conc_act_get
from pm4py.statistics.eventually_follows.log import get as efg_get

from pm4py.statistics.traces.generic.log import case_statistics

from pm4py.visualization.graphs import visualizer as graphs_visualizer
from pm4py.visualization.sna import visualizer as sna_visualizer

from pm4py.util import constants
from pm4py.util.business_hours import BusinessHours

from pm4py.algo.organizational_mining.sna import algorithm as sna
from pm4py.algo.organizational_mining.roles import algorithm as roles_discovery

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
    sna_visualizer.view(gviz_handover_work,
                        variant=sna_visualizer.Variants.PYVIS)

    # Calculate subcontracting
    subcontracting_values = sna.apply(
        event_log, variant=sna.Variants.SUBCONTRACTING_LOG
    )
    gviz_subcontracting = sna_visualizer.apply(
        subcontracting_values, variant=sna_visualizer.Variants.PYVIS
    )
    sna_visualizer.view(gviz_subcontracting, variant=sna_visualizer.Variants.PYVIS)

    # Calculate working together
    working_together_values = sna.apply(
        event_log, variant=sna.Variants.WORKING_TOGETHER_LOG
    )
    gviz_working_together = sna_visualizer.apply(
        working_together_values, variant=sna_visualizer.Variants.PYVIS
    )
    sna_visualizer.view(gviz_working_together, variant=sna_visualizer.Variants.PYVIS)

    # Calculate similar activities
    similar_activities_values = sna.apply(
        event_log, variant=sna.Variants.JOINTACTIVITIES_LOG
    )
    gviz_similar_activities_values = sna_visualizer.apply(
        similar_activities_values, variant=sna_visualizer.Variants.PYVIS
    )
    sna_visualizer.view(
        gviz_similar_activities_values, variant=sna_visualizer.Variants.PYVIS)

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

    # Calculate activity instances

    # Calculate number of activities

    # Calculate case duration
    # Min
    min_case_duration = min(all_cases_duration)
    # Median
    median_case_duration = median(all_cases_duration)
    # Average
    average_case_duration = sum(all_cases_duration) / len(all_cases_duration)
    # Max
    max_case_duration = max(all_cases_duration)

    # Calculate Log timeframe
    # Start
    # End

    # Case duration distribution
    x, y = case_statistics.get_kde_caseduration(event_log, parameters={
        constants.PARAMETER_CONSTANT_TIMESTAMP_KEY: "time:timestamp"})

    gviz = graphs_visualizer.apply_plot(x, y, variant=graphs_visualizer.Variants.CASES)
    graphs_visualizer.view(gviz)

    statistics_results = {
        "all_cases_durations": all_cases_duration,
        "count_case": count_cases,
        "case_variants": case_variants,
        "count_variants": count_variants,
        "min_case_duration": min_case_duration,
        "median_case_duration": median_case_duration,
        "average_case_duration": average_case_duration,
        "max_case_duration": max_case_duration,
    }

    return statistics_results


# Single timestamp statistics


def calculate_median_case_duration(log):
    """Function to calculate the median case duration"""
    return case_statistics.get_all_casedurations(
        log,
        parameters={case_statistics.Parameters.TIMESTAMP_KEY: "time:timestamp"},
    )


def calculate_case_arrival_ratio(log):
    """Function to calculate the case arrival ratio"""
    return case_arrival.get_case_arrival_avg(
        log, parameters={case_arrival.Parameters.TIMESTAMP_KEY: "time:timestamp"}
    )


def calculate_case_dispersion_ratio(log):
    """Function to calculate the case dispersion ratio"""
    return case_arrival.get_case_dispersion_avg(
        log, parameters={case_arrival.Parameters.TIMESTAMP_KEY: "time:timestamp"}
    )


# Interval logs statistics


def calculate_business_hours(log):
    """Function to calculate statistics derived from business hours"""
    st = datetime.fromtimestamp(100000000)
    et = datetime.fromtimestamp(200000000)
    # bh_object = BusinessHours(st, et, worktiming=[10, 16], weekends=[5, 6, 7]) specifying work time and work days
    bh_object = BusinessHours(st, et)
    worked_time = bh_object.getseconds()
    return worked_time


def calculate_cycle_time(log):
    """Function to enrich the given event log with cycle time attributes"""
    return interval_lifecycle.assign_lead_cycle_time(log)


def calculate_sojourn_time(log):
    """Function to calculate sojourn time"""
    return soj_time_get.apply(
        log,
        parameters={
            soj_time_get.Parameters.TIMESTAMP_KEY: "time:timestamp",
            soj_time_get.Parameters.START_TIMESTAMP_KEY: "start_timestamp",
        },
    )


def calculate_concurrent_activities(log):
    """Function to calculate concurrent activities"""
    return conc_act_get.apply(
        log,
        parameters={
            conc_act_get.Parameters.TIMESTAMP_KEY: "time:timestamp",
            conc_act_get.Parameters.START_TIMESTAMP_KEY: "start_timestamp",
        },
    )


# Graphs
def calculate_eventually_follows_graph(log):
    """Function to calculate eventually follows graph"""
    print(efg_get.apply(log))
    return


def calculate_distribution_case_duration_graph(log):
    """Function to calculate the distribution of case duration graph"""
    x, y = case_statistics.get_kde_caseduration(
        log, parameters={constants.PARAMETER_CONSTANT_TIMESTAMP_KEY: "time:timestamp"}
    )
    gviz = graphs_visualizer.apply_plot(x, y, variant=graphs_visualizer.Variants.CASES)
    graphs_visualizer.save(gviz, "PMT/media/graphs")
    return
