"""
Maintains a dictionary of valid Graphite message templates.
See: https://github.com/influxdata/influxdb/tree/master/services/graphite
"""

class Template(object):
    """
    Create a lookup dictionary for quick template access (e.g. by an encoder)

    Definitions:
        metric-name: first part if a Graphite message
        metric-range: number of dots '.' in a metric-name

    Templates matching a given Graphite message must have the same
    metric-range. metric-names match on shorter templates if a templates
    ends with a wildcard '*'. More specific templates match first.
    """
    def __init__(self, templates):
        d = {}
        for template in templates:
            length = template.count('.')
            d[length] = template
        self.templates = d

    def get(self, key):
        try:
            return self.templates[key]
        except KeyError:
            # TODO: make this faster?
            key -= 1
            while key >= 0:
                template = self.templates.get(key)
                if template and template.endswith('*'):
                    return template
                key -= 1
        return None
