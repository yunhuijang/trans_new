import os
from tests.translucent_event_log.objects.tel.importer.xes.iterparse_tel import import_tel
from tests.translucent_event_log_new.objects.tel.importer.xes.utils import log_to_tel
from pm4py.algo.discovery.alpha import factory as alpha_miner
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.objects.log.exporter.xes import factory as xes_exporter
from pm4py.visualization.petrinet import factory as vis_factory

input_file_path = os.path.join("input_data", "running-example.xes")
log = import_tel(input_file_path)
nett, im, fm = alpha_miner.apply(log)


tel = log_to_tel(nett, im, fm, log)

for trace in tel:
    for event in trace:
        print(event['enabled'])
        print(event['concept:name'])
    print(" ")

output_path = os.path.join("input_data", "running-example_alpha_tel.xes")
xes_exporter.export_log(tel, output_path)