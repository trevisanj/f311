# # Gear for finding files


import os
import hypydrive as hpd


def get_path(*args, module=hpd):
  """Returns full path to hypydrive package, or else specified module.

  Arguments are added at the end of os.path.join()"""
  p = os.path.abspath(os.path.join(module.__path__[0], *args))
  return p


def get_default_data_path(*args, module=hpd):
  """Returns full path to object inside the default data directory"""
  p = get_path("data", "default", *args, module=module)
  return p


def get_data_path(*args, module=hpd):
  """Returns full path to object inside data directory"""
  p = get_path("data", *args, module=module)
  return p


# TODO this may really not be the case: get_scripts_path
def get_scripts_path(*args, module=hpd):
    """Returns path to pyfant scripts. Arguments are added to the end os os.path.join()"""
    return get_path("scripts", *args, module=module)


