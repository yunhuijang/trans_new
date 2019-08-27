import os

from pm4py.objects.log.importer.csv import factory as csv_importer
from pm4py.objects.conversion.log import factory as conversion_factory
from pm4py.algo.discovery.alpha import factory as alpha_miner
from pm4py.visualization.petrinet import factory as vis_factory
from tests.translucent_event_log_new.algo.discover_petrinet.alpha_revise import trans_alpha

event_stream = csv_importer.import_event_stream(os.path.join("input_data", "sample.csv"))
log = conversion_factory.apply(event_stream)

net, im, fm = trans_alpha(log)
nett, imm, fmm = alpha_miner.apply(log)

gviz = vis_factory.apply(net, im, fm)
gvizz = vis_factory.apply(nett, imm, fmm)
vis_factory.view(gviz)
vis_factory.view(gvizz)

