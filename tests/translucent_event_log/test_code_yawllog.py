from tests.translucent_event_log.objects.yawl import importer as yawl_importer
from tests.translucent_event_log.objects.tel.importer import xes as tel_importer
from tests.translucent_event_log.objects.tel.importer.yawl import utils
import os


input_file_path_yawl = os.path.join("input_data", "SimpleMakeTripProcess.yawl")
input_file_path_log = os.path.join("input_data", "SimpleMakeTripProcess.ywl1.3.xes")

yawlnet, initial_marking, final_marking = yawl_importer.iterparse_yawl.import_yawl(input_file_path_yawl)
yawllog = tel_importer.iterparse_tel.import_tel(input_file_path_log)

tel = utils.yawl_log_to_tel(yawlnet, initial_marking, final_marking, yawllog, 2)

for trace in tel:
    for event in trace:
        if event['lifecycle:transition'] == 'complete':
            print(event['enabled'])
            print(event['concept:name'])
    print("   ")

