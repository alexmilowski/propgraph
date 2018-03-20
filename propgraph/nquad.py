
def nquad_literal(v):
   return '"' + str(v).replace('\\','\\\\').replace('"','\\"') + '"'

def blank_id(prefix='n'):
    n = 0
    while True:
       n += 1
       yield '_:' + prefix + str(n)



def triple(output,subject,predicate,value,value_type=None):
   if subject[0:2]=='_:':
      output.write(subject)
   else:
      output.write('<')
      output.write(subject)
      output.write('>')
   output.write(' <')
   output.write(predicate)
   output.write('> ')
   if value_type=='xs:anyURI':
      if value[0:2]=='_:':
         output.write(value)
      else:
         output.write('<')
         output.write(str(value))
         output.write('>')
   elif value_type=='blank':
      output.write(str(value))
   else:
      output.write(nquad_literal(value))
      if value_type is None and type(value)==int:
         value_type = 'xs:int'
      elif value_type is None and type(value)==float:
         value_type = 'xs:double'
      if value_type is not None:
         output.write('^^')
         output.write('<')
         output.write(value_type)
         output.write('>')
   output.write(' .\n')

def node_subject(subjects,ids,node,typemap,base,use_blank):

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

   key_value = node.get(key)

   key_exists = key_value in subjects if key_value is not None else False
   subject = subjects.get(key_value) if key_value is not None else None
   xid = None
   if subject is None and key_value is not None:
      subject = base + str(key_value)
      if use_blank:
         xid = subject
         subject = next(ids)
   elif subject is not None and key_value is not None:
      xid = base + str(key_value)

   if subject is None:
      subject = next(ids)
   elif not key_exists:
      subjects[key_value] = subject

   return (subject,xid,key_exists)

def type_subject(output,subjects,ids,subject,subject_type,use_blank=False,type_predicate='rdf:type',**kwargs):
   type_type = 'xs:anyURI'
   if use_blank:
      type_xid = subject_type
      subject_type = subjects.get(type_xid)
      if subject_type is None:
         subject_type = next(ids)
         type_type = 'blank'
         subjects[type_xid] = subject_type
         triple(output,subject_type,'xid',type_xid)
      elif subject_type[0:2]=='_:':
         type_type='blank'
   triple(output,subject,type_predicate,subject_type,value_type=type_type)


def nquad_update(graph,output,typemap={},base='',subjects={},vocab='',use_blank=False,duplicates=False,type_predicate='rdf:type',**kwargs):

   ids = blank_id();

   for position,scope in enumerate(graph if type(graph)==list else [graph]):
      for label in scope:
         if label=='@edges':
            continue
         node = scope[label]

         subject, xid, exists = node_subject(subjects,ids,node,typemap,base,use_blank)

         if not duplicates and exists:
            continue

         if xid is not None:
            triple(output,subject,'xid',xid)

         types = node['@type']
         if type(types)!=list:
            types = [types]

         for ntype in types:
            type_subject(output,subjects,ids,subject,vocab + ntype,use_blank=use_blank,type_predicate=type_predicate)

         for pname in node:
            if pname=='@type':
               continue
            pspec = typemap.get(pname)
            ptype = None
            if pspec is not None:
               ptype = pspec.get('type')
            triple(output,subject,vocab + pname,node[pname],value_type=ptype)

      for edge in scope['@edges']:
         etypes = edge['@type']
         if type(etypes)!=list:
            etypes = [etypes]

         pnames = list(filter(lambda name: name!='@type' and name!='@source' and name!='@target',edge.keys()))
         if len(pnames)>0:
            raise ValueError('Edges with properties not supported')
         else:
            source = node_subject(subjects,ids,scope[edge['@source']],typemap,base,use_blank)
            target = node_subject(subjects,ids,scope[edge['@target']],typemap,base,use_blank)
            for etype in etypes:
               triple(output,source[0],vocab + etype,target[0],value_type='blank')
