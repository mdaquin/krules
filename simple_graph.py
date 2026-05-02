'''
A simple rule-based system for inferring new relations from existing ones.
Rules are defined in a text file with lines of the form:

# This is a comment
shortcut_name :: relation_name
# This is a rule
entity1 rel3 entity :- entity1 rel1 entity2, entity2 rel2 entity3

The constraints on rules are that:
- The premise must be a path of relations between entities.
- The conclusion must be a relation betwween the two entities at the beginning and end of the path of the premise.
- The premise's path cannot be longer than 6 relations (to keep things manageable).
'''
import json 
import numpy as np

class RuleParsingError(Exception): pass

class Rule():
    def __init__(self, premise, conclusion):
        self.premise = premise 
        while len(self.premise) < 6: self.premise.append(-1)
        self.conclusion = conclusion 
    def __str__(self):
        return str(self.conclusion)+" :- "+str(self.premise)

class KRuleBase:
    def __init__(self, rules_file):
        self.shortcuts = {}
        self.rules = []
        with open(rules_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'): # comments
                    if self.isShortcutDefinition(line): self.addShortcutDefinition(line)
                    else: self.addRule(line)
        print("Loaded", len(self.shortcuts), "shortcuts and", len(self.rules), "rules.")

    def isShortcutDefinition(self, line): return "::" in line
    
    def addShortcutDefinition(self, line):
        parts = line.split("::")
        if len(parts) != 2:
            print("Invalid shortcut definition:", line)
            raise RuleParsingError("Invalid shortcut definition")
        shortcut = parts[0].strip()
        expansion = parts[1].strip()
        self.shortcuts[shortcut] = expansion

    def addRule(self, line):
        if ":-" not in line: raise RuleParsingError("Invalid rule definition: "+line)
        parts = line.split(":-")
        premise_part = parts[1].strip()
        conclusion_part = parts[0].strip()
        premise_relations = []
        premise_entities = []
        for comp in premise_part.split(","):
            comp = comp.strip()
            comp = comp.split(" ")
            if len(comp) != 3: raise RuleParsingError("Invalid premise component "+comp+" in rule: "+line)
            premise_entities.append((comp[0], comp[2]))
            if len(premise_entities) != 1 and premise_entities[-1][0] != premise_entities[-2][1]:
                raise RuleParsingError("Entities in premise of rule do not form a path: "+line)
            if comp[1] in self.shortcuts: premise_relations.append(list(self.shortcuts.keys()).index(comp[1])) 
            elif comp[1] == "?": premise_relations.append(-1) # wildcard for any custom relation, which is "related"
            else: raise RuleParsingError("Unknown relation in premise of rule: "+comp[1]+" in line: "+line)
        conclusion_parts = conclusion_part.split(" ")
        index1 = -1
        index2 = -1
        for i in range(len(premise_entities)):
            if premise_entities[i][0] == conclusion_parts[0]: index1 = i
            if premise_entities[i][0] == conclusion_parts[2]: index2 = i
        if premise_entities[-1][1] == conclusion_parts[2]: index2 = len(premise_entities)
        if premise_entities[-1][1] == conclusion_parts[0]: index1 = len(premise_entities)
        if index1 == -1 or index2 == -1:
            print(premise_entities)
            print(conclusion_parts)
            raise RuleParsingError("Entities in conclusion not found in premise: "+line)
        conclusion_relation = conclusion_parts[1]
        if conclusion_relation in self.shortcuts: 
            conclusion_relation = list(self.shortcuts.keys()).index(conclusion_relation)
        else: raise RuleParsingError("Unknown relation in conclusion of rule: "+conclusion_relation+" in line: "+line)
        rule = Rule(premise_relations, (conclusion_relation, index1, index2))
        self.rules.append(rule)
    
    def process(self, relations):
        # relations is a dict of relation -> list of (ent1, ent2) pairs
        # where relation is an int in the index of keys of short cuts or "?" for any custom relation, 
        # and ent1 and ent2 are integers that are indices of entities in the index
        entpairs = np.empty((0,2), dtype=int)
        relpaths = np.empty((0,6), dtype=int)
        entpaths = np.empty((0,7), dtype=int)
        # create the base structure... 
        for irel in relations:
            for ents in relations[rel]:
                entpairs =  np.vstack([entpairs, [ents[0], ents[1]]])
                relpaths = np.vstack([relpaths, [irel, -1, -1, -1, -1, -1]]) 
                entpaths = np.vstack([entpaths, [ents[0], ents[1], -1, -1, -1, -1, -1]]) 
                entpairs, relpaths, entpaths = self.completeFromRel(len(entpairs)-1, entpairs, relpaths, entpaths)        
        i = 0
        while i < len(entpairs): # this might grow as we add new entpairs
            entpairs, relpaths, entpaths = self.applyRules(i, entpairs, relpaths, entpaths)
            i+=1 
        result = {}
        for i,relpath in enumerate(relpaths):
            if relpath[1] != -1: continue # only return direct relations
            rel = int(relpath[0])
            if rel not in result: result[rel] = []
            result[rel].append(entpairs[i].tolist())
        return result
    
    def applyRules(self, i, entpairs, relpaths, entpaths):
        relpath = relpaths[i]
        for rule in self.rules:  # might there be a more efficient way than checking all rules?
            if (relpath == rule.premise).all():
                ent1 = entpaths[i][rule.conclusion[1]]
                ent2 = entpaths[i][rule.conclusion[2]]
                newrel = rule.conclusion[0]
                # check if we already have this relation
                if not self.known(ent1, newrel, ent2, entpairs, relpaths):
                    entpairs = np.vstack([entpairs, [ent1, ent2]])
                    relpaths = np.vstack([relpaths, [int(newrel), -1, -1, -1, -1, -1]])
                    entpaths = np.vstack([entpaths, [ent1, ent2, -1, -1, -1, -1, -1]])
                    # print("Added", ent1, newrel, ent2)
                    entpairs, relpaths, entpaths = self.completeFromRel(len(entpairs)-1, entpairs, relpaths, entpaths) 
        return entpairs, relpaths, entpaths
    
    def known(self, ent1, rel, ent2, entpairs, relpaths): # TODO: make more efficient
        for i in range(len(entpairs)):
            if entpairs[i][0] == ent1 and entpairs[i][1] == ent2:
                if relpaths[i][0] == rel:
                    return True
        return False
    
    def findPathTo(self, relpath, ent, relpaths, entpairs):
        if len(relpath) == 0: return []
        # reduce relpath to values that are not -1
        # relpath = [r for r in relpath if r != -1] # only relevant for from
        # print("   Finding path to", ent, "using", relpath)
        eindex = np.where((entpairs[:,1] == ent) & (relpaths[:,0] == relpath[-1]) & (relpaths[:,1] == -1))[0]
        # print("      ind to ents:", eindex)
        nep, nrp = [], []
        if len(relpath) > 1:
           for ei in eindex: 
                nep, nrp = self.findPathTo(relpath[:-1], entpairs[ei][1], relpaths, entpairs)
        return nrp+[relpath[-1]], nep+[ent]
    
    def findPathFrom(self, relpath, ent, relpaths, entpairs):
        relpath = [r for r in relpath if r != -1]
        if len(relpath) == 0: return []        
        #print("   Finding path from", ent, "using", relpath)
        eindex = np.where((entpairs[:,0] == ent) & (relpaths[:,0] == relpath[0]) & (relpaths[:,1] == -1))[0]
        # print("      ind to ents:", eindex)
        nep, nrp = [], []
        if len(relpath) > 1:
           for ei in eindex: 
                nep, nrp = self.findPathFrom(relpath[1:], entpairs[ei][0], relpaths, entpairs)
        return [relpath[-1]]+nrp, [ent]+nep
    
    def completeFromRel(self, i, entpairs, relpaths, entpaths):
        ent1,rel,ent2 = entpairs[i][0], relpaths[i][0], entpairs[i][1]
        # print("   Completing from", ent1, rel, ent2)
        paths = []
        for rule in self.rules: 
            if rel in rule.premise: paths.append(rule.premise)
        for path in paths:
            if len(path) > 1: 
                irels = np.where(path == rel)[0]
                for irel in irels:
                    prevepaths = self.findPathTo(path[:irel], ent1, relpaths, entpairs) 
                    nextepaths = self.findPathFrom(path[irel+1:], ent2, relpaths, entpairs)
            # combine prevepaths and nextepaths with rel in the middle
            # add paths to entpaths, relpaths, entpairs
        return entpairs, relpaths, entpaths

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python krules.py <rule_file> <rdf_file>")
        sys.exit(1)
    rule_file = sys.argv[1]
    rdf_file = sys.argv[2]
    rb = KRuleBase(rule_file)
    # rels, enti = rdf_to_relations(rdf_file, rb.shortcuts)
    # irels = rb.process(rels)
    # print(irels)
