#!/usr/bin/python

import zmqclient
import itertools
import csv
from math import *
from modelxml import *
from subprocess import Popen
import getpass
import new 
import collections

username       = getpass.getuser()
host           = 'localhost'
port           = '10000'
algostr        = 'rf_execute'
fileptr        = 'DMB_infFB_sales_spend_lagspend_data.csv'
yobv           = 'sales'
model_loc      = '/home/%s/production/resources'%username
movement       =  1
output         = '/tmp/dmb_allnew_fblagspend_iv_factors.csv'

converted_cols_path =  '/tmp/converted_col.csv'

result_dir     = '/home/%s/production/output'%username

include_iv     = True
varmap         = collections.OrderedDict()
rev_varmap     = collections.OrderedDict()


#peristing csv column names in abbreviated form.
def __persistColumns(filepath,fileout,obvslist=[]):
   #filepath = '%s/%s' %(model_loc,fileptr)
   #fileout  = converted_cols_path
   counter = 0

   try:
      f = open(filepath,'r')
      fo = open(fileout,'w')
      reader = csv.reader(f)
      for row in reader:
         if counter == 0:
             ch_counter = 1
             onl = []
             for col in row:
                if col == 'timestamp' or col in obvslist:
                   onl.append('%s' %(col))
                else:   
                   if '_eff' not in col and '_eff_var' not in col:
                      onl.append('%s_%d' %('ch',ch_counter))
                      varmap['%s_%d' %('ch',ch_counter)] = col
                      rev_varmap[col] = '%s_%d' %('ch',ch_counter)
                      ch_counter += 1
                   else:
                      xc = col.split('_eff')
                      chan = rev_varmap.get(xc[0])
                      onl.append('%s' %(''.join([chan,'_eff',xc[1]])))
                      
             fo.write('%s\n' %(','.join(onl)))  
         else:
             outlist = []
             for i in range(0,len(row)):
                outlist.append(str(row[i]))
             fo.write('%s\n' %(','.join(outlist)))  
          
         counter += 1  

      fo.close()
      f.close()
   except:
      import traceback
      traceback.print_exc()

   return counter


def latesteffectivenessValues(resultfile,chefflist=[]):      
   counter = 0
   varlist = ['%s_var'%i for i in chefflist]
   effectivnessMap = {}
   varianceMap = {}
   totalList = []
   onl = []

   try:
      f = open(resultfile,'r')
      reader = csv.reader(f)
      for row in reader:
         rowlist = []
         countermap = {}
         if counter == 0:
             for col in row:
                onl.append(col)
         else:
             for i in range(0,len(row)):
                colname = onl[i]
                rowlist.append(str(row[i]))
                if colname in chefflist and colname not in countermap:
                   effectivnessMap[varmap.get(colname.replace('_eff',''))] = float(row[i])
                   countermap[colname] = 'occured'
                if colname in varlist:
                   varianceMap[varmap.get(colname.replace('_eff_var',''))] = float(row[i])

             totalList.append(rowlist)      
                   
         counter += 1  

      f.close()
   except:
      import traceback
      traceback.print_exc()

   return effectivnessMap,varianceMap,onl,totalList


def writeResult(fileout,colnames,results=[]):
   f = open(fileout,'w')
   realcolnames = []

   for i in colnames:
      chn = i.split('_')
      if len(chn) > 1:
         if len(chn[2:]) > 0:
            rname = '%s_%s'%(varmap.get('%s_%s'%(chn[0],chn[1])),'_'.join(chn[2:]))
         else:
            rname = '%s'%(varmap.get('%s_%s'%(chn[0],chn[1])))
      else:
         rname = i
      realcolnames.append(rname)

   f.write('%s\n'%(','.join(realcolnames)))

   for item in results:
      f.write('%s\n'%','.join(item))

   f.close()   


def executeFilter(configFile,input_file=None,output_file=None,qqlist=[],rrlist=[]):

   print "&&&&&&&&&&&&&&&&&&&&&&&&&&&& Calling Smoothing....... &&&&&&&&&&&&&&&&&&&&&&&&&&&"
   fconf = open(configFile,'r')
   xconf = fconf.read()
   temp = new.module('temp')
   exec xconf in temp.__dict__

   modelId        = 'dmonte'
   model_loc      = '/home/%s/production/resources'%username
   model_xml      = '%s/%s/%s.xml'%(model_loc,'Models',modelId)
   model_xml_init = '%s/%s/%sInit.xml'%(model_loc,'Models',modelId)
   model_exc_def  = '%s/%s_exc_def.xml' %(model_loc,modelId)
   
   obvs_list = temp.observations_list

   if input_file:
      ivfile = input_file
   else:
      ivfile = temp.ivfile

   smout_ll = temp.outfile.split('.')
   smout_file = '%s_smooth.%s'%(smout_ll[0],smout_ll[1])

   datasize = __persistColumns(ivfile,'%s/%s'%(model_loc,smout_file),obvs_list)

   temp.execute(varmap,rev_varmap)


   init_map = temp.init_map
   init_var_map = temp.init_var_map
   scalingEq_map = temp.scalingEq_map
   observationMap = temp.observationMap
   transistionMap = temp.transistionMap
   required_optimization = temp.required_optimization 

   #clearing scaling equation map.
   scalingEq_map.clear()


   #replacing original variable name with the autogenerated name
   for k,v in varmap.items():
      if v in scalingEq_map:
         eqvl = scalingEq_map.get(v)
         scalingEq_map.pop(v)
         scalingEq_map[k] = eqvl

   #####################################################################################################      

   ######################### Sliding window & require optimizationconfigs ##############################
   window = temp.window
   start = temp.start
   #end = start + window
   end = 1000000
   #optimization = temp.optimization
   optimization = False
   intercept = temp.intercept
   #####################################################################################################

   ################################### Annealing config ################################################
   #annealing_size = temp.annealing_size
   annealing_size = 1
   anneal_pnt = temp.anneal_pnt
   #####################################################################################################

   ######################################## Algos ######################################################
   #filteralgo = temp.filteralgo
   filteralgo = 'sukf'
   optalgo = temp.optalgo
   #####################################################################################################

   finalResult = []
   colnames = []

   if end > datasize:
      end = datasize-2


   while anneal_pnt <= annealing_size:
      print 'Annealing for step %d' %anneal_pnt
      start = 0
      #end = start + window

      while end < datasize:

         print 'Crafting Model Xml for start = %d, end = %d' %(start,end)
         #model xml generation
         obv_l       = obvs_list
         chlist      = []
         init_states = []
         init_vars   = []
         proc_noises = []
         obv_noises  = [str(temp.obvnoise) for i in obv_l]
         opt_l       = []

         for k,v in varmap.items():
            chlist.append(k)
            if v in init_map:
               print 'channel = %s found in init map ' %v
               init_states.append(init_map.get(v)) 
            else:
               print 'channel = %s not found in init map hence taking default initial value' %v
               init_states.append(temp.istate_default) 

            if v in init_var_map:
               print 'channel = %s found in init var map ' %v
               init_vars.append(init_var_map.get(v)) 
            else:
               print 'channel = %s not found in init var map hence taking default initial value' %v
               init_vars.append(temp.ivar_default) 

            if len(qqlist) > 0:
               for noise in qqlist[-1]:
                  proc_noises.append(str(noise))
            else:
               proc_noises.append(str(temp.procnoise))
           
            if len(rrlist) > 0:
               for no in range(len(rrlist[-1])):
                  obv_noises[no] = rrlist[-1][no]

            '''
            if v in required_optimization:
               opt_val = required_optimization.get(v)
               if opt_val:
                  opt_l.append('true')
               else:
                  opt_l.append('false')
            else:
               opt_l.append(('%s'%optimization).lower()) 
            '''
            opt_l.append('false')

         #modelxml
         ModelXml(modelId,chlist,obv_l,[],[],model_xml,intercept,scalingEq_map,transistionMap,observationMap)
         #model init xml
         ModelInitXml(chlist,obv_l,init_states,init_vars,proc_noises,obv_noises,opt_l,[],model_xml_init,str(optimization).lower())
         #model exc def
         execDef(modelId,str(start),str(end),'%sInit.xml'%(modelId),model_exc_def,optimization,filteralgo,optalgo)
         po = None
         try:
            po = Popen('/home/%s/production/start.sh %s %s' %(username,'%s_exc_def.xml'%(modelId),smout_file),shell=True)
            po.wait()
   
            import os

            dirlist = [i for i in os.listdir('/home/%s/production/output'%username)] 

            realpath = os.path.realpath('')
            maxmodtime,dirpath = 0.0,None
            for i in dirlist:
               if os.path.getmtime('%s/%s/%s'%(realpath,'output',i)) > maxmodtime:
                   maxmodtime = os.path.getmtime('%s/%s/%s'%(realpath,'output',i))
                   dirpath = i

            filelist = [i for i in os.listdir('%s/%s/%s'%(realpath,'output',dirpath)) if os.path.isfile('%s/%s/%s/%s'%(realpath,'output',dirpath,i))]       
            minmodtime,filepath = 1000000000000,None
            for i in filelist:
               if os.path.getmtime('%s/%s/%s/%s'%(realpath,'output',dirpath,i)) < minmodtime:
                  minmodtime = os.path.getmtime('%s/%s/%s/%s'%(realpath,'output',dirpath,i))
                  filepath = i
                

            chefflist = ['%s_eff'%i for i in chlist]
            latesteffMap,varianceMap,colnames,totalResult = latesteffectivenessValues('%s/output/%s/%s'%(realpath,dirpath,filepath),chefflist)  

            finalResult.extend(totalResult)

            #updating initial values map with the latest run values
            for k,v in latesteffMap.items():
               init_map[k] = v

            for k,v in varianceMap.items():
               init_var_map[k] = v

            start = end
            end = start + window

            if start >= datasize-2:
               print 'Last window computer = %d' %start
               break  

            if end > datasize-2:
               end = datasize-2

         except KeyboardInterrupt:
            print 'Killing application %s' %(po.pid)
            po.kill()

      anneal_pnt += 1
   if output_file:
       finalresult = output_file
   else:
       finalresult = temp.finalresult
      
   writeResult(finalresult,colnames,finalResult)  

# ----------------------------------------------------------------------------------------
'''
if __name__=='__main__':
  import sys
  if len(sys.argv) < 2:
     print "Usage: ./smoothing.py input-config-file"
     exit(0)

  inputconfig = sys.argv[1]
  executeFilter(inputconfig)
'''
