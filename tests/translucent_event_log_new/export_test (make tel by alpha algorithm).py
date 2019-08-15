import os
from tests.translucent_event_log.objects.tel.importer.xes.iterparse_tel import import_tel
from tests.translucent_event_log_new.objects.tel.importer.xes.utils import log_to_tel
from pm4py.algo.discovery.alpha import factory as alpha_miner
from pm4py.objects.log.exporter.xes import factory as xes_exporter

input_file_path = os.path.join("input_data", "roadtraffic100traces.xes")
log = import_tel(input_file_path)
nett, initial_marking, final_marking = alpha_miner.apply(log)

tel = log_to_tel(nett, initial_marking, final_marking, log)

output_path = os.path.join("input_data", "roadtraffic100traces_tel.xes")
xes_exporter.export_log(tel, output_path)