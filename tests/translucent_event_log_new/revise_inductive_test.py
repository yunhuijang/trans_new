import os
from tests.translucent_event_log.objects.tel.importer.xes.iterparse_tel import import_tel
import tests.translucent_event_log_new.objects.tel.tel as tel
from tests.translucent_event_log_new.objects.tel.importer.xes.utils import log_to_tel
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.visualization.process_tree import factory as vis_factory
from tests.translucent_event_log.objects.tel.importer.xes.iterparse_tel import import_tel
import os
from tests.translucent_event_log_new.objects.tel.importer.xes.utils import log_to_tel
from pm4py.algo.discovery.alpha import factory as alpha_miner
from tests.translucent_event_log_new.objects.tel.utils import tel_set_enabled
from tests.translucent_event_log_new.algo.discover_automaton import utils
from datetime import timedelta

input_file_path = os.path.join("input_data", "running-example_tel.xes")
log = import_tel(input_file_path)
tel = tel_set_enabled(log)
logg = xes_importer.apply(input_file_path)
nett= inductive_miner.apply(tel)
net= inductive_miner.apply(logg)

gviz = vis_factory.apply(nett)
vis_factory.view(gviz)
gviz = vis_factory.apply(net)
vis_factory.view(gviz)
