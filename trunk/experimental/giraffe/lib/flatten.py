# From: "Raymond Hettinger" <vze4rx4y@verizon.net>
# Newsgroups: comp.lang.python
# Subject: Re: Itertools wishlists
# Date: Mon, 14 Mar 2005 18:52:21 GMT
# 
# >     Steven> complex atomicity test).  I also have the feeling that any
# >     Steven> complicated atomictiy test is more than a simple and-ing
# >     Steven> of several tests...
# 
# "Ville Vainio"
# > I also have the feeling that if the atomicity criterion was any more
# > complex in the API, the proposal would be shot down immediately on the
# > grounds of not being fundamental enough as concept.
# 
# Would this meet your needs?

def flatten(iterable, atomic_iterable_types=(basestring,)):
    iterstack = [iter(iterable)]
    while iterstack:
        for elem in iterstack[-1]:
            if not isinstance(elem, atomic_iterable_types):
                try:
                    it = iter(elem)
                except TypeError:
                    pass
                else:
                    iterstack.append(it)
                    break
            yield elem
        else:
            iterstack.pop() # only remove iterator when it is exhausted

#
# Raymond Hettinger
