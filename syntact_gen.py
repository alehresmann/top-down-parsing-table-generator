'''A script for generating the first set, follow set, and parsing table for a
grammar.'''

import copy
# import sys
# from tabulate import tabulate
# from pandas import *


def get_rules_and_empty_nonterm_set(gram):
    """Returns rules, and a dictionary containing empty sets for each
    nonterminal variable."""
    rules = dict()
    ents = dict()  # empty nonterm set

    # get the rules
    for rule in gram:
        rule = rule.split()
        if rules.get(rule[0]) is None:
            rules[rule[0]] = []
            ents[rule[0]] = set()
        rules[rule[0]].append(rule[2:])
        for var in rule:
            if var.islower():
                rules[var] = [[var]]
                ents[var] = set()
    return rules, ents


def get_first(var, first, rules):
    """Returns the first set of a particular variable"""
    for rule in rules[var]:
        add_epsilon = True
        for rhvar in rule:
            # if var is a semantic action, skip it by pretending it can be
            # nullified
            if "action" in rhvar:
                continue
            if rhvar.islower():  # VAR -> a B for some terminal a
                first[var].add(rhvar)
                add_epsilon = False
                break
            elif rhvar == "EPSILON":  # VAR -> epsilon
                first[var].add(rhvar)
                break
            elif rhvar == var:  # VAR -> VAR B for nonterminal VAR
                break
            else:  # VAR -> A B for some nonterminal A
                rhfirst = get_first(rhvar, first, rules)
                for right_var in rhfirst:
                    if right_var != "EPSILON":
                        # First(A) contains epsilon
                        first[var].add(right_var)
                if "EPSILON" not in rhfirst:
                    # First(A) doesn't contain epsilon
                    add_epsilon = False
                    break
        if add_epsilon:
            first[var].add("EPSILON")

    return first[var]


def get_first_set(gram):
    """Returns the first set of a grammar"""

    rules, first = get_rules_and_empty_nonterm_set(gram)

    previous_first = None
    while previous_first != first:
        previous_first = copy.deepcopy(first)
        for var in rules:
            get_first(var, first, rules)
    return first


def get_first_set_json(first):
    """Returns the first set of a grammar as a json string"""
    first = sorted([(key, sorted(value)) for key, value in first.items()])
    json_first = "{\n"

    for key, value in first:
        json_first += "\"" + key + "\":["
        for word in value:
            json_first += "\"" + word + "\","
        json_first = json_first[:-1]
        json_first += "],\n"

    json_first = json_first[:-1]
    json_first += "\n}"
    return json_first


def get_follow_set(gram, first_set):
    """returns the follow set of a grammar"""
    rules, follow = get_rules_and_empty_nonterm_set(gram)
    # delete all nonterminals from the dictionary, as they have no follow set
    for var in list(follow.keys()):
        if var.islower() or "action" in var or "node" in var:
            del follow[var]
    # add END to the follow set of the first symbol.
    follow["INIT"].add("END")

    # actual loop for finding follow set:
    previous_follow = None
    while previous_follow != follow:
        previous_follow = copy.deepcopy(follow)
        for var in rules:
            for rhs in rules[var]:
                for right_var in rules:
                    if "action" in right_var:
                        continue

                    if right_var in rhs and not right_var.islower():
                        index = rhs.index(right_var)
                        while "action" in rhs[index]:
                            index += 1

                        if index == (len(rhs) - 1):
                            follow[right_var].update(follow[var])
                        else:
                            while "action" in rhs[index + 1]:
                                index += 1
                                if index >= len(rhs) - 1:
                                    break
                            if index >= (len(rhs) - 1):
                                follow[right_var].update(follow[var])

                            else:
                                follow[right_var].update(first_set[rhs[index +
                                                                       1]] -
                                                         {"EPSILON"})
                                if "EPSILON" in first_set[rhs[index + 1]]:
                                    follow[right_var].update(follow[var])

    return follow


def get_table(rules, first, follow):
    """get table for given grammar"""
    table = dict()
    # initiate table
    for left in first:
        table[left] = dict()
    for var in table:
        for left in first:
            if left.islower():
                if var.islower():
                    if var == left:
                        table[var][left] = [var]
                    else:
                        table[var][left] = [""]
                else:
                    table[var][left] = [""]
        table[var]["END"] = [""]

    # actual algorithm
    for var in rules:
        for rule in rules[var]:
            nullable = True
            for sym in rule:
                if "action" in sym:
                    continue
                if sym == "EPSILON":
                    break
                if sym.islower():
                    table[var][sym] = rule
                    nullable = False
                    break
                else:
                    for fi in first[sym]:
                        if fi != "EPSILON":
                            table[var][fi] = rule
                    if "EPSILON" not in first[sym]:
                        nullable = False
                        break
            if nullable:
                for sym in follow[var]:
                    table[var][sym] = rule

    # add epsilon rules:
    for var in table:
        if "EPSILON" in first[var]:
            for sym in table[var]:
                if table[var][sym] == [""]:
                    table[var][sym] = ["EPSILON"]
    return table


def add_errors(table):
    """ add errors to empty cells in the table"""
    # this is rather poor as error handling, should probably be more
    # intelligent. all it does is: if the top of your stack is a terminal and
    # your next token is not that terminal, scan until you see that terminal.
    # if the top of your stack is a nonterminal and your next token isn't
    # expected, pop that nonterminal.
    for left in table:
        for right in table[left]:
            if left.islower():
                if table[left][right] == [""]:
                    table[left][right] = ["ERROR_SCAN"]
            else:
                if table[left][right] == [""]:
                    table[left][right] = ["ERROR_POP"]

    return table


def get_token_dict(rules):
    """ get dictionary of all terminal variables (aka tokens)"""
    # note: is a dict to keep in place placement of values and act as a set
    # although this is an abuse of the data structure.
    tokens = dict()
    for var in rules:
        for rule in rules[var]:
            for value in rule:
                if value.islower():
                    tokens[value] = ""
    tokens["END"] = ""
    return tokens


def get_json_token_row(rules):
    """ get dictionary of all terminals, in JSON format."""
    tokens = get_token_dict(rules)
    string = "["
    for token in tokens:
        string += "\"" + token + "\","
    string = string[:-1]
    string += "]"
    return string


def get_json(table, rules):
    """get table in JSON format"""
    json = "{\n \"token_row\":" + \
        get_json_token_row(rules) + ",\n \"matrix\" : {\n"
    for left in table:
        json += "\"" + left + "\" : ["
        for right in table[left]:
            json += "["
            for var in table[left][right]:
                json += "\"" + var + "\","
            json = json[:-1]
            json += "],"
        json = json[:-1]
        json += "],\n"
    json = json[:-2]
    json += "}}"
    return json


def main():
    """main func handling the user interface to all the above functions"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate a parsing table for a given grammar.')
    parser.add_argument('file_name',
                        metavar='grammar_file',
                        type=str,
                        nargs=1,
                        help='the file name for the provided grammar')
    parser.add_argument('-fi',
                        '--first_set',
                        action='store_true',
                        help='Get the first set of a given grammar.')

    parser.add_argument('-fo',
                        '--follow_set',
                        action='store_true',
                        help='Get the follow set of a given grammar.')

    parser.add_argument('-t',
                        '--table',
                        action='store_true',
                        help='Get the table of a given grammar.')
    parser.add_argument('-e',
                        '--errors',
                        action='store_true',
                        help='add SCAN and POP errors to the table.')
    parser.add_argument('-d',
                        '--default',
                        action='store_true',
                        help='print the requested output in default mode.')

    parser.add_argument('-p',
                        '--pretty',
                        action='store_true',
                        help='print the requested output in pretty mode.')

    parser.add_argument('-j',
                        '--json',
                        action='store_true',
                        help='print the requested output in json.')

    args = parser.parse_args()

    if (not args.first_set and not args.follow_set and not args.table):
        raise Exception(
            "You select at least the first set (-fi) option, the follow set"
            " (-fo) option ,or the parsing table (-t) option!")

    grammar = ""
    try:
        with open(args.file_name[0], "r") as file:
            # the last el will be an empty string
            grammar = file.read().split("\n")[:-1]
    except IOError:
        print("Unable to open or read given file.")
        exit(0)

    rules, _ = get_rules_and_empty_nonterm_set(grammar)
    first = get_first_set(grammar)
    follow = get_follow_set(grammar, first)
    table = get_table(rules, first, follow)
    tokens = list(get_token_dict(rules).keys())

    if args.errors:
        table = add_errors(table)

    has_tabulate = False
    try:
        from tabulate import tabulate
        has_tabulate = True
    except ImportError:
        pass

    if not has_tabulate and args.pretty:
        print("Pretty print requires the tabulate package. Install it with:"
              "pip install --user tabulate")
        args.tabulate = False

    if (not args.default and not args.pretty and not args.json):
        if has_tabulate:
            args.tabulate = True
        else:
            args.default = True

    if args.default:
        if args.first_set:
            for var in first:
                print(var + "\t", first[var])
            print("\n\n")
        if args.follow_set:
            for var in follow:
                print(var + "\t", follow[var])
            print("\n\n")
        if args.table:
            print("terminals:" + str(tokens))
            for left in table:
                print(left, end=":\t")
                for right in table[left]:
                    print(str(table[left][right]), end="\t")
                print("\n", end="")
            print("\n\n")

    if args.pretty:
        if args.first_set:
            # flip the code and name and sort
            data = sorted([(key, sorted(value))
                           for key, value in first.items()])
            print(tabulate(data))
        if args.follow_set:
            # flip the code and name and sort
            data = sorted([(key, sorted(value))
                           for key, value in follow.items()])
            print(data)
            print(tabulate(data))
        if args.table:
            data = list()
            tokens.insert(0, "_")
            data.append(tokens)
            matrix = [([k] + [(table[k][v2]) for v2 in v])
                      for k, v in table.items()]
            data.extend(matrix)
            print(tabulate(data))

    if args.json:
        if args.first_set:
            print(get_first_set_json(first))
            print("\n\n")
        if args.follow_set:
            print(get_first_set_json(follow))
            print("\n\n")
        if args.table:
            print(get_json(table, rules))
            print("\n\n")


if __name__ == "__main__":
    main()
