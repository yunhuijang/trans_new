from tests.translucent_event_log.objects.tel.importer.xes.iterparse_tel import import_tel
from pm4py.objects.log.log import EventLog, Trace

def import_tel_from_yawl(input_file_path):

    '''
    Imports translucent event log from yawl logging

    Parameters
    ----------
    :param input_file_path: input file path of yawl logging

    Returns
    --------
    :return: translucent event log (only complete)
    '''


    log = import_tel(input_file_path)
    new_log = EventLog()
    s = set()
    for trace in log:
        new_trace = Trace()
        ci = trace.attributes['concept:name']
        for event in trace:
            if event['lifecycle:instance'] == ci:
                if event['lifecycle:transition'] == 'schedule':
                    s.add(event['concept:name'])
                elif event['lifecycle:transition'] == 'complete':
                    event.set_enabled(frozenset(s))
                    new_trace.append(event)
                    s.remove(event['concept:name'])
        new_log.append(new_trace)
    return new_log




