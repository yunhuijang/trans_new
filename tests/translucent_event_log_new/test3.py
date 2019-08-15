import itertools
import os
from tests.translucent_event_log_new.objects.tel.importer.xes.iterparse_tel import import_tel
from tests.translucent_event_log_new.objects.tel.importer.xes.utils import log_to_tel
from pm4py.algo.discovery.alpha import factory as alpha_miner
from tests.translucent_event_log_new.algo.discover_petrinet.state_based_region import is_essential
from tests.translucent_event_log.objects.tel import utils

input_file_path = os.path.join("input_data", "running-example.xes")
log = import_tel(input_file_path)
for trace in log:
    print(trace.attributes)













