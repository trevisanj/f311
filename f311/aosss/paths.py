import a99
import aosss as ao


__all__ = ["get_aosss_path", "get_aosss_data_path", "get_aosss_scripts_path",]


def get_aosss_path(*args):
  """Returns full path aosss package. Arguments are added at the end of os.path.join()"""
  return a99.get_path(*args, module=ao)
  # p = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), *args))
  # return p


def get_aosss_data_path(*args):
    """Returns path to aosss scripts. Arguments are added to the end os os.path.join()"""
    return get_aosss_path("data", *args)


def get_aosss_scripts_path(*args):
    """Returns path to aosss scripts. Arguments are added to the end os os.path.join()"""
    return get_aosss_path("..", "scripts", *args)

