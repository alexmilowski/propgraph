
def cypher_literal(v):
   if type(v)==str:
      return '"' + v.replace('\\','\\\\').replace('"','\\"') + '"'
   else:
      return str(v)

def cypher_update(graph,output,typemap={},**kwargs):
   for position,scope in enumerate(graph if type(graph)==list else [graph]):
      for label in scope:
         if label=='@edges':
            continue
         node = scope[label]
         types = node['@type']
         if type(types)!=list:
            types = [types]
         key = None
         for ntype in types:
            tspec = typemap.get(ntype)
            if tspec is not None:
               key = tspec.get('key')
            if key is not None:
               break
         if key is None:
            key = 'id'
         ntype_label = ''.join(map(lambda x : ':'+x,types))

         if key not in node:
            raise ValueError('key {key} not found in node: {node}'.format(key=key,node=str(node)))

         if position>0:
            output.write('\n')
         output.write('MERGE (`n{label}`{ntype} {{ `{key}`: {value}}})'.format(label=label,ntype=ntype_label,key=key,value=cypher_literal(node[key])))
         pcount = 0
         for pname in node:
            if pname==key or pname=='@type':
               continue
            if pcount==0:
               output.write('\nSET ')
            else:
               output.write(', ');
            output.write('`n{label}`.`{pname}` = {pvalue}'.format(label=label,pname=pname,pvalue=cypher_literal(node[pname])))
            pcount += 1
      for edge in scope['@edges']:
         etypes = edge['@type']
         if type(etypes)!=list:
            etypes = [etypes]
         etype_label = ''.join(map(lambda x : ':'+x,etypes if type(etypes)==list else [etypes]))
         output.write('\n')
         output.write('CREATE (`n{source}`)-[{label} {{'.format(source=edge['@source'],label=etype_label))
         pcount = 0
         for pname in edge:
            if pname=='@source' or pname=='@target' or pname=='@type':
               continue
            if pcount>0:
               output.write(', ')
            output.write('`{pname}` = {pvalue}'.format(pname=pname,pvalue=cypher_literal(edge[pname])))
            pcount += 1
         output.write('}}]->(`n{target}`)'.format(target=edge['@target']))
      output.write(';')
