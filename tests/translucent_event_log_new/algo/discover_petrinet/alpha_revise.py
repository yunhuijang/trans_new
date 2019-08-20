import time

from pm4py.algo.discovery.alpha.data_structures import alpha_classic_abstraction
from pm4py.algo.discovery.dfg.versions import native as dfg_inst
from pm4py.algo.discovery.dfg.utils import dfg_utils
from pm4py.objects import petri
from pm4py.algo.discovery.alpha.versions import classic
from pm4py.objects.petri.petrinet import Marking


def trans_alpha(log):
    dfg = {k: v for k, v in dfg_inst.apply(log).items() if v > 0}
    start_activities = dfg_utils.infer_start_activities(dfg)
    end_activities = dfg_utils.infer_end_activities(dfg)

    labels = set()
    for el in dfg:
        labels.add(el[0])
        labels.add(el[1])
    for a in start_activities:
        labels.add(a)
    for a in end_activities:
        labels.add(a)
    labels = list(labels)

    alpha_abstraction = alpha_classic_abstraction.ClassicAlphaAbstraction(start_activities, end_activities, dfg)

    pairs = list(map(lambda p: ({p[0]}, {p[1]}),
                     filter(lambda p: classic.__initial_filter(alpha_abstraction.parallel_relation, p),
                            alpha_abstraction.causal_relation)))

    parallel_set = alpha_abstraction.parallel_relation
    loop_set = set()
    for rel in parallel_set.copy():
        pre_act = rel[0]
        post_act = rel[1]
        for trace in log:
            for i in range(len(trace)):
                    if trace[i]['concept:name'] == pre_act and trace[i+1]['concept:name'] == post_act:
                        pre_en = trace[i]['enabled']
                        if post_act in pre_en:
                            pass
                        else:
                            loop_set.add((pre_act, post_act)) #find loops based on enabling information

    for i in range(0, len(pairs)):
        t1 = pairs[i]
        for j in range(i, len(pairs)):
            t2 = pairs[j]
            if t1 != t2:
                if t1[0].issubset(t2[0]) or t1[1].issubset(t2[1]):
                    if not (classic.__check_is_unrelated(alpha_abstraction.parallel_relation, alpha_abstraction.causal_relation,
                                                 t1[0], t2[0]) or classic.__check_is_unrelated(
                        alpha_abstraction.parallel_relation, alpha_abstraction.causal_relation, t1[1], t2[1])):
                        new_alpha_pair = (t1[0] | t2[0], t1[1] | t2[1])
                        if new_alpha_pair not in pairs:
                            pairs.append((t1[0] | t2[0], t1[1] | t2[1]))

    internal_places = filter(lambda p: classic.__pair_maximizer(pairs, p), pairs)
    net = petri.petrinet.PetriNet('alpha_classic_net_' + str(time.time()))
    label_transition_dict = {}

    for i in range(0, len(labels)):
        label_transition_dict[labels[i]] = petri.petrinet.PetriNet.Transition(labels[i], labels[i])
        net.transitions.add(label_transition_dict[labels[i]])

    for pair in internal_places:
        for loop in loop_set:
            if loop[0] in pair[0]:
                pair[1].add(loop[1])
            if loop[0] in pair[1]:
                pair[0].add(loop[1]) #add arcs in loop

        place = petri.petrinet.PetriNet.Place(str(pair))
        net.places.add(place)

        for in_arc in pair[0]:
            petri.utils.add_arc_from_to(label_transition_dict[in_arc], place, net)
        for out_arc in pair[1]:
            petri.utils.add_arc_from_to(place, label_transition_dict[out_arc], net)

    src = classic.__add_source(net, alpha_abstraction.start_activities, label_transition_dict)
    sink = classic.__add_sink(net, alpha_abstraction.end_activities, label_transition_dict)

    return net, Marking({src: 1}), Marking({sink: 1})