import sys
import metakit
import cPickle as pickle

def wrap(value, type):
    if type == 'V':
        return view_to_list(value)
    else:
        return value

def view_to_list(view):
    return list(dict((prop.name, wrap(getattr(row, prop.name), prop.type)) 
                     for prop in view.structure()) 
                for row in view)

db = metakit.storage(sys.argv[1], 0)

views = []

desc = db.description()
sofar = []
add = sofar.append
depth = 0
for c in desc:
    if c == '[': depth += 1
    elif c == ']': depth -= 1
    if depth == 0 and c == ',':
        views.append("".join(sofar))
        sofar[:] = []
    else:
        add(c)
views.append("".join(sofar))

di = dict(zip(views, [view_to_list(db.getas(v)) for v in views]))

print "converted succesfully"

#####

db = metakit.storage('out.db', 1)

def fill(view, data):
    for row in data:
        attrs = dict((k, v) for k, v in row.iteritems() if not isinstance(v, list))
        subviews = dict((k, v) for k, v in row.iteritems() if isinstance(v, list))
        ind = view.append(**attrs)
        for name, value in subviews.iteritems():
            fill(getattr(view[ind], name), value)

for viewdesc, data in di.iteritems():
    view = db.getas(viewdesc)
    fill(view, data)

db.commit()

print "converted succesfully"
