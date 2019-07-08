from pm4py.objects import log as log_lib
import logging
from tests.translucent_event_log.objects.tel import tel as tel_lib
from lxml import etree
import ciso8601


def __parse_attribute(elem, store, key, value, tree):
    if len(elem.getchildren()) == 0:
        store[key] = value
    else:
        store[key] = {log_lib.util.xes.KEY_VALUE: value, log_lib.util.xes.KEY_CHILDREN: {}}
        if elem.getchildren()[0].tag.endswith(log_lib.util.xes.TAG_VALUES):
            tree[elem] = store[key][log_lib.util.xes.KEY_CHILDREN]
            tree[elem.getchildren()[0]] = tree[elem]
        else:
            tree[elem] = store[key][log_lib.util.xes.KEY_CHILDREN]
    return tree

def import_simulated_log(input_file_path):
    '''
    Converts yawl simulated log by ProM Import Framework (MXML) into log object

    Parameters
    ----------
    :param input_file_path: input yawl logging file (mxml) path

    Returns
    --------
    log object (pm4py.objects.log.log.EventLog)

    '''

    #todo: to check whether it is yawl file or not

    EVENT_END = 'end'
    EVENT_START = 'start'

    context = etree.iterparse(input_file_path, events=['start', 'end'])
    log = None
    trace = None
    event = None

    tree = {}

    for tree_event, elem in context:
        if tree_event == EVENT_START:
            parent = tree[elem.getparent()] if elem.getparent() in tree else None

            if elem.tag.endswith('WorkflowModelElement'):
                if parent is not None:
                    tree = __parse_attribute(elem, parent, 'activity', elem.text, tree)

                continue

            elif elem.tag.endswith('EventType'):
                if parent is not None:
                    tree = __parse_attribute(elem, parent, 'lifecycle:transition', elem.text, tree)

            elif elem.tag.endswith('Timestamp'):
                try:
                    dt = ciso8601.parse_datetime(elem.text)
                    tree = __parse_attribute(elem, parent, 'timestamp', dt, tree)

                except TypeError:
                    logging.info("failed to parse date: " + str(elem.text))
                except ValueError:
                    logging.info("failed to parse date: " + str(elem.text))
                continue

            elif elem.tag.endswith('AuditTrailEntry'):
                if event is not None:
                    raise SyntaxError('file contains <AuditTrailEntry> in another <AuditTrailEntry> tag')
                event = tel_lib.Event()
                tree[elem] = event
                continue

            elif elem.tag.endswith('ProcessInstance'):
                if trace is not None:
                    raise SyntaxError('file contains <ProcessInstance> in another <ProcessInstance> tag')

                trace = log_lib.log.Trace()
                tree[elem] = trace.attributes
                continue

            elif elem.tag.endswith('Process'):
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

            if elem.tag.endswith('AuditTrailEntry'):
                if trace is not None:
                    trace.append(event)
                    event = None
                continue

            elif elem.tag.endswith('ProcessInstance'):
                log.append(trace)
                trace = None
                continue

            elif elem.tag.endswith('Process'):
                continue

    del context

    return log
