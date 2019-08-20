
def tel_set_enabled(tel):

    '''
    set enabled attribute in tel file

    :param tel:
    :return:
    '''

    for trace in tel:
        for event in trace:
            if event['enabled'] != 'set()':
                en_list = event['enabled'][1:-1].split(',')
                en = set()
                for i in en_list:
                    en.add(i)
                event.set_enabled(frozenset(en))
            else:
                event.set_enabled(frozenset())

    return tel