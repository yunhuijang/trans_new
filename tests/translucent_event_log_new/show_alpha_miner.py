
import os
from pm4py.objects.log.importer.xes import factory as xes_importer
from tests.translucent_event_log_new.objects.tel.importer.xes import utils as xes_utils
from tests.translucent_event_log_new.objects.tel.importer.xes import iterparse_tel
from pm4py.algo.discovery.alpha import factory as alpha_miner
from pm4py.objects.log.exporter.xes import factory as xes_exporter
from pm4py.visualization.petrinet import factory as vis_factory
from tests.translucent_event_log_new.objects.tel.importer.xes import iterparse_tel

input_file_path = os.path.join("input_data","roadtraffic50traces.xes")

log = iterparse_tel.import_tel(input_file_path) #괄호 안에 원하는 파일의 경로를 쓴다.
#log에 alpha algorithm을 적용
net, initial_marking, final_marking = alpha_miner.apply(log)
#도출된 petri net을 visualization
gviz = vis_factory.apply(net, initial_marking, final_marking)
vis_factory.view(gviz)
