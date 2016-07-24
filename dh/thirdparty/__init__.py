"""
Third-party modules which are essential and must always available.

For maximum compatibility, these modules should be pure Python without
non-standard dependencies.

List of modules:

  * atomicwrites (https://github.com/untitaker/python-atomicwrites)
  * pypng (https://github.com/drj11/pypng)
  * tabulate (https://bitbucket.org/astanin/python-tabulate)
  * tqdm (https://github.com/tqdm/tqdm)

"""


###
#%% wrappers for "atomicwrites" module
###


import dh.thirdparty.atomicwrites
awopen = dh.thirdparty.atomicwrites.atomic_write

