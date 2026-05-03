'''
A simple rule-based system for inferring new relations from existing ones.
Rules are defined in a text file with lines of the form:

# This is a comment
shortcut_name :: relation_name
# This is a rule
entity1 rel3 entity :- entity1 rel1 entity2, entity2 rel2 entity3

The constraints on rules are that the premise must be a path of relations between entities. The conclusion must 
be a relation betwween the two entities at the beginning and end of the path of the premise.
'''

class RuleParsingError(Exception): pass

class Rule():
    def __init__(self, premise, conclusion):
        """ 
        premise is a list of relation indices
        conclusion is a tuple of (relation index, index of entity 1 in premise, index of entity 2 in premise)
        """
        self.premise = premise 
        self.conclusion = conclusion 
        self.subpaths = self._premise_subpaths()
        self.strpremise = self._rels_to_str(premise)
        self.strsubpaths = [self._rels_to_str(subpath) for subpath in self.subpaths]
    def __str__(self):
        return str(self.conclusion)+" :- "+str(self.premise)
    def _premise_subpaths(self):
        subpaths = []
        rels = self.premise
        for i in range(1, len(rels)+1):
            for j in range(len(rels)-i+1):
                subrels = rels[j:j+i]
                if subrels not in subpaths: subpaths.append(subrels)
        return subpaths    
    def _rels_to_str(self, rels):
        relsstr = ""
        for r in rels: relsstr += "_"+str(r)
        return relsstr

class KRuleBase:
    def __init__(self, rules_file):
        self.shortcuts = {}
        self.rules = []
        self.usefulpaths = []
        self.rulepaths = {}
        with open(rules_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'): # comments
                    if self.isShortcutDefinition(line): self.addShortcutDefinition(line)
                    else: self.addRule(line)
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
            raise RuleParsingError("Entities in conclusion not found in premise: "+line)
        conclusion_relation = conclusion_parts[1]
        if conclusion_relation in self.shortcuts: 
            conclusion_relation = list(self.shortcuts.keys()).index(conclusion_relation)
        else: raise RuleParsingError("Unknown relation in conclusion of rule: "+conclusion_relation+" in line: "+line)
        rule = Rule(premise_relations, (conclusion_relation, index1, index2))
        self.rules.append(rule)
        for subpath in rule.strsubpaths:
            if subpath not in self.usefulpaths: self.usefulpaths.append(subpath)
        if rule.strpremise not in self.rulepaths: self.rulepaths[rule.strpremise] = []
        self.rulepaths[rule.strpremise].append(rule)

    def process(self, relations):
        pathindex = {}
        e1index = {}
        e2index = {}
        count = 0
        for rel in relations:
            for entpair in relations[rel]:
                self._add_to_relpaths(rel, entpair, pathindex, e1index, e2index)
                count += 1
                if count % 1000 == 0: print(".", end="", flush=True)
        if count >= 1000: print()
        result = {}
        for path in pathindex:
            rel = path[1:]
            if "_" in rel: continue # only return direct relations
            rel = int(rel)
            if rel not in result: result[rel] = []
            for entities in pathindex[path]:
                result[rel].append(entities)
        return result

    # path as a string : 
    #    - 1 index path -> (e1, e2)
    #    - 1 index e1 -> (path->e2)
    #    - 1 index e2 -> (path->e1)
    # TODO: deal with possible cycles... if needed
    def _add_to_relpaths(self, rel, entpair, pathindex, e1index, e2index):
        npaths = {"_"+str(rel): [entpair]} # initialise npaths with the new relation
        for usefulpath in self.usefulpaths: 
           # BUG: will fail if more than 10 rels ("_1" in "_10")
           if "_"+str(rel) in usefulpath: # TODO: store strrel 
               # get all indexes of "_"+str(rel) in usefulpath, and for each one, split the path and get the origins and destinations
               rel_indexes = [i for i in range(len(usefulpath)) if usefulpath.startswith("_"+str(rel), i)]
               for rel_index in rel_indexes:
                    prevpath = usefulpath[:rel_index]
                    nextpath = usefulpath[rel_index+len("_"+str(rel)):]
                    if prevpath is None or prevpath == "": origins = [entpair[0]]
                    elif entpair[0] not in e2index or prevpath not in e2index[entpair[0]]: continue
                    else: origins = e2index[entpair[0]][prevpath]
                    if nextpath is None or nextpath == "": destinations = [entpair[1]]
                    elif entpair[1] not in e1index or nextpath not in e1index[entpair[1]]: continue
                    else: destinations = e1index[entpair[1]][nextpath]
                    for origin in origins:
                        for destination in destinations:
                            if usefulpath not in npaths: npaths[usefulpath] = []
                            if (origin, destination) not in npaths[usefulpath]: npaths[usefulpath].append((origin, destination))  
        for path, entities in npaths.items():
            if path not in pathindex: pathindex[path] = []
            pathindex[path].extend(entities)
            for entity in entities:
                if entity[0] not in e1index: e1index[entity[0]] = {}
                if path not in e1index[entity[0]]: e1index[entity[0]][path] = []
                if entity[1] not in e1index[entity[0]][path]: e1index[entity[0]][path].append(entity[1])
                if entity[1] not in e2index: e2index[entity[1]] = {}
                if path not in e2index[entity[1]]: e2index[entity[1]][path] = []
                if entity[0] not in e2index[entity[1]][path]: e2index[entity[1]][path].append(entity[0])
        for path, entities in npaths.items():
            if path in self.rulepaths:
                for entpair in entities:
                    for rule in self.rulepaths[path]:
                        nentpair = (entpair[0], entpair[1]) if rule.conclusion[1] == 0 else (entpair[1], entpair[0])
                        if not self.known(rule.conclusion[0], nentpair, e1index): 
                            self._add_to_relpaths(rule.conclusion[0], nentpair, pathindex, e1index, e2index)

    def known(self, rel, entpair, e1index):
        return entpair[0] in e1index and "_"+str(rel) in e1index[entpair[0]] and entpair[1] in e1index[entpair[0]]["_"+str(rel)]

def rdf_to_relations(rdf_file, oshortcuts):
    import rdflib
    relations = {}
    ents = {}
    shortcuts = {v:k for k,v in oshortcuts.items()}
    ishortcuts = {sc:i for i,sc in enumerate(oshortcuts.keys())}
    g = rdflib.Graph()
    g.parse(rdf_file)
    for s, p, o in g:
        if isinstance(s, rdflib.term.URIRef) and isinstance(p, rdflib.term.URIRef) and isinstance(o, rdflib.term.URIRef):
            s,p,o = str(s), str(p), str(o)
            if p in shortcuts:
                irel = ishortcuts[shortcuts[p]]
                if irel not in relations: relations[irel] = []
                if s not in ents: ents[s] = len(ents)
                if o not in ents: ents[o] = len(ents)
                relations[irel].append((ents[s], ents[o]))
    g.close()
    return relations, ents

def relations_to_rdf(relations, ents, shortcuts, output_file):
    import rdflib
    g = rdflib.Graph()
    rev_ents = {v: k for k, v in ents.items()}
    for rel in relations:
        shortcut = list(shortcuts.keys())[rel]
        p = shortcuts[shortcut]
        for entpair in relations[rel]:
            s = rev_ents[entpair[0]]
            o = rev_ents[entpair[1]]
            g.add((rdflib.URIRef(s), rdflib.URIRef(p), rdflib.URIRef(o)))
    g.serialize(destination=output_file, format='nt', encoding='utf-8')

if __name__ == "__main__":
    import sys
    import time
    if len(sys.argv) != 4:
        print("Usage: python krules.py <rule_file> <rdf_file> <output_file>")
        sys.exit(1)
    rule_file = sys.argv[1]
    rdf_file = sys.argv[2]
    output_file = sys.argv[3]
    rb = KRuleBase(rule_file)
    print("Loaded", len(rb.shortcuts), "shortcuts and", len(rb.rules), "rules.")
    rels, enti = rdf_to_relations(rdf_file, rb.shortcuts)
    print("Loaded", len(rels), "relations and", len(enti), "entities from RDF file.")
    count = 0
    print(f"{sum(len(rels[rel]) for rel in rels)} triples included")
    time1 = time.time()
    irels = rb.process(rels)
    ttime = time.time() - time1
    print("Obtained", sum(len(irels[rel]) for rel in irels), "triples after inference in", ttime, "seconds.")
    relations_to_rdf(irels, enti, rb.shortcuts, output_file)
    print("Saved to", output_file)