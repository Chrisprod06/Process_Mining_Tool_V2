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

from pm4py.util import constants
from pm4py.util.business_hours import BusinessHours

from data_handling.models import EventLog

from statistics import median,

def calculate_numeric_statistics(event_log_id) -> dict:
    """Function that calculates different statistics available in pm4py"""

    # Find log file path
    selected_event_log = EventLog.objects.get(pk=event_log_id)
    selected_event_log_file = selected_event_log.event_log_file
    selected_event_log_path = "media/" + str(selected_event_log_file)

    # Import xes file
    event_log = xes_importer.apply(selected_event_log_path)

    # Calculate cases duration
    all_cases_duration = case_statistics.get_all_case_durations(event_log, parameters={
        case_statistics.Parameters.TIMESTAMP_KEY: "time:timestamp"})
    # Calculate number of cases
    count_cases = len(all_cases_duration)
    # Calculate number of case variants
    variants_count = case_statistics.get_variant_statistics(event_log)
    variants_count = sorted(variants_count, key=lambda x: x['count'], reverse=True)
    # Calculate activity instances

    # Calculate number of activities

    # Calculate case duration
    # Min
    min_case_duration = min(all_cases_duration)
    # Median
    median_case_duration = median(all_cases_duration)
    # Average
    average_case_duration  = sum(list)/len(list)
    # Max
    max_case_duration = max(all_cases_duration)

    # Calculate Log timeframe
    # Start
    # End

    statistics_results = {
        "all_cases_durations": all_cases_duration,
        "count_case": count_cases

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
