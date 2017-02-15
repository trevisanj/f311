import re
import a99

__all__ = ["compile_simids"]

def compile_simids(specs):
    """
    Compiles a list of simulation IDs (e.g., 'C000793') from a sequence of specifications

    Args:
        specs: ``[spec0, spec1, ...]``, where each element may be:

            - a number (convertible to int), or

            - a range such as '1000-1010' (string)

    Returns: list of strings starting with "C"
    """
    numbers = []
    for candidate in specs:
        try:
            if '-' in candidate:
                groups = re.match('(\d+)\s*-\s*(\d+)$', candidate)
                if groups is None:
                    raise RuntimeError("Could not parse range")
                n0 = int(groups.groups()[0])
                n1 = int(groups.groups()[1])
                numbers.extend(list(range(n0, n1 + 1)))
            else:
                numbers.append(int(candidate))
        except Exception as E:
            a99.get_python_logger().info("SKIPPED Argument '%s': %s" % (candidate, str(E)))
    numbers = set(numbers)
    simids = ["C%06d" % n for n in numbers]

    return simids
