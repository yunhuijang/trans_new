import copy
from pm4py.objects.petri.semantics import execute as petri_execute
from pm4py.objects.petri.petrinet import Marking

def is_enabled(t, yn, m):
    '''
    Check if Transition t is enabled or not in Marking m

    Parameters
    -----------
    :param t: transition of yawl net
    :param yn: yawl net
    :param m: marking

    Returns
    --------
    if t is enabled, return True

    '''

    flag = False
    is_trans_hid = False
    if t not in yn.transitions:
        return False
    else:
        for a in t.in_arcs:
            if not a.source.is_hidden:
                if m[a.source] < a.weight:
                    return False
            else:
                for b in a.source.in_arcs:
                    for c in b.source.in_arcs:
                        for d in c.source.in_arcs:
                            if d.source.is_hidden:
                                is_trans_hid = True
                                for e in d.source.in_arcs:
                                    if m[e.source] < e.weight:
                                        return False
                if not is_trans_hid:
                    p = a.source
                    for b in p.in_arcs:
                        if is_enabled(b.source, yn, m):
                            flag = True
                            return True
                    if not flag:
                        return False
    return True


def execute(t, yn, m):
    mm = Marking()
    mmm = Marking()
    m_out = copy.copy(m)

    if not is_enabled(t, yn, m):
        #if it should not be executed, just execute it and return original marking + executed marking
        for arcs in t.out_arcs:
            m[arcs.target] += 1
        return m

    for a in t.in_arcs:
        p = a.source
        if not p.is_hidden or m[p] >= a.weight:
            m_out = petri_execute(t, yn, m)
        else:
            for c in p.in_arcs:
                for d in c.source.in_arcs:
                    for e in d.source.in_arcs:
                        if e.source.is_hidden:
                            mmm = petri_execute(e.source, yn, m)
                            if mmm is not None and len(mmm) > 0:
                                break
                        if mmm is not None and len(mmm) > 0:
                            break
                    if mmm is not None and len(mmm) > 0:
                        break
                for b in p.in_arcs:
                    if mmm is not None and len(mmm) > 0:
                        mm = petri_execute(b.source, yn, mmm)
                        if mm is not None:
                            break
                    else:
                        mm = petri_execute(b.source, yn, m)
                        if mm is not None:
                            break
                m_out = petri_execute(t, yn, mm)

    return m_out


def enabled_transitions(yn, m):
    enabled = set()
    for t in yn.transitions:
        if not t.is_hidden:
            if is_enabled(t, yn, m):
                enabled.add(t)

    return enabled