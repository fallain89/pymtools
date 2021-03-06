# coding=utf-8
"""
                                Reader module
"""
import os
import re
import sys
import csv
import logging


LOG = logging.getLogger(__name__)


class ReadableFile(object):
    """
    Readable file argparse action
    """

    def __init__(self, filepath, patterns=None):
        """
        File object related to one or more pattern (list of string)
        :param filepath:
        :param patterns:
        """
        self.patterns = patterns
        self.filepath = filepath
        self.filetype = os.path.splitext(filepath)[1][1:]
        self.filename = os.path.basename(os.path.splitext(filepath)[0])
        self.lines = {}

    def load(self):
        """
        Fill lines with dictionary. Each key is a line number in the given file
        :return: None
        """
        lines_dict = {}
        if not self.patterns and self.filetype == "csv":
            LOG.info("Reading with csv parser")
            with open(self.filepath) as csvfile:
                reader = csv.DictReader(
                    csvfile,
                    fieldnames=("protein", "spec", "iteration", "rest_no",
                                "contrib_no", "resid1", "resid2", "res1",
                                "res2", "atm1", "atm2", "pc_viol", "dc_ref",
                                "d_ref", "dc_avg", "dc_min", "dc_med", "d_avg",
                                "d_min", "d_med", "sdev", "lower", "upper",
                                "viol", "cutoff", "nbest", "rest_weight",
                                "valid", "contact_5", "contact_8", "group"))
                # Avoid first line
                next(reader)
                for index, line in enumerate(reader):
                    lines_dict[index] = line
            self.lines = lines_dict
        elif self.patterns:
            LOG.info("Reading %s with %s parser" % (self.filepath,
                                                    self.filetype))
            LOG.debug("Patterns: %s" % self.patterns)
            with open(self.filepath) as f:
                for index, line in enumerate(f):
                    for pattern in self.patterns:
                        match = pattern.match(line)
                        if match:
                            lines_dict[index] = match.groupdict()
                            break
            self.lines = lines_dict
            LOG.debug("Read %d lines" % len(self.lines))
        else:
            LOG.error("Can't read input file %s. Check if given format is "
                      "supported [%s]" % (self.filepath, self.filetype))
            sys.exit(1)


class CnstrFile(ReadableFile):
    """
    Constraint file class
    """
    TBLFORMAT = [
        re.compile(
            r"^(?P<assignflag>assign)\s+\(segid\s+\"\s*(?P<segid1>\w*)\s*\"\s+"
            r"and\s+resid\s+(?P<resid1>\d+)\s+and\s+name\s+(?P<atm1>\w+)\)\s+"
            r"\(segid\s+\"\s*(?P<segid2>\w*)\s*\"\s+and\s+resid\s+(?P<resid2>"
            r"\d+)\s+and\s+name\s+(?P<atm2>\w+)\)\s+(?P<target>\d+\.?\d*)\s+"
            r"(?P<lower>\d+\.?\d*)\s+(?P<upper>\d+\.?\d*)\s+weight\s+(?P<weight"
            r">\d+\.?\d*)\s+!\s+spec=(?P<spec>\w+),\s+no=(?P<no>\d+),\s+id=(?P<"
            r"id>\d+),\s+vol=(?P<vol>\d+\.?\d*e?-?\d*)\s*$"
        ),
        re.compile(
            r"^(?P<assignflag>assign)\s+\(resid\s+(?P<resid1>\d+)\s+and\s+name"
            r"\s+(?P<atm1>\w+)"
            r"\)\s+\(resid\s+(?P<resid2>\d+)\s+and\s+name"
            r"\s+(?P<atm2>\w+)\)\s+(?P<target>\d+\.?\d*)\s+(?P<lower>\d+\.?\d*)"
            r"\s+(?P<upper>\d+\.?\d*)\s+weight\s+(?P<weight>\d+\.?\d*)\s*$"
        ),
        re.compile(
            r"^\s*(?P<ambiflag>or)\s+\(segid\s+\"\s*(?P<segid1>\w*)\s*\"\s+and"
            r"\s+resid\s+(?P<resid1>\d+)\s+and\s+name\s+(?P<atm1>\w+)\)\s+\(seg"
            r"id\s+\"\s*(?P<segid2>\w*)\s*\"\s+and\s+resid\s+(?P<resid2>\d+)\s+"
            r"and\s+name\s+(?P<atm2>\w+)\)\s*$"
        ),
        re.compile(
            r"^\s*(?P<ambigflag>or)\s+\(resid\s+(?P<resid1>\d+)\s+and\s+name"
            r"\s+(?P<atm1>\w+)\)\s+\(resid\s+(?P<resid2>\d+)\s+and\s+name"
            r"\s+(?P<atm2>\w+)\)\s*$"
        )
    ]
    TXTFORMAT = [
        re.compile(
          r"^(?P<resid1>\d+)\s+(?P<resid2>\d+)\s+(?P<spec>\w+)\s*$"
        ),
    ]

    def __init__(self, filepath):
        if os.path.splitext(filepath)[1][1:] == "tbl":
            super(CnstrFile, self).__init__(filepath, self.TBLFORMAT)
        elif os.path.splitext(filepath)[1][1:] == "txt":
            super(CnstrFile, self).__init__(filepath, self.TXTFORMAT)
        else:
            super(CnstrFile, self).__init__(filepath)
