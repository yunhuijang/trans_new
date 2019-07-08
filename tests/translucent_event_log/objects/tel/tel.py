from pm4py.objects.log.log import Event

class Event(Event):

    def __init__(self, *args, **kwargs):
        self._dict = dict(*args, **kwargs)
        if 'enabled' in args:
            self._enabled = args['enabled']
        else:
            {}

    def set_enabled(self, value):
        self._enabled = value
        self._dict['enabled'] = value

    def _get_enabled(self):
        return dict(self)['enabled']

    enabled = property(_get_enabled)
