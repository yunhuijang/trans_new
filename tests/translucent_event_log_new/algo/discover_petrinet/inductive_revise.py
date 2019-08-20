from collections import Counter

from pm4py import util as pmutil
from pm4py.objects.log.util import xes as xes_util


def get_dfg_graph_trans(log, parameters = None):

    if parameters is None:
        parameters = {}
    if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    activity_key = parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
    dfg_list = []
    for trace in log:
        for i in range(len(trace)-1):
            en_set = trace[i+1]['enabled']
            for en in en_set:
                dfg_list.append((trace[i][activity_key], en))

    return Counter(dfg_list)