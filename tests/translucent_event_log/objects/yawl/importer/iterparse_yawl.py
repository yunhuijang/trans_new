from lxml import etree
import os
import time
from pm4py.visualization.petrinet import factory as vis_factory
import random
from tests.translucent_event_log.objects.yawl import yawl
from pm4py.objects import petri


def import_yawl(input_file_path):
    '''
    Imports yawl net object (including hidden place and hidden transitions) from yawl file

    Parameters
    ----------
    :param input_file_path: input file path of yawl file

    Returns
    -------
    net, initial marking, final marking
    '''

    tree = etree.parse(input_file_path)
    root = tree.getroot()

    net = yawl.YawlNet('imported_' + str(time.time()))
    marking = yawl.petrinet.Marking()
    fmarking = yawl.petrinet.Marking()

    nett = None
    nettt = None


    for child in root:
        if 'specification' in child.tag:
            nett = child

    places_dict = {}
    trans_dict = {}

    #todo: 일단 여러 net인 경우는 고려 X. 하나만 고려.
    if nett is not None:
        for child in nett:
            if 'decomposition' in child.tag and child.get('isRootNet') == 'true' and child.get('{' + child.nsmap['xsi'] + '}' +'type') == 'NetFactsType':
                dec = child
                for child in dec:
                    if 'processControlElements' in child.tag:
                        nettt = child

    for child in nettt: #set places
        number = 0
        if "condition" in child.tag or "inputCondition" in child.tag or 'outputCondition' in child.tag:
            place_id = child.get("id")
            if "condition" in child.tag:
                for child2 in child:
                    if "name" in child2.tag:
                        place_name = child2.text
            else:
                place_name = place_id
                if "inputCondition" in child.tag:
                    number = 1 #initial marking
                if "outputCondition" in child.tag:
                    number = 2
                    finalmarkings =child
            places_dict[place_id] = yawl.YawlNet.Place(place_id)
            net.places.add(places_dict[place_id]) #add place
            if number == 1:
                marking[places_dict[place_id]] = 1 #set initial marking
            elif number == 2:
                fmarking[places_dict[place_id]] = 1

    for child in nettt: #set transitions
        if 'task' in child.tag:
            trans_name = child.get('id')
            trans_label = trans_name

            for child2 in child:
                if 'name' in child2.tag:
                    if child2.text:
                        trans_label = child2.text
                elif 'join' in child2.tag:
                    join_type = child2.get('code')
                elif 'split' in child2.tag:
                    split_type = child2.get('code')
            trans_dict[trans_name] = yawl.YawlNet.Transition(trans_name, False, join_type, split_type, trans_label)
            net.transitions.add(trans_dict[trans_name])

    for child in nettt: # add arcs
        if "condition" in child.tag or "inputCondition" in child.tag or "task" in child.tag: #place -> transition arc
            for child2 in child:
                if 'flowsInto' in child2.tag:
                    arc_source = child.get('id')
                    for child3 in child2:
                        if 'nextElementRef' in child3.tag:
                            arc_target = child3.get('id')
                    if "task" in child.tag:
                        if arc_target in places_dict:#transition to place
                            petri.utils.add_arc_from_to(trans_dict[arc_source], places_dict[arc_target], net)
                        elif arc_target in trans_dict: #transition to transition (add place between them)
                            place_id = random.randrange(0,1000) # assumption: number of places is less than 500
                            while place_id in places_dict:
                                place_id = random.randrange(0,1000)
                            places_dict[place_id] = yawl.YawlNet.Place(place_id)
                            net.places.add(places_dict[place_id])
                            petri.utils.add_arc_from_to(trans_dict[arc_source], places_dict[place_id], net)
                            petri.utils.add_arc_from_to(places_dict[place_id], trans_dict[arc_target], net)
                    else: #place to transition
                        petri.utils.add_arc_from_to(places_dict[arc_source], trans_dict[arc_target], net)

    #add hidden places, transitions for XOR split, XOR join, OR join
    for trans in net.transitions.copy():
        if not trans.is_hidden:
            new_trans_dict = {}
            if trans.split_type == 'xor': #xor split
                new_trans_dict = {}
                for arcs in trans.out_arcs:
                    trans_name = random.randrange(0,1000)
                    while trans_name in trans_dict:
                        trans_name = random.randrange(0,1000)
                    trans_dict[trans_name] = yawl.YawlNet.Transition(trans_name, True)
                    net.transitions.add(trans_dict[trans_name])
                    new_trans_dict[trans_name] = trans_dict[trans_name]
                    petri.utils.add_arc_from_to(trans_dict[trans_name], arcs.target, net)

                for arcs in trans.out_arcs.copy():
                    source = arcs.source
                    target = arcs.target
                    source.out_arcs.remove(arcs)
                    target.in_arcs.remove(arcs)
                    net.arcs.remove(arcs)

                place_id = random.randrange(0,1000)
                while place_id in places_dict:
                    place_id = random.randrange(0,1000)
                places_dict[place_id] = yawl.YawlNet.Place(place_id, True)
                net.places.add(places_dict[place_id]) # add place for xor split
                petri.utils.add_arc_from_to(trans, places_dict[place_id], net)
                for transs in new_trans_dict.values():
                    petri.utils.add_arc_from_to(places_dict[place_id], transs, net)

                new_trans_dict = {}

            if trans.join_type == 'xor' or trans.join_type == 'or':

                for arc in trans.in_arcs:
                    place = arc.source
                    trans_name = random.randrange(0,1000)
                    while trans_name in trans_dict:
                        trans_name = random.randrange(0,1000)
                    trans_dict[trans_name] = yawl.YawlNet.Transition(trans_name, True)
                    petri.utils.add_arc_from_to(place, trans_dict[trans_name], net)
                    net.transitions.add(trans_dict[trans_name])
                    new_trans_dict[trans_name] = trans_dict[trans_name]

                for arcs in trans.in_arcs.copy():
                    if arc_source not in new_trans_dict:
                        source = arcs.source
                        target = arcs.target
                        source.out_arcs.remove(arcs)
                        target.in_arcs.remove(arcs)
                        net.arcs.remove(arcs)

                place_id = random.randrange(0,1000)
                while place_id in places_dict:
                    place_id = random.randrange(0,1000)
                places_dict[place_id] = yawl.YawlNet.Place(place_id, True)
                net.places.add(places_dict[place_id])
                petri.utils.add_arc_from_to(places_dict[place_id], trans, net)

                for transs in new_trans_dict.values():
                    petri.utils.add_arc_from_to(transs, places_dict[place_id], net)

    return net, marking, fmarking