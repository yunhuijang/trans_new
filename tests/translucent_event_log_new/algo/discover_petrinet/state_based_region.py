from itertools import chain, combinations, product
from pm4py.objects.petri.petrinet import PetriNet
from pm4py.objects.petri import utils as petri_utils
from pm4py.objects.petri.common.initial_marking import discover_initial_marking
from pm4py.objects.petri.common.final_marking import discover_final_marking


def transition_dict(auto):
    dic = {}
    for trans in auto.transitions:
       dic[trans.name] = trans

    return dic


def find_GER(auto, e):
    '''
    Find ger(e) for each event

    Parameters
    ----------
    :param auto: automaton
    :param e: event e's name (string)

    Returns
    --------
    :return: ger_set for e
    '''

    ger_set = set()

    for state in auto.states:
        if e in str(state.name):
            ger_set.add(state)

    return ger_set


def generate_minimal_pre_region(auto, e):
    '''
    Make minimal region set for automaton

    Parameters
    ----------
    e: event

    Returns
    ---------
    minimal pre region set

    '''
    pre_region = set()
    explored = set()
    ger = find_GER(auto, e)
    expand_states(auto, ger, pre_region, explored)
    return pre_region


def is_region(auto, r):
    '''
    find whether r is a region or not

    Parameters
    -----------
    :param auto: automaton
    :param r: set of states

    Returns
    ---------
    :return: if r is region: return True else: return False
    '''
    enter = set()
    exit_ = set()
    in_ = set()
    out = set()

    for trans in auto.transitions:
        # if type(r) == set:
        if trans.from_state in r:
            if trans.to_state in r:
                in_.add(trans)
            else:
                exit_.add(trans)
        else:
            if trans.to_state in r:
                enter.add(trans)
            else:
                out.add(trans)

    trans_dict = {}
    for trans in auto.transitions:
        trans_dict[trans.name] = 0
    for trans in auto.transitions:
        if trans in in_ and trans_dict[trans.name]%10 < 1:
            trans_dict[trans.name] += 1
        if trans in out and (trans_dict[trans.name]%100)/10 <1:
            trans_dict[trans.name] += 10
        if trans in exit_ and (trans_dict[trans.name]%1000)/100 <1:
            trans_dict[trans.name] += 100
        if trans in enter and (trans_dict[trans.name]%10000)/1000 <1:
            trans_dict[trans.name] += 1000

    for t in trans_dict:
        if trans_dict[t] not in {1, 10, 100, 1000, 11}:
            return False, trans_dict

    return True, trans_dict


def expand_states(auto, r, R, explored):
    '''
    Find expanded minimum pre-regions from ger

    Parameters
    -----------
    :param auto: automaton
    :param r: set of states to be expanded (region candidate)
    :param R: set of all regions
    :param explored: set of expansions already generated

    Returns
    --------
    :return: minimal pre-region set
    '''
    if r in explored:
        return #avoids to repeat previous expansions

    is_reg, trans_dict = is_region(auto, r)
    if is_reg:
        for re in R.copy():
            if r.issubset(re):
                R.remove(re) #remove supersets of r
        flag = True
        for re in R:
            if re.issubset(r):
                flag = False
        if flag:
            R.add(frozenset(r)) #r is minimal among R
        return

    #begin expanding
    for trans in auto.transitions:
        if trans_dict[trans.name] not in {1,10,100,1000,11}:
            e = trans
            break
    num = trans_dict[e.name] #determine the state of lemma 4.2

    #one direction
    trans_set = set()
    for trans in auto.transitions:
        if trans.name == e.name:
            trans_set.add(trans)
    if num in {1001, 101, 1011, 111, 1100, 1111, 1101, 1110}: #lemma 1, 2
        rr = r
        for t in trans_set:
            if t.to_state in r and t.from_state not in r:
                rr = rr.union({t.from_state})
            if t.to_state not in r and t.from_state in r:
                rr = rr.union({t.to_state})

    elif num == 1010: #lemma 3
        for t in trans_set:
            if t.to_state in r and t.from_state not in r:
                rr = r.union({t.from_state})

    elif num == 110: #lemma 4
        for t in trans_set:
            if t.from_state in r and t.to_state not in r:
                rr = r.union({t.to_state})

    expand_states(auto, rr, R, explored)
    explored.add(frozenset(rr))

    #two directions
    if num == 1010:
        for t in trans_set:
            if t.from_state not in r and t.to_state not in r:
                rr = r.union({t.to_state})
    elif num == 110:
        for t in trans_set:
            if t.to_state not in r and t.from_state not in r:
                rr = r.union({t.from_state})
    if explored is None:
        explored = set()

    expand_states(auto, rr, R, explored)
    explored.add(frozenset(rr))


def is_excitation_closure(auto, e):
    '''

    :param e:
    :return:
    '''
    pre = generate_minimal_pre_region(auto, e)
    if pre is None or len(pre) < 1:
        inter = set()
    else:
        inter = pre.pop()
        for r in pre:
            inter = inter & r

    if inter == find_GER(auto, e) or pre is None:
        return True, inter
    else:
        return False, inter


def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


def sum_digit(num):
    if num < 10:
        return num
    return num % 10 + sum_digit(num/10)


def split_labels(auto, e):
    '''
    split labels for event e

    Parameters
    ----------
    auto: automaton
    e: event name

    Returns
    --------
    newauto: new automaton with splitted label

    '''


    cand_set = set()
    flag, inter = is_excitation_closure(auto, e) #checke whether ec or not
    if not flag:
        ger = find_GER(auto, e)
        pset = powerset(inter)
        for i in pset:
            if i.issubset(ger):
                cand_set.add(frozenset(i)) #make candidate set which is subset of ger and superset of intersections

    cost_dic = {}
    for i in cand_set:
        split_event_set = set()
        sum = 0
        dic = is_region(auto, i)[1]
        new_dic = {}
        for t in dic:
            new_dic[t] = sum_digit(dic[t]) #if value > 1, event t violates region
        for key, values in new_dic.items():
            if values > 1:
                split_event_set.add(key) #key violates region

        for j in new_dic.values():
            sum += j
        cost_dic[i]['cost'] = sum - len(new_dic)
        cost_dic[i]['split'] = split_event_set

    #split_re: proper subset including GER
    #split_act: activity that needs to be splitted
    split_re, split_act = min(cost_dic.items(), key = (lambda k: cost_dic[k])) #find the minimum set that violates region

    no_cross = {}
    exit_ = {}
    enter = {}

    newauto = auto
    for trans in newauto.transitions:
        if trans.name in split_act:
            no_cross[trans.name] = set()
            exit_[trans.name] = set()
            enter[trans.name] = set()

            if trans.from_state in split_re:
                if trans.to_state in split_re:
                    no_cross[trans.name].add(trans)
                else:
                    exit_[trans.name].add(trans)
            else:
                if trans.to_state in split_re:
                    enter[trans.name].add(trans)
                else:
                    no_cross[trans.name].add(trans)

    for trans in split_act:
        for tt in newauto.transitions:
            for t in exit_[trans.name]:
                if t == tt:
                    tt.name = tt.name + '1'
            for t in no_cross[trans.name]:
                if t == tt:
                    tt.name = tt.name + '2'
            for t in enter[trans.name]:
                if t == tt:
                    tt.name = tt.name + '3'

    return newauto

def is_essential(auto):

    '''
    for each minimal pre region in automaton, determine whether region is essential or not

    Parameters
    ----------
    auto: input automaton

    Return
    --------
    pre_region_dict: events for each pre region
    essential_region_dict: True: essential region / False: non essential region

    '''


    pre_region_dict = {}
    essential_region_dict = {}
    min_cover_cand_dict = {}

    for trans in auto.transitions:
        region_set = generate_minimal_pre_region(auto, trans.name)
        for r in region_set:
            try:
                pre_region_dict[r].add(trans.name)
            except KeyError:
                pre_region_dict[r] = set()
                pre_region_dict[r].add(trans.name)

    for trans in auto.transitions:
        pre_region_set = set()
        er = find_GER(auto, trans.name)  # find ER(e)
        for key, value in pre_region_dict.items():
            if trans.name in value:
                pre_region_set.add(key)  # find pre_region_set for e

        combi_set = set()
        if len(pre_region_set) >= 2:
            for i in range(2, len(pre_region_set) + 1):
                combi_set.add(combinations(pre_region_set, i))  # make combi set to find intersection

            for i in combi_set:
                for j in i:  # j: each combination
                    for k in range(len(j)):  # k: each element in intersection(each region):
                        if k == 0:
                            inter = j[k]
                        else:
                            inter = inter.intersection(j[k])  # intersection for j

                    if inter != er:
                        min_cover_cand = pre_region_set - set(j)
                        try:
                            min_cover_cand_dict[trans.name].add(frozenset(min_cover_cand))
                        except KeyError:
                            min_cover_cand_dict[trans.name] = set()
                            min_cover_cand_dict[trans.name].add(frozenset(min_cover_cand))
                        for k in range(len(j)):
                            essential_region_dict[j[k]] = False
                    else:
                        for k in range(len(j)):
                            essential_region_dict[j[k]] = True
        else:
            for i in pre_region_set:
                essential_region_dict[i] = True

    return min_cover_cand_dict, essential_region_dict

def irredundant_place_cand(auto):

    min_cover_cand_dict, essential_dict = is_essential(auto)
    sol_cand = []
    if min_cover_cand_dict:
        binary_dict = {}

        l = [True, False]
        tf_list = product(l, repeat=len(essential_dict)) #generate tf_list to find solutions

        for j in tf_list:
            for num in j:
                for region in essential_dict:
                    binary_dict[region] = j[num]

            final_condition = True
            for value in min_cover_cand_dict.values():
                cond = []
                for i in value:
                    if len(i) == 1:
                        cond.append(binary_dict[i])
                    else:
                        con = True
                        for j in i:
                            con = con and binary_dict[j]
                        cond.append(con)
                condition = cond[0]
                for i in range(len(cond)):
                    condition = condition or cond[i]
                final_condition = final_condition and condition
            if final_condition: # the eq is 1
                sol_cand.append(binary_dict)

    return sol_cand #solution candidates (regions which has False values can be removed)

def find_irredundant_cover(sol_cand):

    '''
    Find which region is irredundant (based on number of places)

    '''
    min = 10000000
    sol = None
    for i in sol_cand:
        count = 0
        for value in i.values():
            if value:
                count += 1
        if count < min:
            min = count
            sol = i
    return sol #solution (regions with False value have to be removed)

def map_to_PN(auto, region_set):
    '''
    Make Petri net from automaton

    :param auto: automaton to change into petri net
    :return: petri net
    '''

    net = PetriNet("New Net")
    trans_set = set()
    for trans in auto.transitions:
        if trans.name not in trans_set:
            t = PetriNet.Transition(trans.name, trans.name)
            net.transitions.add(t)
            trans_set.add(trans.name) #add transitions to petri net


    petri_trans_dict = transition_dict(net)
    id = 0
    for region in region_set:
        exit_set = set()
        enter_set = set()
        place = PetriNet.Place(id) #add places to petri net
        net.places.add(place)
        for event, value in is_region(auto, region)[1].items():
            if value == 100: # exit
                exit_set.add(event)
            elif value == 1000: # enter
                enter_set.add(event)
        for t in exit_set:
            petri_utils.add_arc_from_to(place, petri_trans_dict[t], net)
        for tt in enter_set:
            petri_utils.add_arc_from_to(petri_trans_dict[tt], place, net)
        id +=1

    #add final place (optional)
    # final_place = PetriNet.Place(id)
    # net.places.add(final_place)
    # for trans in net.transitions:
    #     if len(trans.out_arcs) < 1:
    #         petri_utils.add_arc_from_to(trans, final_place, net)

    im = discover_initial_marking(net)
    fm = discover_final_marking(net)

    return net, im, fm

def petri_net_synthesis(auto):

    split = True
    newauto = auto
    while split: #label splitting
        split = False #flag (until splitting is not needed)
        for e in newauto.transitions:
            if not is_excitation_closure(auto, e.name):
                newauto = split_labels(auto, e)
                split = True

    sol_cand = irredundant_place_cand(newauto)
    sol = find_irredundant_cover(sol_cand)


    region_set = set()
    for trans in newauto.transitions:
        r = generate_minimal_pre_region(newauto, trans.name)
        if r is not None:
            if sol is not None:
                if sol[r]:
                    for reg in r:
                        region_set.add(frozenset(reg))
            else:
                for reg in r:
                    region_set.add(frozenset(reg))

    return map_to_PN(newauto, region_set)




