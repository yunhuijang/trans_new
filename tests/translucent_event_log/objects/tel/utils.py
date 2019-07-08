from tests.translucent_event_log.objects.automaton import transition_system as ts

def add_arc_from_to(name, fr, to, auto, data=None):
    """
    Adds a transition from a state to another state in some transition system.
    Assumes from and to are in the transition system!

    Parameters
    ----------
    name: name of the transition
    fr: state from
    to:  state to
    ts: transition system to use
    data: data associated to the Transition System

    Returns
    -------
    None
    """
    tran = ts.TransitionSystem.Transition(name, fr, to, data)
    auto.transitions.add(tran)
    fr.outgoing.add(tran)
    to.incoming.add(tran)

def discover_automaton(tel):
    '''
    Makes an accepting automaton based on translucent event log

    Parameters
    ----------
    tel: translucent event log (tests.translucent_event_log.tel.tel)

    Returns
    --------
    accepting automaton
    '''

    enabled_set = set()
    auto = ts.TransitionSystem()
    id = 0
    final_state = ts.TransitionSystem.State({'final'}, id)
    id+=1
    auto.states.add(final_state)  # final state
    transition_set = set()


    for trace in tel:
        for event in trace:
            en = event['enabled']
            if en not in enabled_set:
                auto.states.add(ts.TransitionSystem.State(en, id))
                id+=1
                enabled_set.add(en)  # make states set (S)

    for trace in tel:
        enabled_list = []
        activity_list = []
        for event in trace:
            enabled_list.append(event['enabled'])
            activity_list.append(event['concept:name'])
        for i in range(len(enabled_list)):
            for state in auto.states:
                if enabled_list[i] == state.name:
                    curr_state = state
                act = activity_list[i]
                if i != len(enabled_list) - 1:
                    if enabled_list[i + 1] == state.name:
                        next_state = state
                else:
                    next_state = final_state
            trans = ts.TransitionSystem.Transition(act, curr_state, next_state)

            if trans not in transition_set:
                auto.transitions.add(trans)
                transition_set.add(trans)
                add_arc_from_to(act, curr_state, next_state, auto)

    for state in auto.states:
        if state.name != {'final'}:
            state.name = set(state.name)

    return auto

def discover_annotated_automaton(tel):
    '''
    Makes annotated Discovered Automaton from accepting automaton

    Parameters
    -----------
    :param tel: translucent event log
    :param automaton: accepting automaton

    Returns
    --------
    annotated discovered automaton
    '''

    aut = discover_automaton(tel)
    state_list = aut.states
    trans_list = aut.transitions

    n = 0
    for trace in tel:
        n += 1
        for i in range(len(trace) - 1):
            curr_time = trace[i]['time:timestamp']
            next_time = trace[i + 1]['time:timestamp']
            t = next_time - curr_time
            for state in state_list:
                if trace[i]['enabled'] == state.name:
                    state.sfreq += 1
                    state.stsum += t
            for trans in trans_list:
                if trace[i]['concept:name'] == trans.name and trace[i]['enabled'] == trans.from_state.name and \
                        trace[i + 1]['enabled'] == trans.to_state.name:
                    trans.afreq += 1
                    trans.atsum += t

    for state in state_list:
        if state.name == {'final'}:  # set state annotations for final state
            state.sfreq = n
            state.stsum = 0
            state.stavg = 0
        else:
            state.stavg = state.stsum / state.sfreq

    for trans in trans_list:  # set transition annotations for transitions goes to final state
        if trans.afreq == 0:
            for trace in tel:
                l = len(trace)
                if trans.name == trace[l - 1]['concept:name'] and trans.to_state.name == {'final'}:
                    trans.afreq += 1

    for trans in trans_list:
        trans.atavg = trans.atsum / trans.afreq


    return aut
