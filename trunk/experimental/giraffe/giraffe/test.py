from project import Project
from worksheet import Worksheet
from lib.ElementTree import dump

project = Project()

data1 = Worksheet('data1', project)
data1.add_column('A')
data1.A = [1, 2, 40]

project.filename = 'test.xml'
project.save()
