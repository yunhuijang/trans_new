from pm4py.objects.petri import utils as petri_utils
from pm4py.objects.petri.petrinet import PetriNet
from pm4py.objects.petri.common.initial_marking import discover_initial_marking
from pm4py.objects.petri.common.final_marking import discover_final_marking
from itertools import combinations


def minimal_region_set(auto):
    '''
    Make minimal region set from accepting automaton
    :param auto: Accepting automaton
    :return: minimal region set
    '''

    e = set()  # event list
    ger_dict = {}  # GER(e) dictionary
    post_dict = {}
    for trans in auto.transitions:
        if trans.name not in e:
            e.add(trans.name)

    for event in e:  # make ger dict
        ger_dict[event] = set()
        for state in auto.states:
            for a in state.name:
                if a != 'final':
                    if event == a.name:
                        ger_dict[event].add(state)

    for event in e:
        post_dict[event] = set()
        for state in auto.states:
            for a in state.incoming:
                if a.name == event:
                    post_dict[event].add(state)

    region_set = set()  # minimal region set
    r_set = set()
    region_dict = {}  # region's enter
    r_list = []

    for ger in ger_dict.values():
        r_list.append(ger)

    for post in post_dict.values():
        r_list.append(post)

    for i in r_list:
        r_set.add(frozenset(i))

    for state_set in r_set:  # for each minimal region candidates
        enter = set()
        exit = set()
        in_ = set()
        out = set()
        for trans in auto.transitions:
            if trans.from_state in state_set:
                if trans.to_state in state_set:
                    in_.add(trans.name)
                else:
                    exit.add(trans.name)
            else:
                if trans.to_state in state_set:
                    enter.add(trans.name)
                else:
                    out.add(trans.name)
        cond_dict = {}

        for event in e:
            cond_dict[event] = ''
            if event in enter:
                cond_dict[event] += 'enter'  # enter
            if event in exit:
                cond_dict[event] += 'exit'  # exit
            if event in in_ or event in out:
                cond_dict[event] += 'not cross'  # not cross

        is_region = True
        for i in cond_dict.values():
            if i != 'enter' and i != 'exit' and i != 'not cross':  # check whether it is region or not
                is_region = False

        if is_region:
            region_set.add(state_set)
            region_dict[state_set] = (enter, exit)

    return region_set, region_dict, ger_dict

def check_no_self_loop(auto):
    '''
    Check transitions system contains no self loop
    :param auto: input automaton
    :return: if there is no self loop, return True. else: return False
    '''

    for trans in auto.transitions:
        if trans.from_state == trans.to_state:
            return False
    return True

def check_transitions_signal_choices(auto):
    '''
    Check transition system's transitions signal choices
    :param auto: input automaton
    :return: if there is only one unique arc per pair of states, return True. else: return False
    '''

    for state in auto.states:
        out_trans_pair = list(combinations(state.outgoing, 2))
        for pair in out_trans_pair:
            if pair[0].to_state == pair[1].to_state:
                return False
    return True

# def check_event_reachability(auto):


def check_state_separation_property(auto):
    '''
    Check State Separation Property of Transition System
    :param auto: input automaton
    :return: if property holds, return True. else: return False
    '''
    min_region_set, di, ger = minimal_region_set(auto)
    state_pair = list(combinations(auto.states, 2))

    for pair in state_pair:
        sep_region_dict = {}
        sep_region_dict[1] = set()
        sep_region_dict[2] = set()
        for region in min_region_set:
            if pair[0] in region:
                sep_region_dict[1].add(region)
            if pair[1] in region:
                sep_region_dict[2].add(region)
        if sep_region_dict[1] == sep_region_dict[2]:
            return False

    return True


def check_forward_closure_property(auto):
    '''
    Check Forward Closure Property of Transition System
    :param auto: input automaton
    :return: if property holds, return True. else: return False
    '''
    min_region_set, di, ger_dict = minimal_region_set(auto)
    trans_dict = {}

    for trans in auto.transitions:
        trans_dict[trans.name] = {}
        trans_dict[trans.name]['pre-regions'] = set()
        trans_dict[trans.name]['states_in_all'] = set()
        trans_dict[trans.name]['enabled'] = False

        for min_region in di.items():  # for each minimal regions
            for t in min_region[1][1]:  # for exit transitions
                if trans.name == t:
                    trans_dict[trans.name]['pre-regions'].add(min_region[0])

    for trans in trans_dict.items():
        s = []
        for region in trans[1]['pre-regions']:
            s.append(region)
        r = s[0]
        for j in range(len(s)):
            r = r.intersection(s[j])
        trans_dict[trans[0]]['states_in_all'] = r
        if trans_dict[trans[0]]['states_in_all'] == ger_dict[trans[0]]:
            trans_dict[trans[0]]['enabled'] = True

    for trans in trans_dict.items():
        if not trans_dict[trans[0]]['enabled']:
            return False

    return True


def make_petrinet_from_automaton(auto):
    '''
    Make petri net from automaton based on state-based region theory
    :param auto: automaton
    :return: derived petri net
    '''
    min_region_set, di, ger = minimal_region_set(auto)

    id = 0
    net = PetriNet('new_net')
    trans_set = set()
    for trans in auto.transitions:
        if trans.name not in trans_set:
            t = PetriNet.Transition(trans.name, trans.name)
            net.transitions.add(t)
            trans_set.add(trans.name)

    for min_region in di.items():
        place = PetriNet.Place(id)
        net.places.add(place)
        for trans in min_region[1][0]:
            for transs in net.transitions:
                if trans == transs.name:
                    petri_utils.add_arc_from_to(transs, place, net)
        for trans in min_region[1][1]:
            for transs in net.transitions:
                if trans == transs.name:
                    petri_utils.add_arc_from_to(place, transs, net)
        id += 1

    im = discover_initial_marking(net)
    fm = discover_final_marking(net)

    return net, im, fm

def check_elementary_ts(auto):
    '''
    Check the transitions system is elementary or not
    :param auto: input automaton
    :return: if it is elementary, return True. else: return False
    '''

    if check_state_separation_property(auto) and check_forward_closure_property(auto) and check_no_self_loop(auto) and check_transitions_signal_choices(auto):
        return True
    else:
        return False