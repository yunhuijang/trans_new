from tests.translucent_event_log.objects.yawl import semantics

def yawl_log_to_tel(yawlnet, initial_marking, final_marking, yawllog, parameters = 2):
    '''

    Converts Yawl Log into Translucent Event Log

    '''

    for trace in yawllog:
        m = initial_marking
        for event in trace:
            if event['lifecycle:transition'] == 'complete':
                if parameters == 1: #yawl_simulated_log (mxml file)
                    act = event['activity']

                elif parameters == 2: #yawl logging (XES file)
                    act = event['concept:name']

                for trans in yawlnet.transitions:
                    if act == trans.name:
                        t = trans
                        break

                en = semantics.enabled_transitions(yawlnet, m)
                event.set_enabled(frozenset(en))
                if m == final_marking:
                    break
                m = semantics.execute(t, yawlnet, m)

    return yawllog

