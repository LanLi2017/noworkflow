# Copyright (c) 2014 Universidade Federal Fluminense (UFF), Polytechnic Institute of New York University.
# This file is part of noWorkflow. Please, consult the license terms in the LICENSE file.

from __future__ import absolute_import

from collections import defaultdict, OrderedDict
from ..persistence import row_to_dict, persistence

class History(object):

    def __init__(self):
        self.data = {}

    def scripts(self):
        return {s[0].rsplit('/',1)[-1] for s in persistence.distinct_scripts()}

    def graph_data(self, script="*", execution="*"):
        key = (script, execution)
        if key in self.data:
            return self.data[key]

        nodes, edges = [], []
        result = {'nodes': nodes, 'edges': edges}
        id_map, children = {}, defaultdict(list)
        scripts, order = defaultdict(list), OrderedDict()

        # Filter nodes and adds to dicts
        tid = 0
        for trial in persistence.load('trial', order="start"):
            if script != '*' and trial['script'] != script:
                continue
            if execution == 'finished' and not trial['finish']:
                continue
            if execution == 'unfinished' and trial['finish']:
                continue

            trial, trial_id = row_to_dict(trial), trial["id"]
            trial["level"] = 0
            trial["status"] = "Finished" if trial["finish"] else "Unfinished"
            if not trial['run']:
                trial["status"] = "Backup"
            trial["tooltip"] = "<b>{script}</b><br>{status}".format(**trial)
            
            id_map[trial_id] = tid
            scripts[trial['script']].append(trial)
            nodes.append(trial)
            tid += 1

        # Create edges
        for trial in reversed(nodes):
            trial_id, parent_id = trial["id"], trial["parent_id"]
            if parent_id and parent_id in id_map:
                edges.append({
                    'source': id_map[trial_id],
                    'target': id_map[parent_id],
                    'right': 1,
                    'level': 0
                })
                children[parent_id].append(trial_id)
            order[trial['script']] = 1

        # Set position
        level = 0
        for script in order:
            last = level
            for trial in scripts[script]:
                trial_id, parent_id = trial["id"], trial["parent_id"]
                if parent_id and parent_id in id_map:
                    parent = nodes[id_map[parent_id]]
                    if children[parent_id].index(trial_id) > 0:
                        trial["level"] = last
                        last += 1
                    else:
                        trial["level"] = parent["level"]
                    level = max(level, trial["level"] + 1)
                else:
                    trial["level"] = level
                    level += 1
                    last += 1

        self.data[key] = result
        return result