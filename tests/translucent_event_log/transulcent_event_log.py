import xml.etree.ElementTree as ET
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.petri.importer import pnml as pnml_importer
from pm4py.objects.petri import semantics
from pm4py.objects.petri.common import initial_marking as ini
from pm4py.algo.discovery.alpha import factory as alpha_miner



def make_enabledlog_alphaminer(log_file_path, output_file_name):
    '''
    Convert XES to XES++ based on alpha miner (event log with enabled activities)
    (for test)

    Parameters
    ----------
    log_file_path
        log's file path to be changed into XES++

    output_file_name
        output file (XES++)'s name

    '''

    log = xes_importer.import_log(log_file_path)
    net, initial_marking, final_marking = alpha_miner.apply(log)

    doc = ET.parse(log_file_path)
    root = doc.getroot()

    for glob in root.iter("global"):
        if glob.attrib["scope"] == "event":
            enabled = ET.SubElement(glob, "string")
            enabled.set("key", "enabled")
            enabled.set("value", "enabled")

    for trace in root.iter("trace"):
        m = ini.discover_initial_marking(net)
        for event in trace.iter("event"):
            for string in event.iter("string"):
                if string.attrib["key"] == "concept:name":
                    act = string.attrib["value"]  # act: current activity in the event log
                    break
            for trans in net.transitions:
                if act == trans.label:
                    t = trans
                    break
            en = semantics.enabled_transitions(net, m)
            enabled = ET.SubElement(event, "string")
            enabled.set("key", "enabled")
            enabled.set("value", en) #write on the XES file
            if m == final_marking:
                break
            m = semantics.execute(t, net, m)


    doc.write(output_file_name, encoding="utf-8", xml_declaration=True)

def mxml_to_log(input_file_path):
    '''
    Convert mxml file into log (CPN Tools make mxml log file)

    Parameters
    ----------
    :param input_file_path
        Input file path (must be mxml file)

    Returns
    ----------
    :return: converted XES file
    '''

    doc = ET.parse(input_file_path)
    root = doc.getroot()  # load mxml file (xml file)

    root.tag = "log"
    for pi in root.iter("ProcessInstance"):
        pi.tag = "trace"
        caseid = ET.SubElement(pi, "string")
        caseid.set("key", "concept:name")
        caseid.set("value", pi.attrib['id'])
    for audit_trail_entry in root.iter("AuditTrailEntry"):
        audit_trail_entry.tag = "event"
    for wme in root.iter("WorkflowModelElement"):
        wme.tag = "string"
        wme.set("key", "concept:name")
        wme.set("value", wme.text)
        wme.text = None
    for timestamp in root.iter("Timestamp"):
        timestamp.tag = "date"
        timestamp.set("key", "time:timestamp")
        timestamp.set("value", timestamp.text)
        timestamp.text = None
    for eventtype in root.iter("EventType"):
        eventtype.tag = "string"
        eventtype.set("key", "lifecycle:transition")
        eventtype.set("value", eventtype.text)
        eventtype.text = None #change xml tags to XES tags

    out_file = input_file_path[:-4]
    out_file += "xes"
    doc.write(out_file, encoding="utf-8", xml_declaration=True)
    xes_file = xes_importer(out_file)
    log = xes_importer.apply(out_file) #get log object

    return log, xes_file


def cpn_to_petrinet(input_file_path):
    '''
    Convert cpn file into petri net

    Parameters
    ----------
    input_file_path
        Input File path (must be cpn file)
    '''

    doc = ET.parse(input_file_path)
    root = doc.getroot() #load cpn file (xml file)

    for child in root.iter("generator"):
        root.remove(child)

    root.tag = "pnml" #change tag to pnml

    n = 0
    for i in range(len(root[0])):
        tag = root[0][n].tag
        if tag == "page":
            n +=1
        else:
            root[0].remove(root[0][n]) #remove tags that are of no use

    root[0].set("id", "net1")
    root[0].set("type", "http://www.pnml.org/version-2009/grammar/pnmlcoremodel") #set pnml type

    for place in root.iter("place"):
        n = 0
        l = len(place)
        for i in range(l):
            tag = place[n].tag
            if tag == "text":
                n+=1
            else:
                place.remove(place[n]) # remove place's child tags that are of no use

    for trans in root.iter("trans"):
        n = 0
        l = len(trans)
        for i in range(l):
            tag = trans[n].tag
            if tag == "text":
                n+=1
            else:
                trans.remove(trans[n]) # remove trans's child tags that are of no use
        trans.tag = "transition"


    for arc in root.iter("arc"):
        n = 0
        l = len(arc)
        for i in range(l):
            tag = arc[n].tag
            if tag == "transend" or tag == "placeend":
                n+=1
            else:
                arc.remove(arc[n]) #remove arc's child tags that are of no use

    for arc in root.iter("arc"):
        if arc.attrib['orientation'] == 'PtoT':
            arc.set("source", arc.find('placeend').attrib['idref'])
            arc.set("target", arc.find('transend').attrib['idref'])
        else:
            arc.set("source", arc.find('transend').attrib['idref'])
            arc.set("target", arc.find('placeend').attrib['idref']) #change arc into right pnml arc

    for text in root.iter("text"):
        text.tag = "name"


    for name in root.iter("name"):
        text = ET.SubElement(name, "text")
        text.text = name.text
        name.text = None

    out_file = input_file_path[:-3]
    out_file += "pnml"
    doc.write(out_file, encoding="utf-8", xml_declaration=True)
    net, initial_marking, final_marking = pnml_importer.import_net(out_file) #get petrinet object

    return net, initial_marking, final_marking

# import os
# import xml.etree.ElementTree as ET
# from tests.translucent_event_log.cpn import cpn
# import time
# from pm4py.objects.petri.common import final_marking
#
# input_file_path = os.path.join("input_data", "reen-pbb.cpn")
#
# tree = ET.parse(input_file_path)
# root = tree.getroot()
#
# net = cpn.cpn('imported_' + str(time.time()))
# marking = cpn.Marking()
# fmarking = cpn.Marking()
#
# nett = None
# page = None
# finalmarkings = None
#
# for child in root:
#     nett = child
#
# if nett is not None:
#     for child in nett:
#         if "page" in child.tag:
#             page = child #todo: hierachial cpn -> more pages
#
# places_dict = {}
# trans_dict = {}
#
#
#
# if page is not None: # deals with place
#     for child in page: #child: each place
#         if "place" in child.tag:
#             token_dict = {}
#             place_id = child.get("id")
#             place_name = place_id
#             for child2 in child:
#                 if "text" in child2.tag and child2.text is not None:
#                     place_name = child2.text
#                 if "type" in child2.tag:
#                     for child3 in child2:
#                         if child3.tag == "text":
#                             place_type = child3.text
#                 if "initmark" in child2.tag:
#                     for child3 in child2:
#                         if child3.tag == "text" and child3.text is not None:
#                             token_str = child3.text
#                             token_split = token_str.split('++')
#                             token_dict = {}
#                             for i in range(len(token_split)):
#                                 token = token_split[i].split('`')
#                                 if len(token) <= 1:
#                                     token_color = token[0]
#                                     token_num = 1
#                                 else:
#                                     token_num = token[0]
#                                     token_color = token[1]
#                                 token_dict[token_color] = token_num
#
#             places_dict[place_id] = cpn.cpn.Place(place_id, place_type)
#             net.places.add(places_dict[place_id])
#             if token_dict != {}:
#                 marking[places_dict[place_id]] = token_dict
#             del place_name
# print(places_dict)
#
#
# if page is not None: #deals with transition
#     for child in page:
#         trans_name = child.get("id")
#         for child2 in child:
#             if "text" in child2.tag: #set transition label
#                 trans_label = child2.text
#             if "cond" in child2.tag: #set transition guard
#                 for child3 in child2:
#                     if "text" in child3.tag:
#                         trans_guard = child3.text #todo: CPN ML Programming: how to deal with guard?
#

