from xml.dom.minidom import Document

scaling = '1'
power = '1'
state_suffix = '_eff'
objAlgoMap = {'bfgs':'algo.objective.BfgsObjective','ga':'algo.objective.GAObjective','sa':'algo.objective.SAObjective','hybrid':'algo.objective.HybridObjective'}
optAlgoMap = {'bfgs':'algo.bfgs.Bfgs_Optimizer','ga':'algo.ga.GA_Optimizer','sa':'algo.sa.SA_Optimizer','hybrid':'algo.hybrid.Hybrid_Optimizer'}
filterAlgoMap = {'ukf':'algo.parallel.advance.AdvanceUKFActorExecution','pf':'algo.parallel.advance.NewPFActorExecution','bukf':'algo.parallel.advance.BootstrapUKF','sukf':'algo.parallel.advance.AdvanceUKFSmoother','ckf':'algo.parallel.ckf.CKFActorExecution','squkf':'algo.parallel.square.AdvanceSquareUKFActorExecution'}

def execDef(*args):
   modelId = args[0]
   startTime = args[1]
   endTime = args[2]
   initFile = args[3]
   outputfile = args[4]
   optimization = args[5]
   filteralgo = args[6]
   optimizeralgo = args[7]

   doc = Document()

   #root element
   root = doc.createElement('executionDef')
   doc.appendChild(root)

   #executionConfig
   excConfig = doc.createElement('executionConfig')

   #modelId 
   mid = doc.createElement('modelId')
   mid_val = doc.createTextNode('%s' %(modelId))
   mid.appendChild(mid_val)
   excConfig.appendChild(mid)

   #start timestamp
   stp = doc.createElement('startTimeStep')
   stp_val = doc.createTextNode('%s' %(startTime))
   stp.appendChild(stp_val)
   excConfig.appendChild(stp)

   #end timestamp
   etp = doc.createElement('endTimeStep')
   etp_val = doc.createTextNode('%s' %(endTime))
   etp.appendChild(etp_val)
   excConfig.appendChild(etp)

   #init file
   inf = doc.createElement('initFile')
   inf_val = doc.createTextNode('%s' %(initFile))
   inf.appendChild(inf_val)
   excConfig.appendChild(inf)

   #optimizer
   opt = doc.createElement('optimizer')
   #objective function 
   objfun = doc.createElement('objectiveFunc')
   objfun_val = doc.createTextNode(objAlgoMap.get(optimizeralgo))

   objfun.appendChild(objfun_val)
   opt.appendChild(objfun)
   #optimizer function
   optfun = doc.createElement('optimizerFunc')
   optfun_val = doc.createTextNode(optAlgoMap.get(optimizeralgo))
   optfun.appendChild(optfun_val)
   opt.appendChild(optfun)

   excConfig.appendChild(opt)

   #filter
   filt = doc.createElement('filter')
   filt_val = doc.createTextNode('%s' %(filterAlgoMap.get(filteralgo)))
   filt.appendChild(filt_val)
   excConfig.appendChild(filt)

   root.appendChild(excConfig)

   doc.writexml(open(outputfile,'w'))


def ModelInitXml(state_list,obv_list,init_state_list,init_variance_list,
                 procNoise_list,obvNoise_list,optimize_list,params_list,filename,optimization):
   doc = Document()

   #root element
   root = doc.createElement('initilization')
   doc.appendChild(root)

   #stateVars
   stateVars = doc.createElement('stateVars')
   
   for i in range(0,len(state_list)):
       name = doc.createElement('name')
       name.setAttribute('optimize','%s'%(str(optimize_list[i])))       
       name_val = doc.createTextNode('%s%s' %(state_list[i],state_suffix))
       name.appendChild(name_val)
       
       value = doc.createElement('value')
       value_val = doc.createTextNode('%s'%(str(init_state_list[i])))
       value.appendChild(value_val)
 
       stateVars.appendChild(name)
       stateVars.appendChild(value)

   root.appendChild(stateVars)       
   
   #initVariance
   initVariance = doc.createElement('initVariance')

   for i in range(0,len(state_list)):
       name = doc.createElement('name')
       name_val = doc.createTextNode('%s%s' %(state_list[i],state_suffix))
       name.appendChild(name_val)

       value = doc.createElement('value')
       value_val = doc.createTextNode('%s'%(str(init_variance_list[i])))
       value.appendChild(value_val)

       initVariance.appendChild(name)
       initVariance.appendChild(value)

   root.appendChild(initVariance)

   #process Noise
   procNoise = doc.createElement('procNoise')
   for i in range(0,len(state_list)):
       name = doc.createElement('name')
       name.setAttribute('optimize','%s'%(str(optimize_list[i])))       

       name_val = doc.createTextNode('%s%s' %(state_list[i],state_suffix))
       name.appendChild(name_val)
   
       value = doc.createElement('value')
       value_val = doc.createTextNode('%s'%(str(procNoise_list[i])))
       value.appendChild(value_val)

       procNoise.appendChild(name)
       procNoise.appendChild(value)

   root.appendChild(procNoise)


   #observation Noise
   obsNoise = doc.createElement('obsNoise')
   for i in range(0,len(obv_list)):
       name = doc.createElement('name')
       #name.setAttribute('optimize','%s'%(str(optimize_list[i])))       
       name.setAttribute('optimize','%s'%(optimization))      

       name_val = doc.createTextNode('%s' %(obv_list[i]))
       name.appendChild(name_val)
   
       value = doc.createElement('value')
       value_val = doc.createTextNode('%s'%(str(obvNoise_list[i])))
       value.appendChild(value_val)

       obsNoise.appendChild(name)
       obsNoise.appendChild(value)

   root.appendChild(obsNoise)

   #optimizerInitArgs
   optimizerInitArgs = doc.createElement('optimizerInitArgs')

   #population size
   name = doc.createElement('name')
   name_val = doc.createTextNode('pop_size')
   name.appendChild(name_val)
   
   value = doc.createElement('value')
   value_val = doc.createTextNode('10')
   value.appendChild(value_val)

   optimizerInitArgs.appendChild(name) 
   optimizerInitArgs.appendChild(value) 
   
   
   #generations
   name = doc.createElement('name')
   name_val = doc.createTextNode('generations')
   name.appendChild(name_val)
   
   value = doc.createElement('value')
   value_val = doc.createTextNode('20')
   value.appendChild(value_val)

   optimizerInitArgs.appendChild(name) 
   optimizerInitArgs.appendChild(value) 


   #start Temperature
   name = doc.createElement('name')
   name_val = doc.createTextNode('start_temp')
   name.appendChild(name_val)
   
   value = doc.createElement('value')
   value_val = doc.createTextNode('100000')
   value.appendChild(value_val)

   optimizerInitArgs.appendChild(name) 
   optimizerInitArgs.appendChild(value) 


   #end temperature
   name = doc.createElement('name')
   name_val = doc.createTextNode('end_temp')
   name.appendChild(name_val)
   
   value = doc.createElement('value')
   value_val = doc.createTextNode('0.00001')
   value.appendChild(value_val)

   optimizerInitArgs.appendChild(name) 
   optimizerInitArgs.appendChild(value) 

   #iterations
   name = doc.createElement('name')
   name_val = doc.createTextNode('iterations')
   name.appendChild(name_val)
   
   value = doc.createElement('value')
   value_val = doc.createTextNode('10')
   value.appendChild(value_val)

   optimizerInitArgs.appendChild(name) 
   optimizerInitArgs.appendChild(value) 

   #particles
   name = doc.createElement('name')
   name_val = doc.createTextNode('particles')
   name.appendChild(name_val)
   
   value = doc.createElement('value')
   value_val = doc.createTextNode('250')
   value.appendChild(value_val)

   optimizerInitArgs.appendChild(name) 
   optimizerInitArgs.appendChild(value) 

   #samples
   name = doc.createElement('name')
   name_val = doc.createTextNode('samples')
   name.appendChild(name_val)
   
   value = doc.createElement('value')
   value_val = doc.createTextNode('500')
   value.appendChild(value_val)

   optimizerInitArgs.appendChild(name) 
   optimizerInitArgs.appendChild(value) 

   root.appendChild(optimizerInitArgs)


   #initial weight
   initWeight = doc.createElement('initWeight')
   initWeight_val = doc.createTextNode('-0.5')
   initWeight.appendChild(initWeight_val)
   root.appendChild(initWeight)

   #alpha
   alpha = doc.createElement('alpha')
   alpha_val = doc.createTextNode('1')
   alpha.appendChild(alpha_val)
   root.appendChild(alpha)

   #beta
   beta = doc.createElement('beta')
   beta_val = doc.createTextNode('2')
   beta.appendChild(beta_val)
   root.appendChild(beta)

   #kappa 
   kappa = doc.createElement('kappa')
   kappa_val = doc.createTextNode('0.1')
   kappa.appendChild(kappa_val)
   root.appendChild(kappa)
  
   #augmentation
   aug = doc.createElement('augmentation')
   aug_val = doc.createTextNode('false')
   aug.appendChild(aug_val)
   root.appendChild(aug)

   doc.writexml(open(filename,'w'))


def ModelXml(modelId,state_list,obv_list,controls_list,parameters_list,filename,intercept,scalingMap={},transistionMap={},observationMap={}):
   doc = Document()

   #root element
   root = doc.createElement('Model')
   doc.appendChild(root)

   #modelId
   mId = doc.createElement('modelId')
   root.appendChild(mId)

   mIdVal = doc.createTextNode('%s' %modelId)
   mId.appendChild(mIdVal)

   #states
   states = doc.createElement('states')
   
   for item in state_list:
      variable = doc.createElement('variable')
      variable_val = doc.createTextNode('%s%s' %(item,state_suffix)) 
      variable.appendChild(variable_val)
      states.appendChild(variable)

   root.appendChild(states)

   #observation
   observations = doc.createElement('observations')
   
   for item in obv_list:
      variable = doc.createElement('variable')

      variable.setAttribute('fieldAlias','%s_alias'%item)

      if item in scalingMap:
         scalEq = scalingMap.get(item)
         if scalEq[0] == 'Log':
            variable.setAttribute('scalingEq','(%s[1+%s])^%s' %(scalEq[0],item,scalEq[1]))
         elif scalEq[0] == 'exp':    
            variable.setAttribute('scalingEq','(1/(1+E^-%s))^%s' %(item,scalEq[1]))
         else:  
            variable.setAttribute('scalingEq','(%s*%s)^%s' %(item,scalEq[0],scalEq[1]))
            #descaling part 
            #TODO: What would happen when string not in 10^-x format.
            zz = scalEq[0].split('^')
            zz = zz[0] + '^' + str(int(zz[1])*-1)
            xx = str(1/float(scalEq[1]))
            variable.setAttribute('deScalingEq','((%s)^%s)*%s' %(item,xx,zz))
      else:
         variable.setAttribute('scalingEq','(%s*%s)' %(item,scaling))
         variable.setAttribute('deScalingEq','(%s*%s)' %(item,scaling))

      variable_val = doc.createTextNode('%s'%item)
      variable.appendChild(variable_val)
      observations.appendChild(variable)
  
   root.appendChild(observations)

   #controls
   controlVar = doc.createElement('controlVar')
   
   for item in controls_list:
      variable = doc.createElement('variable')
       
      variable_val = doc.createTextNode('%s'%item)
      variable.appendChild(variable_val)
    
      controlVar.appendChild(variable)

   root.appendChild(controlVar)

   

   #modelVars
   modelVar = doc.createElement('modelVar')

   for item in state_list:
      variable = doc.createElement('variable')
      
      if item in scalingMap:
         scalEq = scalingMap.get(item)
         if scalEq[0] == 'Log':
            variable.setAttribute('scalingEq','(%s[1+%s])^%s' %(scalEq[0],item,scalEq[1]))
         elif scalEq[0] == 'exp':    
            variable.setAttribute('scalingEq','(1/(1+E^-%s))^%s' %(item,scalEq[1]))
         else:  
            variable.setAttribute('scalingEq','(%s*%s)^%s' %(item,scalEq[0],scalEq[1]))
            #descaling part 
            #TODO: What would happen when string not in 10^-x format.
            zz = scalEq[0].split('^')
            zz = zz[0] + '^' + str(int(zz[1])*-1)
            xx = str(1/float(scalEq[1]))
            variable.setAttribute('deScalingEq','((%s)^%s)*%s' %(item,xx,zz))
      else:
         variable.setAttribute('scalingEq','(%s*%s)^%s' %(item,scaling,power))
         variable.setAttribute('deScalingEq','(%s*%s)^%s' %(item,scaling,power))

      variable_val = doc.createTextNode('%s' %(item)) 
      variable.appendChild(variable_val)
      modelVar.appendChild(variable)
   
   root.appendChild(modelVar)

   #parameters
   parameters = doc.createElement('parameters')
   root.appendChild(parameters)

   #observation Function
   for obv in obv_list:
      obv_func = doc.createElement('observationFunction')
      obsVar = doc.createElement('obsVar')
      obsVar_val = doc.createTextNode('%s' %(obv))
      obsVar.appendChild(obsVar_val)

      obv_eq_l = [str(intercept)]
      for item in state_list:
          obv_eq_l.append('%s*%s%s'%(item,item,state_suffix))       
   
      equation = doc.createElement('equation')

      if obv in observationMap:
         obv_eq_l = observationMap.get(obv)    #custom observation equation
         equation_val = doc.createTextNode('%s' %(obv_eq_l))
      else:   
         equation_val = doc.createTextNode('%s' %('+'.join(obv_eq_l)))

      equation.appendChild(equation_val)

      obv_func.appendChild(obsVar)
      obv_func.appendChild(equation)

      root.appendChild(obv_func)

   '''
   obv_eq_l1 = []
   for item in state_list[:32]:
       obv_eq_l1.append('((%s*%s)^%s)*%s_awar%s'%(item,scaling,power,item,state_suffix))
   '''    
   
   #transistion Function
   for item in state_list:
       transitionFunction = doc.createElement('transitionFunction')
       
       stateVar = doc.createElement('stateVar')
       stateVar_val = doc.createTextNode('%s%s' %(item,state_suffix))
       stateVar.appendChild(stateVar_val)

       equation = doc.createElement('equation')
       #if item == "awarness":
       if item in transistionMap:
          teq = transistionMap.get(item)
          equation_val = doc.createTextNode('%s' %(teq)) #custom transistion equation
       else:   
          equation_val = doc.createTextNode('%s%s' %(item,state_suffix))   #random walk
       equation.appendChild(equation_val)
       
       transitionFunction.appendChild(stateVar)
       transitionFunction.appendChild(equation)
 
       root.appendChild(transitionFunction)


   #xml = doc.toxml()
  
   doc.writexml(open(filename,'w'))
