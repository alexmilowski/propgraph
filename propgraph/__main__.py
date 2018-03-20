
import json
import argparse
import sys
from propgraph import cypher_update, nquad_update

parser = argparse.ArgumentParser(description='Converts propgraph JSON into OpenCypher creation statements')
parser.add_argument('files',nargs='*')
parser.add_argument('-o','--output',help='Output file')
parser.add_argument('-b','--base',help='A default base URI')
parser.add_argument('-v','--vocab',help='A default vocabulary URI')
parser.add_argument('-t','--typemap',help='Type to property map')
parser.add_argument('-s','--subjects',help='A subject id mapping')
parser.add_argument('--use-blank',help='Type to property map',action='store_true',default=False)
parser.add_argument('--duplicates',help='Allow duplicate properties',action='store_true',default=False)
parser.add_argument('-f','--format',choices=['cypher','nquad','dgraph'],default='cypher')
parser.add_argument('--type-predicate',help='Type predicate for typing nodes/edges',default='rdf:type')

args = parser.parse_args()

def dgraph_update(graph,output,**kwargs):
   output.write('{\nset {\n')
   nquad_update(graph,output,**kwargs)
   output.write('}\n}\n')

format_update = {
   'cypher' : cypher_update,
   'nquad' : nquad_update,
   'dgraph' : dgraph_update
}

update = format_update.get(args.format)

out = sys.stdout

if args.output is not None:
   out = open(args.output,'w')

options = {}

if args.typemap is not None:
   with open(args.typemap,'r') as f:
      options['typemap'] = json.load(f)

if args.base is not None:
   options['base'] = args.base

if args.vocab is not None:
   options['vocab'] = args.vocab

if args.type_predicate is not None:
   options['type_predicate'] = args.type_predicate

if args.subjects is not None:
   with open(args.subjects,'r') as f:
      options['subjects'] = json.load(f)

options['use_blank'] = args.use_blank
options['duplicates'] = args.duplicates

for filename in args.files:
   if filename=='-':
      rawjson = sys.stdin
   else:
      rawjson = open(filename,'r')

   graph = json.load(rawjson)

   if filename!='-':
      rawjson.close()

   update(graph,out,**options)
