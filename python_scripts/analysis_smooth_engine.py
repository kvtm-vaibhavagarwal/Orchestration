#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python

import zmqclient
import itertools
import csv
from math import *
from modelxml import *
from subprocess import Popen
import getpass
import new 
import collections
import smoothing
from datetime import datetime

username       = getpass.getuser()
host           = 'localhost'
port           = '10000'
algostr        = 'rf_execute'
fileptr        = 'DMB_infFB_sales_spend_lagspend_data.csv'
yobv           = 'sales'
model_loc      = '/Users/%s/production/resources'%username
movement       =  1
crosscsv       = '/tmp/dmb_allnew_fblagspend_civ_data_factors.csv'
combineout     = '/tmp/dmb_allnew_fblagspend_iv_civ_factors.csv'
output         = '/tmp/dmb_allnew_fblagspend_iv_factors.csv'

converted_cols_path =  '/tmp/converted_col.csv'

result_dir     = '/Users/%s/production/output'%username

include_iv     = True
varmap         = collections.OrderedDict()
rev_varmap     = collections.OrderedDict()


#peristing csv column names in abbreviated form.
def __persistColumns(filepath,fileout):
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
                if col == 'sales' or col == 'timestamp':
                   onl.append('%s' %(col))
                else:   
                   onl.append('%s_%d' %('ch',ch_counter))
                   varmap['%s_%d' %('ch',ch_counter)] = col
                   rev_varmap[col] = '%s_%d' %('ch',ch_counter)
                   ch_counter += 1
             fo.write('%s\n' %(','.join(onl)))  
         else:
             outlist = []
             for i in range(0,len(row)):
                colname = onl[i]
                if colname == 'timestamp':
                   xx = row[i]
                   try:
                      xx = datetime.strptime(row[i],'%d/%m/%y')
                   except:
                      xx = datetime.strptime(row[i],'%d/%m/%Y')

                   outdate = xx.strftime("%d/%m/%Y")
                   outlist.append(outdate)
                else:
                   outlist.append(str(row[i]))
             fo.write('%s\n' %(','.join(outlist)))  
          
         counter += 1  

      fo.close()
      f.close()
   except:
      import traceback
      traceback.print_exc()

   return counter


def findVI(inpfile,outfile):
   vilist = []
   try:
      start,end = 1,50,
      f = open(outfile,'w')
      f.write('%s,%s\n' %('variable','frequency'))

      #fetching the variable importance score from the server
      print 'Fetching Variable Importance Score %s %s ' %(inpfile,outfile)
      ch_dict = {}
      while end < 200:
         response = zmqclient.fetch_vi(host,port,algostr,'%s'%(inpfile),yobv,start,end)
         for k,v in response.items():
            if k in ch_dict:
               ch_dict[k] = ch_dict[k]+1
            else:
               ch_dict[k] = 1

            f.write('%s,%s\n' %(varmap.get(k),'1'))
   
         f.write('%s,%s\n' %('',''))

         start = start + movement
         end = end + movement

      total_sum = 0

      for k,v in ch_dict.items():
         f.write('%s,%s\n' %(varmap.get(k),str(v)))
         total_sum += v
      
      try:
         avg = total_sum/len(ch_dict)
         #vilist = [k for k,v in ch_dict.items() if v >= avg]
         vilist = [k for k,v in ch_dict.items()]
      except:
         import traceback
         traceback.print_exc()

      f.close()  

   except:
      import traceback
      traceback.print_exc()

   return vilist   


def calculateCrossChannelInfluence(inf_varlist = []):
   combinationlist = list(itertools.combinations(inf_varlist,2))
   createUpdatedCSV(crosscsv,inf_varlist,combinationlist,['Sales_lag','SPFB_Index'])
   vilist = findVI(crosscsv,combineout)
   __persistInfluencers(crosscsv,'/tmp/inf_data01.csv',vilist)


def __persistInfluencers(filepath,fileout,vilist):

   try:
      f = open(filepath,'r')
      fo = open(fileout,'w')
      reader = csv.reader(f)
      counter = 0
      collist = []
      for row in reader:
         if counter == 0:
             onl = []
             for col in row:
                if col == 'timestamp' or col == 'sales':
                   onl.append('%s' %(col))
                else:
                   if col in vilist:
                      onl.append('%s' %(varmap.get(col)))
                collist.append(col)
             fo.write('%s\n' %(','.join(onl)))  
         else:
             outlist = []
             for i in range(0,len(row)):
                colname = collist[i]
                if colname == 'sales' or colname =='timestamp':
                   outlist.append(str(row[i]))
                else:   
                   if colname in vilist:
                      if float(row[i]) > 0:
                         outlist.append('1')
                      else:   
                         outlist.append('0')

             fo.write('%s\n' %(','.join(outlist)))  
          
         counter += 1  

      fo.close()
      f.close()
   except:
      import traceback
      traceback.print_exc()

def createUpdatedCSV(updatecsv,inf_varlist=[],comblist=[],ignorelist = []):
   #f = open('%s/%s'%(model_loc,fileptr),'r')
   f = open('%s'%(converted_cols_path),'r')
   reader = csv.reader(f,delimiter=',',quotechar='"')
   fo = open(updatecsv,'w')

   for i1,i2 in comblist:
      if varmap.get(i1) not in ignorelist and varmap.get(i2) not in ignorelist:
         varmap['%s_%s'%(i1,i2)] = '%s_%s' %(varmap.get(i1),varmap.get(i2))

   count = 0
   colnames = []
   for row in reader:
      colMap = {}
      if count == 0:
         for col in row:
            colnames.append(col)

         combinedlist = []   
         if include_iv:
            combinedlist.extend(inf_varlist)
         combinedlist.extend(['%s_%s' %(i,j) for i,j in comblist if varmap.get(i) not in ignorelist and varmap.get(j) not in ignorelist]) 

         #colstr = ','.join(inf_varlist)
         #combstr = ','.join(['%s_%s' %(i,j) for i,j in comblist])
         combstr = ','.join(combinedlist)

         fo.write('%s,%s,%s\n' %('timestamp',yobv,combstr))
      else:  
         outlist = []
         for i in range(0,len(row)):
            colname = colnames[i]

            if colname == yobv or colname == 'timestamp':
               outlist.append(str(row[i]))

            if colname in inf_varlist:
               colMap[colname] = float(row[i])
         for i1,i2 in comblist:
            if varmap.get(i1) not in ignorelist and varmap.get(i2) not in ignorelist:
               combval = log10(1+colMap.get(i1))*log10(1+colMap.get(i2))
               colMap['%s_%s' %(i1,i2)] = combval

         #do we need the individual iv for next iv calculations
         if include_iv:
            for iv in inf_varlist:
               outlist.append(str(colMap.get(iv))) 
         for i1,i2 in comblist:
             if varmap.get(i1) not in ignorelist and varmap.get(i2) not in ignorelist:
                outlist.append(str(colMap.get('%s_%s' %(i1,i2))))

         fo.write('%s\n'%(','.join(outlist)))   

      count += 1      

   fo.close()   
      
def latesteffectivenessValues(resultfile,smcounter,chefflist=[],trucresults=[],qqlist=[],rrlist=[]):      
   counter = 0
   varlist = ['%s_var'%i for i in chefflist]
   actualchlist = [i.split('_eff')[0] for i in chefflist]
   qlist = ['%s_QVal'%i for i in chefflist]
   effectivnessMap = collections.OrderedDict()
   varianceMap = collections.OrderedDict()
   totalList = []
   onl = []

   try:
      f = open(resultfile,'r')
      reader = csv.reader(f)
      for row in reader:
         rowlist = []
         countermap = {}
         actchmap = {}

         if counter == 0:
             namelist = []
             for col in row:
                onl.append(col)
                if smcounter == 0:
                   if col == 'timestamp' or col == 'sales':
                      namelist.append(col)
                   #ch's input data.
                   if col in actualchlist and col not in actchmap:
                      namelist.append(col)
                      actchmap[col] = 'occured'
                   # for ch_eff names.
                   if col in chefflist and col not in countermap:
                      namelist.append(col) 
                      countermap[col] = 'occured'
                   # for ch_var names.
                   if col in varlist:
                      namelist.append(col)
             if len(namelist) > 0:
                trucresults.append(namelist)
                countermap.clear()
                actchmap.clear()
             print onl
         else:
             truncated_list = [row[0],row[1]]
             ql = []
             rl = []
             for i in range(0,len(row)):
                #this is for smoothing input file.
                colname = onl[i]
                rowlist.append(str(row[i]))

                #channels actual values
                if colname in actualchlist and colname not in actchmap:
                   truncated_list.append(str(row[i]))
                   actchmap[colname] = 'occured'
                #channel effectiveness
                if colname in chefflist and colname not in countermap:
                   effectivnessMap[varmap.get(colname.replace('_eff',''))] = float(row[i])
                   countermap[colname] = 'occured'
                   truncated_list.append(str(row[i]))
                #channel effectiveness variances.
                if colname in varlist:
                   varianceMap[varmap.get(colname.replace('_eff_var',''))] = float(row[i])
                   truncated_list.append(str(row[i]))
                #qvalues
                if colname in qlist:
                   ql.append(str(row[i]))
                #rvalues
                if 'RVal' in colname:
                   rl.append(str(row[i]))
             trucresults.append(truncated_list)
             qqlist.append(ql)
             rrlist.append(rl)


             totalList.append(rowlist)      
                   
         counter += 1  

      f.close()
   except:
      import traceback
      traceback.print_exc()

   print 'rrlist ======== ', rrlist

   return effectivnessMap,varianceMap,onl,totalList


def fetchSMParams(smoutput_file):
   f = open(smoutput_file,'r')
   reader = csv.reader(f)
   counter = 0
   cols = []
   init_states = []
   init_vars = []

   for row in reader:
      if counter == 0:
         for i in range(len(row)):
           cols.append(row[i]) 
      elif counter == 1:
         for i in range(len(row)):
           col_name = cols[i]
           if '_eff_var' in col_name:
              init_vars.append(float(row[i]))
           elif '_eff' in col_name:
              init_states.append(float(row[i]))

      counter += 1
   f.close()

   return init_states,init_vars
   

def prepareSMResultFile(smfileout,trucresults=[]):
   fs = open(smfileout,'w')

   for i in range(len(trucresults)):
      item = trucresults[i]
      if i == 0:
         ll = [item[0],item[1]]
         for col in item[2:]:
            if '_eff_var' in col:
               ch_name = col.split('_eff_var')[0] 
               rname = varmap.get(ch_name)   
               rname = '%s_eff_var'%rname
            elif '_eff' in col:
               ch_name = col.split('_eff')[0] 
               rname = varmap.get(ch_name)
               rname = '%s_eff'%rname   
            else:
               ch_name = col.split('_eff_var')[0] 
               rname = varmap.get(col)
            ll.append(rname)   
         fs.write('%s\n'%(','.join(ll)))
      else:
         xx = datetime.strptime(item[0].split(' ')[0],'%d/%m/%Y')
         outdate = xx.strftime("%d/%m/%Y")
         item[0] = outdate
         fs.write('%s\n'%(','.join(item)))

   fs.close()


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


def executeFilter(configFile):
   fconf = open(configFile,'r')
   xconf = fconf.read()
   temp = new.module('temp')
   exec xconf in temp.__dict__

   modelId        = 'dmonte'
   model_loc      = '/Users/%s/production/resources'%username
   model_xml      = '%s/%s/%s.xml'%(model_loc,'Models',modelId)
   model_xml_init = '%s/%s/%sInit.xml'%(model_loc,'Models',modelId)
   model_exc_def  = '%s/%s_exc_def.xml' %(model_loc,modelId)

   datasize = __persistColumns(temp.ivfile,'%s/%s'%(model_loc,temp.outfile))

   temp.execute(varmap,rev_varmap)


   init_map = temp.init_map
   init_var_map = temp.init_var_map
   scalingEq_map = temp.scalingEq_map
   observationMap = temp.observationMap
   transistionMap = temp.transistionMap
   procNoiseMap = temp.procnoise_map
   required_optimization = temp.required_optimization 
   

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
   end = start + window
   optimization = temp.optimization
   intercept = temp.intercept
   #####################################################################################################

   ################################### Annealing config ################################################
   annealing_size = temp.annealing_size
   anneal_pnt = temp.anneal_pnt
   #####################################################################################################

   ######################################## Algos ######################################################
   filteralgo = temp.filteralgo
   optalgo = temp.optalgo
   #####################################################################################################

   finalResult = []
   colnames = None

   if end > datasize:
      end = datasize-2

   global_qlist = []
   global_rlist = []

   while anneal_pnt <= annealing_size:
      print 'Annealing for step %d' %anneal_pnt
      start = 0
      end = start + window
      truncatelist = [] 
      qqlist = []
      rrlist = []

      sm_counter = 0
     
      #After 2 annealings optimization will get stopped 
      if anneal_pnt > 40:
         optimization = False
         end = datasize - 2

      while end < datasize:

         print 'Crafting Model Xml for start = %d, end = %d' %(start,end)
         #model xml generation
         obv_l       = [yobv]
         chlist      = []
         init_states = []
         init_vars   = []
         proc_noises = []
         obv_noises  = [str(temp.obvnoise)]
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

            #------------------------------------------ Q, R values assignments ----------------------------
            #handling optimization q,r initial values.
            if optimization:
               if len(global_qlist) > 0 and len(global_rlist) > 0:
                  qalist = global_qlist[0]
                  ralist = global_rlist[0]

                  if len(qqlist) > 0:
                     q_noise_list = qqlist[start-1]
                     for nn in q_noise_list:
                        proc_noises.append(str(nn))

                  else:
                     for item in qalist[0]:
                        proc_noises.append(item)

                  if len(rrlist) > 0:
                     r_noise_list = rrlist[start-1]
                     for nn in range(len(r_noise_list)):
                        obv_noises[nn] = r_noise_list[nn]
                  else:
                     for rr in range(len(ralist[0])):
                        obv_noises[rr] = ralist[0][rr]

               else:
                  #first optimization
                  if len(qqlist) > 0:
                     q_noise_list = qqlist[start-1]
                     for nn in q_noise_list:
                        proc_noises.append(str(nn))
                  else:
                     if v in procNoiseMap:
                        print 'channel = %s found in procNoiseMap ' %v
                        proc_noises.append(procNoiseMap.get(v))
                     else:
                        print 'channel = %s not found in procNoiseMap hence taking default initial value' %v
                        proc_noises.append(str(temp.procnoise))

                  if len(rrlist) > 0:
                     r_noise_list = rrlist[start-1]
                     for nn in range(len(r_noise_list)):
                        obv_noises[nn] = r_noise_list[nn]
            else:
               if len(global_qlist) > 0 and len(global_rlist) > 0:
                  qalist = global_qlist[0]
                  ralist = global_rlist[0]

                  if start == 0:
                     q_noise_list = qalist[0]
                  else:
                     q_noise_list = qalist[start]

                  for nn in q_noise_list:
                     proc_noises.append(str(nn))

                  if start == 0:
                     r_noise_list = ralist[0]
                  else:
                     r_noise_list = ralist[start]

                  obv_noises = []
                  for nn in range(len(r_noise_list)):
                     obv_noises.append(r_noise_list[nn])

               else:
                  if v in procNoiseMap:
                     print 'channel = %s found in procNoiseMap ' %v
                     proc_noises.append(procNoiseMap.get(v))
                  else:
                     print 'channel = %s not found in procNoiseMap hence taking default initial value' %v
                     proc_noises.append(str(temp.procnoise))
                  '''
		  if len(rrlist) > 0:
		     r_noise_list = rrlist[start-1]
		     for nn in range(len(r_noise_list)):
		        obv_noises[nn] = r_noise_list[nn]
                  '''
            #------------------------------------------ Q, R values assignments ----------------------------

            #proc_noises.append(str(temp.procnoise))
            if v in required_optimization and optimization:
               opt_val = required_optimization.get(v)
               if opt_val:
                  opt_l.append('true')
               else:
                  opt_l.append('false')
            else:
               opt_l.append(('%s'%optimization).lower())


         #modelxml
         ModelXml(modelId,chlist,obv_l,[],[],model_xml,intercept,scalingEq_map,transistionMap,observationMap)
         #model init xml
         ModelInitXml(chlist,obv_l,init_states,init_vars,proc_noises,obv_noises,opt_l,[],model_xml_init,str(optimization).lower())
         #model exc def
         execDef(modelId,str(start),str(end),'%sInit.xml'%(modelId),model_exc_def,optimization,filteralgo,optalgo)

         #import sys
         #sys.exit(0)
         
         po = None
         try:
            po = Popen('/Users/%s/production/start.sh %s %s' %(username,'%s_exc_def.xml'%(modelId),temp.outfile),shell=True)
            po.wait()

            import os

            dirlist = [i for i in os.listdir('/Users/%s/production/output'%username)] 

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
            latesteffMap,varianceMap,colnames,totalResult = latesteffectivenessValues('%s/output/%s/%s'%(realpath,dirpath,filepath), sm_counter,chefflist,truncatelist,qqlist,rrlist)  

            finalResult.extend(totalResult)

            

            #updating initial values map with the latest run values
            for k,v in latesteffMap.items():
               init_map[k] = v

            for k,v in varianceMap.items():
               init_var_map[k] = v

            start = end
            end = start + window
            sm_counter += 1


            if start >= datasize-2:
               print 'Last window computer = %d' %start
               break  

            if end > datasize-2:
               end = datasize-2

         except KeyboardInterrupt:
            print 'Killing application %s' %(po.pid)
            po.kill()

     
      #--------------------------- smoothing ----------------------------
      print '******************************* smoothing start ****************************'
      try:
         smoutlist = temp.finalresult.split('.')
         #TODO: Need to truncate the final result file for smoothing.
         smoutfile = smoutlist[0]+'_smooth_%d.'%(anneal_pnt) + smoutlist[1]

         data_file = '/tmp/smresult_%d.csv'%anneal_pnt

         prepareSMResultFile(data_file,truncatelist)
         smoothing.executeFilter(configFile,data_file,smoutfile,qqlist,rrlist)

         #fetching smooth parameters.
         sm0_initStates,sm0_initVars = fetchSMParams(smoutfile)

         #updating initial values map with the latest run values
         for k in range(len(sm0_initVars)):
            init_map[k] = sm0_initStates[k]

         for k in range(len(sm0_initVars)):
            init_var_map[k] = sm0_initVars[k]
          
         print 'Cleaning output directory after smoothing ....'
         po = Popen('rm -rf output',shell=True)
         po.wait()
      except:
         import traceback
         traceback.print_exc()

      print '******************************* smoothing end ****************************'
      
      #clearning and inserting into global list
      global_qlist = []
      global_rlist = []      

      global_qlist.append(qqlist)
      global_rlist.append(rrlist)

      #---------------------------- end ---------------------------------
      anneal_pnt += 1

   writeResult(temp.finalresult,colnames,finalResult)  



# ----------------------------------------------------------------------------------------

###################################### Random Forest (Influential Variables) #############
#variable importance score
#__persistColumns('%s/%s' %(model_loc,fileptr),converted_cols_path)
#vilist = findVI('%s'%(converted_cols_path),output)

#for cross channel influence
#calculateCrossChannelInfluence(vilist)
##########################################################################################

if __name__=='__main__':
  import sys
  if len(sys.argv) < 2:
     print "Usage: ./analysis_engine.py input-config-file"
     exit(0)

  inputconfig = sys.argv[1]
  executeFilter(inputconfig)
