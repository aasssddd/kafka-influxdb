"""Encoder for snap-plugin-publisher-kafka."""
try:
    import ujson as json
except ImportError:
    import json
import logging
import datetime
import time

try:
    # Test for mypy support (requires Python 3)
    from typing import List, Text
except:
    pass


class Encoder(object):
    """.

    An encoder for the snap-plugin-publisher-kafka JSON format
    See https://github.com/intelsdi-x/snap-plugin-publisher-kafka

    Sample measurements:

    {
        "timestamp":"2017-09-19T14:56:07.863770559Z",
        "namespace":"/intel/docker/225c1a3e9f65/stats/filesystem/xvda1/writes_merged",
        "data":1.4012927170541047,
        "dataRate":null,
        "unit":"",
        "tags":{
            "annotation.io.kubernetes.container.hash":"84aff253",
            "annotation.io.kubernetes.container.ports":"[{\"hostPort\":8081,\"containerPort\":8081,\"protocol\":\"TCP\"},{\"hostPort\":4040,\"containerPort\":4040,\"protocol\":\"TCP\"}]",
            "annotation.io.kubernetes.container.restartCount":"0",
            "annotation.io.kubernetes.container.terminationMessagePath":"/dev/termination-log",
            "annotation.io.kubernetes.container.terminationMessagePolicy":"File",
            "annotation.io.kubernetes.pod.terminationGracePeriod":"30",
            "deploymentId":"",
            "io.kubernetes.container.logpath":"/var/log/pods/f5c0b6cb-9d49-11e7-8b0f-0e74cc86d65c/spark-worker2_0.log",
            "io.kubernetes.container.name":"spark-worker2",
            "io.kubernetes.docker.type":"container",
            "io.kubernetes.pod.name":"spark-worker2-3627921749-2dszx",
            "io.kubernetes.pod.namespace":"default",
            "io.kubernetes.pod.uid":"f5c0b6cb-9d49-11e7-8b0f-0e74cc86d65c",
            "io.kubernetes.sandbox.id":"7af02489c3873d150d19259d82641d56daad40cc872ce941e3be785b79f6642f",
            "nodename":"ip-10-0-17-95.ec2.internal",
            "plugin_running_on":"snap-3490148048-prllg"
        },
        "version":8,
        "last_advertised_time":"2017-09-19T14:56:08.863770559Z"
    }

    """

    def encode(self, msg):
        # type: (bytes) -> List[Text]
        measurements = []

        for line in msg.decode().split("\n"):
            try:
                # Set flag for float precision to get the same
                # results for Python 2 and 3.
                json_object = self.parse_line(line.replace("\\", "\\\\"))
            except ValueError as e:
                logging.debug("Error in encoder: %s", e)
                continue
            try:
                # to set plugin, plugin_instance as the measurement name, just need pass ['plugin', 'plugin_instance']
                for ent in json_object:
                    measurement = Encoder.format_measurement_name(ent, ['namespace'])
                    tags = Encoder.format_tags(ent, ['tags'])
                    value = Encoder.format_value(ent)
                    time = Encoder.format_time(ent)
                    measurements.append(Encoder.compose_data(measurement, tags, value, time))
            except Exception as e:
                logging.debug("Error in input data: %s. Skipping.", e)
                continue
        return measurements

    @staticmethod
    def parse_line(line):
        # return json.loads(line, {'precise_float': True})
        # for influxdb version > 0.9, timestamp is an integer
        return json.loads(line)

    # following methods are added to support customizing measurement name, tags much more flexible
    @staticmethod
    def compose_data(measurement, tags, value, time):
        data = "{0!s},{1!s} {2!s} {3!s}".format(measurement, tags, value, time)
        return data

    @staticmethod
    def format_measurement_name(entry, args):
        name = []
        for arg in args:
            if arg in entry:
                # avoid to add extra _ if some entry value is None
                if entry[arg] != '':
                    name.append(entry[arg])
        return '_'.join(name)

    @staticmethod
    def format_tags(entry, args):
        tag = []
        for arg in args:
            if arg in entry:
                # to avoid add None as tag value
                for k in entry[arg]:
                    tag.append("{0!s}={1!s}".format(k, entry[arg][k]))
        return ','.join(tag)

    @staticmethod
    def format_time(entry):
        d = datetime.datetime.strptime(entry['timestamp'][:-4], "%Y-%m-%dT%H:%M:%S.%f")
        return int(time.mktime(d.timetuple()))

    @staticmethod
    def format_value(entry):
        values = entry['data']
        value = "value={0!s}".format(values)
        return value
