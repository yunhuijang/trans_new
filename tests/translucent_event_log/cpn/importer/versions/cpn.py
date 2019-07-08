import os

from tests.translucent_event_log.cpn import cpn
from pm4py.objects.petri.common import final_marking

def import_net(input_file_path):
    '''
    Import a coloured petri net from a CPN file

    Parameters
    ----------
    :param input_file_path:
        Input file path
    '''

