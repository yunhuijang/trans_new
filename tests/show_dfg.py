import os
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.algo.discovery.dfg import factory as dfg_factory
from pm4py.visualization.dfg import factory as dfg_vis_factory

log = xes_importer.import_log(os.path.join("input_data","roadtraffic50traces.xes"))
dfg = dfg_factory.apply(log)

gviz = dfg_vis_factory.apply(dfg, log=log, variant="frequency") #or variant = "performance"
dfg_vis_factory.view(gviz)