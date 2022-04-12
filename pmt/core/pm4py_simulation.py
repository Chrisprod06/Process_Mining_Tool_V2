from pm4py.algo.simulation.playout.petri_net import algorithm as simulator
from pm4py.objects.log.importer.xes import importer as xes_importer
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

    if
