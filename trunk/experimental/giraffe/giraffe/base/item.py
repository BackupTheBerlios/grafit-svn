from giraffe.common.commands import Command, command_list

storage_desc = {}

def register_class(cls, description):
    storage_desc[cls] = description

def wrap_attribute(name):
    def get_data(self):
        return getattr(self.data, name)
    def set_data(self, value):
        setattr(self.data, name, value)
    return property(get_data, set_data)

class Item(object):
    def __init__(self, project, id=None):
        self.project = project
        self._update(id)

    def _update(self, id):
        self.view, self.data, self.id = self.project.add(self, id)

    description = 'items[name:S,id:S]'
    name = wrap_attribute('name')
