# Copyright 2017 by Kozo Nishida.  All rights reserved.
# This code is part of the Biopython distribution and governed by its
# license.  Please see the LICENSE file that should have been included
# as part of this package.

"""Code to work with the KEGG Gene database.

Functions:
parse - Returns an iterator giving Record objects.

Classes:
Record - A representation of a KEGG Gene.
"""

# other Biopython stuff
from __future__ import print_function

from Bio.KEGG import _write_kegg
from Bio.KEGG import _wrap_kegg

# Set up line wrapping rules (see Bio.KEGG._wrap_kegg)
name_wrap = [0, "",
             (" ", "$", 1, 1),
             ("-", "$", 1, 1)]
id_wrap = lambda indent: [indent, "", (" ", "", 1, 0)]


class Record(object):
    """Holds info from a KEGG Gene record.

    Members:
    entry       The entry identifier.
    name        A list of the gene names.
    definition  The definition for the gene.
    orthology   A list of 2-tuples: (orthology id, role)
    organism    A tuple: (organism id, organism)
    position    The position for the gene
    motif       A list of 2-tuples: (database, list of link ids)
    dblinks     A list of 2-tuples: (database, list of link ids)

    """

    def __init__(self):
        """__init__(self)

        Create a new Record.
        """
        self.entry = ""
        self.name = []
        self.definition = ""
        self.orthology = []
        self.organism = ""
        self.position = ""
        self.motif = []
        self.dblinks = []

    def __str__(self):
        """__str__(self)

        Returns a string representation of this Record.
        """
        return self._entry() + \
               self._name() + \
               self._dblinks() + \
               "///"

    def _entry(self):
        return _write_kegg("ENTRY",
                           [self.entry])

    def _name(self):
        return _write_kegg("NAME",
                           [_wrap_kegg(l, wrap_rule=name_wrap)
                            for l in self.name])

    def _definition(self):
        return _write_kegg("DEFINITION",
                           [self.definition])

    def _dblinks(self):
        s = []
        for entry in self.dblinks:
            s.append(entry[0] + ": " + " ".join(entry[1]))
        return _write_kegg("DBLINKS",
                           [_wrap_kegg(l, wrap_rule=id_wrap(9))
                            for l in s])


def parse(handle):
    """Parse a KEGG Gene file, returning Record objects.

    This is an iterator function, typically used in a for loop.  For
    example, using one of the example KEGG files in the Biopython
    test suite,

    >>> with open("KEGG/gene.sample") as handle:
    ...     for record in parse(handle):
    ...         print("%s %s" % (record.entry, record.name[0]))
    ...
    b1174 minE
    b1175 minD


    """
    record = Record()
    for line in handle:
        if line[:3] == "///":
            yield record
            record = Record()
            continue
        if line[:12] != "            ":
            keyword = line[:12]
        data = line[12:].strip()
        if keyword == "ENTRY       ":
            words = data.split()
            record.entry = words[0]
        elif keyword == "NAME        ":
            data = data.strip(";")
            record.name.append(data)
        elif keyword == "DEFINITION  ":
            record.definition = data
        elif keyword == "ORTHOLOGY   ":
            id, name = data.split("  ")
            orthology = (id, name)
            record.orthology.append(orthology)
        elif keyword == "ORGANISM    ":
            id, name = data.split("  ")
            organism = (id, name)
            record.organism = organism
        elif keyword == "POSITION    ":
            record.position = data
        elif keyword == "MOTIF       ":
            key, values = data.split(": ")
            values = values.split()
            row = (key, values)
            record.motif.append(row)
        elif keyword == "DBLINKS     ":
            if ":" in data:
                key, values = data.split(": ")
                values = values.split()
                row = (key, values)
                record.dblinks.append(row)
            else:
                row = record.dblinks[-1]
                key, values = row
                values.extend(data.split())
                row = key, values
                record.dblinks[-1] = row


if __name__ == "__main__":
    from Bio._utils import run_doctest
    run_doctest()
