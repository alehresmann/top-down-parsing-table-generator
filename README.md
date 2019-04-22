# Parser Table Generator
The following script take in the syntactic definition of a programming language (i.e. as a grammar) and generates the resulting parsing table for a top-down parser. If you are only interested in the first or follow sets, you can directly pull those too. For more information on what a parser is, see [the wikipedia page on it](https://en.wikipedia.org/wiki/Parsing).
## Input
An example input is provided in test.txt. For a larger example, see grammar.txt. Note that the input format is *not* validated, so if you wrongly give an input you may get some errors.
**The expected format is as follows:**
* one rule per line
* nonterminal variables are in upper case
* terminal variables are in lower case
* epsilon, the empty character, is written as EPSILON
* if a rule contains epsilon, that is the only thing it contains.

  e.g SOMEVAR -> EPSILON is allowed, but SOMEVAR -> somevar SOMEVAR EPSILON is not.
* the rules are of the form:  NONTERM -> somevar SOMEVAR somevar


  eg:                         CLASSDECL\_EBNF -> CLASSDECL CLASSDECL\_EBNF semicolon
* the symbol INIT is the starting symbol
* Semantic actions (symbols that are not vital to the parsing of the program but still need to be part of the rules if you wish to generate an abstract syntax tree) contain the word "action" (they are the only ones to do so), and have their first letter capitalised.

## Interface:
### Output
| Option Name   | Option               |
|:--------------|:---------------------|
| first set:    | `-fi \| --first_set` |
| follow set:   | `-fo \| --follow_set`|
| parsing table:| `-t \| --table`      |
|parsing table with scan and pop errors: | `-te \| --table_errors` |

## Output Formats:
| Option Name | Option |  Notes  |
|:------------|:-------|:--------|
| default:    | `-d \| --default `| |
| pretty:     |`-p \| --pretty`   | Requires the *tabulate* package. |
| json:       |`-j \| --json`       | |

The json option give you a json file with containing an object composed of two objects: a *TOKEN_ROW* listing all terminal symbols in a particular order, aka the header row of your table, and a *MATRIX* containing an object for each terminal and nonterminal. For each terminal and nonterminal, it will contain a list of lists, the outer list the length of the *TOKEN_ROW*, and each inner list containing some variables (aka the rule it matches to).

By default, the pretty printout is used, except when you don't have *tabulate* installed, in which case the default option is used.

## Examples
| Code | Description |
|:---- |:------------|
| `python syntact_gen.py my_grammar.txt -fo -d` | prints the follow set of my\_grammar.txt in default format. |
|`python syntact_gen.py my_grammar.txt -fi -p` | prints the first set of my\_grammar.txt with tabulate. |
| `python syntact_gen.py my_grammar.txt -t -j > table.json` | prints the table of my\_grammar.txt in json format, and writes it to a file called table.json. |
