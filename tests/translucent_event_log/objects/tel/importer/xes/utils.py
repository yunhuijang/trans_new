from pm4py.objects.petri import semantics


def log_to_tel(net, initial_marking, final_marking, tel):
    '''
    set enabled into the log

    Parameters
    ----------
    :param net: petri net
    :param log: tel object

    Returns
    --------
    translucent event log
    '''

    for trace in tel:
        m = initial_marking
        for event in trace:
            act = event['concept:name']

            for trans in net.transitions:
                if act == trans.label:
                    t = trans
                    break

            en = semantics.enabled_transitions(net, m)
            event.set_enabled(frozenset(en))
            if m == final_marking:
                break
            m = semantics.execute(t, net, m)  # find enabled activity

    return tel