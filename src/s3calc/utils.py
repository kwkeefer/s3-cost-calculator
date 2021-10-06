import yaml

def format_float(flt):
    """ Formats a float with commas, rounds to two decimal points, wrapped in quotes

    Args:
        flt: a float
    """
    if flt:
        return '"' + f"{flt:,.2f}" + '"'
    else:
        return None


def _read_config_file(filepath):
    with open(filepath, "r") as f:
        return yaml.safe_load(f.read())
