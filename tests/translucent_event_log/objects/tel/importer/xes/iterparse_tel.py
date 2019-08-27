import logging

import ciso8601
from lxml import etree

from pm4py.objects import log as log_lib
from pm4py.objects.log.importer.xes.versions.iterparse_xes import __parse_attribute
from tests.translucent_event_log_new.objects.tel import tel as tel_lib
from pm4py.objects.petri import semantics
from pm4py.objects.petri.common import initial_marking as ini
from pm4py.algo.discovery.alpha import factory as alpha_miner
from pm4py.objects.log.util import sorting

EVENT_END = 'end'
EVENT_START = 'start'

def import_tel(filename, parameters = None):
    '''
    Imports XES file into translucent event log (tel) object

    Parameters
    ----------
    filename:
        Absolute filename
    parameters
        Parameters of the algorithm, including
            timestamp_sort -> Specify if we should sort log by timestamp
            timestamp_key -> If sort is enabled, then sort the log by using this key
            reverse_sort -> Specify in which direction the log should be sorted
            index_trace_indexes -> Specify if trace indexes should be added as event attribute for each event
            max_no_traces_to_import -> Specify the maximum number of traces to import from the log
            (read in order in the XML file)

    Returns
    -------
    log : :class:`tests.translucent_event_log.tel.EventLog`
        A translucent log (including enabled)
    '''

    if parameters is None:
        parameters = {}

    timestamp_sort = False
    timestamp_key = "time:timestamp"
    reverse_sort = False
    insert_trace_indexes = False
    max_no_traces_to_import = 1000000000

    if "timestamp_sort" in parameters:
        timestamp_sort = parameters["timestamp_sort"]
    if "timestamp_key" in parameters:
        timestamp_key = parameters["timestamp_key"]
    if "reverse_sort" in parameters:
        reverse_sort = parameters["reverse_sort"]
    if "insert_trace_indexes" in parameters:
        insert_trace_indexes = parameters["insert_trace_indexes"]
    if "max_no_traces_to_import" in parameters:
        max_no_traces_to_import = parameters["max_no_traces_to_import"]

    context = etree.iterparse(filename, events=['start', 'end'])

    log = None
    trace = None
    event = None

    tree = {}

    for tree_event, elem in context:
        if tree_event == EVENT_START:  # starting to read
            parent = tree[elem.getparent()] if elem.getparent() in tree else None

            if elem.tag.endswith(log_lib.util.xes.TAG_STRING):
                if parent is not None:
                    tree = __parse_attribute(elem, parent, elem.get(log_lib.util.xes.KEY_KEY),
                                             elem.get(log_lib.util.xes.KEY_VALUE), tree)
                continue

            elif elem.tag.endswith(log_lib.util.xes.TAG_DATE):
                try:
                    dt = ciso8601.parse_datetime(elem.get(log_lib.util.xes.KEY_VALUE))
                    tree = __parse_attribute(elem, parent, elem.get(log_lib.util.xes.KEY_KEY), dt, tree)
                except TypeError:
                    logging.info("failed to parse date: " + str(elem.get(log_lib.util.xes.KEY_VALUE)))
                except ValueError:
                    logging.info("failed to parse date: " + str(elem.get(log_lib.util.xes.KEY_VALUE)))
                continue

            elif elem.tag.endswith(log_lib.util.xes.TAG_EVENT):
                if event is not None:
                    raise SyntaxError('file contains <event> in another <event> tag')
                event = tel_lib.Event()
                tree[elem] = event
                continue

            elif elem.tag.endswith(log_lib.util.xes.TAG_TRACE):
                if len(log) >= max_no_traces_to_import:
                    break
                if trace is not None:
                    raise SyntaxError('file contains <trace> in another <trace> tag')
                trace = log_lib.log.Trace()
                tree[elem] = trace.attributes
                continue

            elif elem.tag.endswith(log_lib.util.xes.TAG_FLOAT):
                if parent is not None:
                    try:
                        val = float(elem.get(log_lib.util.xes.KEY_VALUE))
                        tree = __parse_attribute(elem, parent, elem.get(log_lib.util.xes.KEY_KEY), val, tree)
                    except ValueError:
                        logging.info("failed to parse float: " + str(elem.get(log_lib.util.xes.KEY_VALUE)))
                continue

            elif elem.tag.endswith(log_lib.util.xes.TAG_INT):
                if parent is not None:
                    try:
                        val = int(elem.get(log_lib.util.xes.KEY_VALUE))
                        tree = __parse_attribute(elem, parent, elem.get(log_lib.util.xes.KEY_KEY), val, tree)
                    except ValueError:
                        logging.info("failed to parse int: " + str(elem.get(log_lib.util.xes.KEY_VALUE)))
                continue

            elif elem.tag.endswith(log_lib.util.xes.TAG_BOOLEAN):
                if parent is not None:
                    try:
                        val0 = elem.get(log_lib.util.xes.KEY_VALUE)
                        val = False
                        if str(val0).lower() == "true":
                            val = True
                        tree = __parse_attribute(elem, parent, elem.get(log_lib.util.xes.KEY_KEY), val, tree)
                    except ValueError:
                        logging.info("failed to parse boolean: " + str(elem.get(log_lib.util.xes.KEY_VALUE)))
                continue

            elif elem.tag.endswith(log_lib.util.xes.TAG_LIST):
                if parent is not None:
                    # lists have no value, hence we put None as a value
                    tree = __parse_attribute(elem, parent, elem.get(log_lib.util.xes.KEY_KEY), None, tree)
                continue

            elif elem.tag.endswith(log_lib.util.xes.TAG_ID):
                if parent is not None:
                    tree = __parse_attribute(elem, parent, elem.get(log_lib.util.xes.KEY_KEY),
                                             elem.get(log_lib.util.xes.KEY_VALUE), tree)
                continue

            elif elem.tag.endswith(log_lib.util.xes.TAG_EXTENSION):
                if log is None:
                    raise SyntaxError('extension found outside of <log> tag')
                if elem.get(log_lib.util.xes.KEY_NAME) is not None and elem.get(
                        log_lib.util.xes.KEY_PREFIX) is not None and elem.get(log_lib.util.xes.KEY_URI) is not None:
                    log.extensions[elem.get(log_lib.util.xes.KEY_NAME)] = {
                        log_lib.util.xes.KEY_PREFIX: elem.get(log_lib.util.xes.KEY_PREFIX),
                        log_lib.util.xes.KEY_URI: elem.get(log_lib.util.xes.KEY_URI)}
                continue

            elif elem.tag.endswith(log_lib.util.xes.TAG_GLOBAL):
                if log is None:
                    raise SyntaxError('global found outside of <log> tag')
                if elem.get(log_lib.util.xes.KEY_SCOPE) is not None:
                    log.omni_present[elem.get(log_lib.util.xes.KEY_SCOPE)] = {}
                    tree[elem] = log.omni_present[elem.get(log_lib.util.xes.KEY_SCOPE)]
                continue

            elif elem.tag.endswith(log_lib.util.xes.TAG_CLASSIFIER):
                if log is None:
                    raise SyntaxError('classifier found outside of <log> tag')
                if elem.get(log_lib.util.xes.KEY_KEYS) is not None:
                    classifier_value = elem.get(log_lib.util.xes.KEY_KEYS)
                    if "'" in classifier_value:
                        log.classifiers[elem.get(log_lib.util.xes.KEY_NAME)] = [x for x in classifier_value.split("'")
                                                                                if x.strip()]
                    else:
                        log.classifiers[elem.get(log_lib.util.xes.KEY_NAME)] = classifier_value.split()
                continue

            elif elem.tag.endswith(log_lib.util.xes.TAG_LOG):
                if log is not None:
                    raise SyntaxError('file contains > 1 <log> tags')
                log = log_lib.log.EventLog()
                tree[elem] = log.attributes
                continue

        elif tree_event == EVENT_END:
            if elem in tree:
                del tree[elem]
            elem.clear()
            if elem.getprevious() is not None:
                try:
                    del elem.getparent()[0]
                except TypeError:
                    pass

            if elem.tag.endswith(log_lib.util.xes.TAG_EVENT):
                if trace is not None:
                    trace.append(event)
                    event = None
                continue

            elif elem.tag.endswith(log_lib.util.xes.TAG_TRACE):
                log.append(trace)
                trace = None
                continue

            elif elem.tag.endswith(log_lib.util.xes.TAG_LOG):
                continue

    del context

    # net, initial_marking, final_marking = alpha_miner.apply(log)
    #
    # for trace in log:
    #     m = ini.discover_initial_marking(net)
    #     for event in trace:
    #         act = event['concept:name']
    #
    #         for trans in net.transitions:
    #             if act == trans.label:
    #                 t = trans
    #                 break
    #
    #         en = semantics.enabled_transitions(net, m)
    #         event.set_enabled(frozenset(en))
    #         if m == final_marking:
    #             break
    #         m = semantics.execute(t, net, m) #find enabled activity
    #
    if timestamp_sort:
        log = sorting.sort_timestamp(log, timestamp_key=timestamp_key, reverse_sort=reverse_sort)
    if insert_trace_indexes:
        log.insert_trace_index_as_event_attribute()

    return log