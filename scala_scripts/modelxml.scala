import java.io.File
import javax.xml.parsers.DocumentBuilderFactory
import javax.xml.transform.dom.DOMSource
import javax.xml.transform.stream.StreamResult
import javax.xml.transform.TransformerFactory
import net.darkmist.alib.console.GetPass


/**
 * Created with IntelliJ IDEA.
 * User-> VaibhavAgarwal
 * Date-> 22/10/13
 * Time-> 10->40 AM
 * To change this template use File | Settings | File Templates.
 */
object modelxml {
  val scaling="1"
  val power="1"
  val state_suffix ="_eff"
  val objAlgoMap=Map("bfgs"->"algo.objective.BfgsObjective","ga"->"algo.objective.GAObjective","sa"->"algo.objective.SAObjective","hybrid"->"algo.objective.HybridObjective")
  val optAlgoMap=Map("bfgs"->"algo.bfgs.Bfgs_Optimizer","ga"->"algo.ga.GA_Optimizer","sa"->"algo.sa.SA_Optimizer","hybrid"->"algo.hybrid.Hybrid_Optimizer")
  val filterAlgoMap=Map("ukf"->"algo.parallel.advance.AdvanceUKFActorExecution","pf"->"algo.parallel.advance.NewPFActorExecution","bukf"->"algo.parallel.advance.BootstrapUKF","sukf"->"algo.parallel.advance.AdvanceUKFSmoother","ckf"->"algo.parallel.ckf.CKFActorExecution","squkf"->"algo.parallel.square.AdvanceSquareUKFActorExecution")

  def execDef(args:Any*){
    val modelId = args(0)
    val startTime = args(1)
    val endTime = args(2)
    val initFile = args(3)
    val outputfile = args(4)
    val optimization = args(5)
    val filteralgo = args(6)
    val optimizeralgo = args(7)

    var docFactory = DocumentBuilderFactory.newInstance()
    var docBuilder = docFactory.newDocumentBuilder()

    var doc = docBuilder.newDocument()
    //root element
    var root = doc.createElement("executionDef")
    doc.appendChild(root)

    //executionConfig
    var excConfig = doc.createElement("executionConfig")

    //modelId
    var mid = doc.createElement("modelId")
    var mid_val = doc.createTextNode(s"$modelId")
    mid.appendChild(mid_val)
    excConfig.appendChild(mid)

    //start timestamp
    var stp = doc.createElement("startTimeStep")
    var stp_val = doc.createTextNode(s"$startTime")
    stp.appendChild(stp_val)
    excConfig.appendChild(stp)

    //end timestamp
    var etp = doc.createElement("endTimeStep")
    var etp_val = doc.createTextNode(s"$endTime")
    etp.appendChild(etp_val)
    excConfig.appendChild(etp)

    //init file
    var inf = doc.createElement("initFile")
    var inf_val = doc.createTextNode(s"$initFile")
    inf.appendChild(inf_val)
    excConfig.appendChild(inf)

    //optimizer
    var opt = doc.createElement("optimizer")
    //objective function
    var objfun = doc.createElement("objectiveFunc")
    var objfun_val = doc.createTextNode((objAlgoMap.get(optimizeralgo.asInstanceOf[String])).toString)

    objfun.appendChild(objfun_val)
    opt.appendChild(objfun)
    //optimizer function
    var optfun = doc.createElement("optimizerFunc")
    var optfun_val = doc.createTextNode((optAlgoMap.get(optimizeralgo.asInstanceOf[String])).toString)
    optfun.appendChild(optfun_val)
    opt.appendChild(optfun)

    excConfig.appendChild(opt)

    //filter
    var filt = doc.createElement("filter")
    var filt_val = doc.createTextNode((filterAlgoMap.get(filteralgo.asInstanceOf[String])).toString)
    filt.appendChild(filt_val)
    excConfig.appendChild(filt)

    root.appendChild(excConfig)

    // write the content into xml file
    var transformerFactory = TransformerFactory.newInstance();
    var transformer = transformerFactory.newTransformer();
    var source = new DOMSource(doc);
    var result = new StreamResult(new File(outputfile.asInstanceOf[String]));
    //var result = new StreamResult(new File("E:\\file.xml"));

    // Output to console for testing
    // StreamResult result = new StreamResult(System.out);

    transformer.transform(source, result);

  }

  def ModelInitXml(state_list:List[Any],obv_list:List[Any],init_state_list:List[Any],init_variance_list:List[Any],procNoise_list:List[Any],obvNoise_list:List[Any],optimize_list:List[Any],params_list:List[Any],filename:String,optimization:Any){
    var docFactory = DocumentBuilderFactory.newInstance()
    var docBuilder = docFactory.newDocumentBuilder()

    var doc = docBuilder.newDocument()

    //root element
    var root = doc.createElement("initilization")
    doc.appendChild(root)

    //stateVars
    var stateVars = doc.createElement("stateVars")

    for (i<-0 until (state_list).length){
      var name = doc.createElement("name")
      name.setAttribute("optimize",(optimize_list(i)).toString)
      var name_val = doc.createTextNode(((state_list(i)).toString)+state_suffix)
      name.appendChild(name_val)

      var value = doc.createElement("value")
      var value_val = doc.createTextNode((init_state_list(i)).toString)
      value.appendChild(value_val)

      stateVars.appendChild(name)
      stateVars.appendChild(value)
    }

    root.appendChild(stateVars)
    //initVariance
    var initVariance = doc.createElement("initVariance")

    for (i <- 0 until (state_list).length){
      var name = doc.createElement("name")
      var name_val = doc.createTextNode(((state_list(i)).toString)+state_suffix)
      name.appendChild(name_val)

      var value = doc.createElement("value")
      var value_val = doc.createTextNode((init_variance_list(i)).toString)
      value.appendChild(value_val)

      initVariance.appendChild(name)
      initVariance.appendChild(value)
    }

    root.appendChild(initVariance)

    //process Noise
    var procNoise = doc.createElement("procNoise")
    for (i <- 0 until (state_list).length){
      var name = doc.createElement("name")
      name.setAttribute("optimize",(optimize_list(i)).toString)

      var name_val = doc.createTextNode((state_list(i)).toString+state_suffix)
      name.appendChild(name_val)

      var value = doc.createElement("value")
      var value_val = doc.createTextNode((procNoise_list(i)).toString)
      value.appendChild(value_val)

      procNoise.appendChild(name)
      procNoise.appendChild(value)

    }

    root.appendChild(procNoise)

    //observation Noise
    var obsNoise = doc.createElement("obsNoise")
    for (i <- 0 until (obv_list).length){
      var name = doc.createElement("name")
      //name.setAttribute("optimize","%s"%(str(optimize_list[i])))
      name.setAttribute("optimize",optimization.asInstanceOf[String])

      var name_val = doc.createTextNode((obv_list(i)).toString)
      name.appendChild(name_val)

      var value = doc.createElement("value")
      var value_val = doc.createTextNode((obvNoise_list(i)).toString)
      value.appendChild(value_val)

      obsNoise.appendChild(name)
      obsNoise.appendChild(value)
    }

    root.appendChild(obsNoise)

    //optimizerInitArgs
    var optimizerInitArgs = doc.createElement("optimizerInitArgs")

    //population size
    var name = doc.createElement("name")
    var name_val = doc.createTextNode("pop_size")
    name.appendChild(name_val)

    var value = doc.createElement("value")
    var value_val = doc.createTextNode("10")
    value.appendChild(value_val)

    optimizerInitArgs.appendChild(name)
    optimizerInitArgs.appendChild(value)


    //generations
    name = doc.createElement("name")
    name_val = doc.createTextNode("generations")
    name.appendChild(name_val)

    value = doc.createElement("value")
    value_val = doc.createTextNode("20")
    value.appendChild(value_val)

    optimizerInitArgs.appendChild(name)
    optimizerInitArgs.appendChild(value)


    //start Temperature
    name = doc.createElement("name")
    name_val = doc.createTextNode("start_temp")
    name.appendChild(name_val)

    value = doc.createElement("value")
    value_val = doc.createTextNode("100000")
    value.appendChild(value_val)

    optimizerInitArgs.appendChild(name)
    optimizerInitArgs.appendChild(value)


    //end temperature
    name = doc.createElement("name")
    name_val = doc.createTextNode("end_temp")
    name.appendChild(name_val)

    value = doc.createElement("value")
    value_val = doc.createTextNode("0.00001")
    value.appendChild(value_val)

    optimizerInitArgs.appendChild(name)
    optimizerInitArgs.appendChild(value)

    //iterations
    name = doc.createElement("name")
    name_val = doc.createTextNode("iterations")
    name.appendChild(name_val)

    value = doc.createElement("value")
    value_val = doc.createTextNode("10")
    value.appendChild(value_val)

    optimizerInitArgs.appendChild(name)
    optimizerInitArgs.appendChild(value)

    //particles
    name = doc.createElement("name")
    name_val = doc.createTextNode("particles")
    name.appendChild(name_val)

    value = doc.createElement("value")
    value_val = doc.createTextNode("250")
    value.appendChild(value_val)

    optimizerInitArgs.appendChild(name)
    optimizerInitArgs.appendChild(value)

    //samples
    name = doc.createElement("name")
    name_val = doc.createTextNode("samples")
    name.appendChild(name_val)

    value = doc.createElement("value")
    value_val = doc.createTextNode("500")
    value.appendChild(value_val)

    optimizerInitArgs.appendChild(name)
    optimizerInitArgs.appendChild(value)

    root.appendChild(optimizerInitArgs)


    //initial weight
    var initWeight = doc.createElement("initWeight")
    var initWeight_val = doc.createTextNode("-0.5")
    initWeight.appendChild(initWeight_val)
    root.appendChild(initWeight)

    //alpha
    var alpha = doc.createElement("alpha")
    var alpha_val = doc.createTextNode("1")
    alpha.appendChild(alpha_val)
    root.appendChild(alpha)

    //beta
    var beta = doc.createElement("beta")
    var beta_val = doc.createTextNode("2")
    beta.appendChild(beta_val)
    root.appendChild(beta)

    //kappa
    var kappa = doc.createElement("kappa")
    var kappa_val = doc.createTextNode("0.1")
    kappa.appendChild(kappa_val)
    root.appendChild(kappa)

    //augmentation
    var aug = doc.createElement("augmentation")
    var aug_val = doc.createTextNode("false")
    aug.appendChild(aug_val)
    root.appendChild(aug)

    // write the content into xml file
    var transformerFactory = TransformerFactory.newInstance();
    var transformer = transformerFactory.newTransformer();
    var source = new DOMSource(doc);
    var result = new StreamResult(new File(filename.asInstanceOf[String]));
    //var result = new StreamResult(new File("E:\\file.xml"));

    // Output to console for testing
    // StreamResult result = new StreamResult(System.out);

    transformer.transform(source, result);
    }

  def ModelXml(modelId:Any,state_list:List[Any],obv_list:List[Any],controls_list:List[Any],parameters_list:List[Any],filename:String,intercept:Any,scalingMap:Map[Any,Any]=Map(),transistionMap:Map[Any,Any]=Map(),observationMap:Map[Any,Any]=Map()){
    var docFactory = DocumentBuilderFactory.newInstance()
    var docBuilder = docFactory.newDocumentBuilder()

    var doc = docBuilder.newDocument()
    //root element
    var root = doc.createElement("Model")
    doc.appendChild(root)

    //modelId
    var mId = doc.createElement("modelId")
    root.appendChild(mId)

    var mIdVal = doc.createTextNode(modelId.toString)
    mId.appendChild(mIdVal)

    //states
    var states = doc.createElement("states")

    for (item <- state_list){
      var variable = doc.createElement("variable")
      var variable_val = doc.createTextNode((item.toString+state_suffix))
      variable.appendChild(variable_val)
      states.appendChild(variable)
    }
    root.appendChild(states)

    //observation
    var observations = doc.createElement("observations")

    for (item <- obv_list){
      var variable = doc.createElement("variable")

      variable.setAttribute("fieldAlias",(item.toString+"_alias"))

    if (scalingMap.contains(item)){
      var scalEq = scalingMap.get(item).asInstanceOf[List[Any]]
      if ((scalEq(0)) == "Log"){
        variable.setAttribute("scalingEq",("("+(scalEq(0)).toString+"[1+"+item.toString+"])^"+(scalEq(1)).toString))
      }
      else if (scalEq(0) == "exp"){
        variable.setAttribute("scalingEq","(1/(1+E^-"+item.toString+"))^"+(scalEq(1)).toString)
      }
      else{
        variable.setAttribute("scalingEq","("+item.toString+"*"+(scalEq(0)).toString+")^"+(scalEq(1)).toString)
        //descaling part
        //do to What would happen when string not in 10^-x format.
        var zz = scalEq(0).asInstanceOf[String].split("^")
        var zz1 = (zz(0))+ "^"+ (((-1)*(((zz(1)).toInt))).toString)
        var xx = (1/((scalEq(1)).asInstanceOf[Float])).toString
        variable.setAttribute("deScalingEq",("(("+item.toString+")^"+xx.toString+")*"+zz1.toString))
      }
    }
    else{
    variable.setAttribute("scalingEq",("("+item.toString+"*"+scaling.toString+")"))
    variable.setAttribute("deScalingEq",("("+item.toString+"*"+scaling.toString+")"))
    }

      var variable_val = doc.createTextNode(item.toString)
      variable.appendChild(variable_val)
      observations.appendChild(variable)
    }
    root.appendChild(observations)

    //controls
    var  controlVar= doc.createElement("controlVar")

    for (item <- controls_list){
      var variable = doc.createElement("variable")

      var variable_val = doc.createTextNode(item.toString)
      variable.appendChild(variable_val)

      controlVar.appendChild(variable)
    }
    root.appendChild(controlVar)

    //modelVars
    var modelVar = doc.createElement("modelVar")

    for (item <- state_list){
      var variable = doc.createElement("variable")

      if (scalingMap.contains(item)){
        var scalEq = scalingMap.get(item).asInstanceOf[List[Any]]
        if (scalEq(0) == "Log"){
          variable.setAttribute("scalingEq",("("+(scalEq(0)).toString+"[1+"+item.toString+"])^"+(scalEq(1)).toString))
        }
        else if (scalEq(0) == "exp"){
          variable.setAttribute("scalingEq","(1/(1+E^-"+item.toString+"))^"+(scalEq(1)).toString)
        }
        else{
          variable.setAttribute("scalingEq",("("+item.toString+"*"+(scalEq(0)).toString+")^"+(scalEq(1)).toString))
          //descaling part
          //do to What would happen when string not in 10^-x format.
          var zz = scalEq(0).asInstanceOf[String].split("^")
          var zz1 = (zz(0)).toString + "^" + (((zz(1)).toInt)*(-1)).toString
          var xx = (1/((scalEq(1)).asInstanceOf[Float])).toString
          variable.setAttribute("deScalingEq",("(("+item.toString+")^"+xx.toString+")*"+zz1.toString ))
        }
      }
      else{
        variable.setAttribute("scalingEq",("("+item.toString+"*"+scaling+")^"+power))
        variable.setAttribute("deScalingEq",("("+item.toString+"*"+scaling+")^"+power))

        var variable_val = doc.createTextNode((item).toString)
        variable.appendChild(variable_val)
        modelVar.appendChild(variable)
      }
    }
    root.appendChild(modelVar)

    //parameters
    var parameters = doc.createElement("parameters")
    root.appendChild(parameters)

    //observation Function
    for (obv <- obv_list){
      var obv_func = doc.createElement("observationFunction")
      var obsVar = doc.createElement("obsVar")
      var obsVar_val = doc.createTextNode(obv.toString)
      obsVar.appendChild(obsVar_val)

      var obv_eq_l = List(intercept.toString)
      for (item <- state_list){
        obv_eq_l::=((item.toString+"*"+item.toString+state_suffix))
        obv_eq_l=obv_eq_l.reverse
      }
      var equation = doc.createElement("equation")

      if (observationMap.contains(obv)){
        var obv_eq_l = observationMap.get(obv)    //custom observation equation
        var equation_val = doc.createTextNode((obv_eq_l).toString)
        equation.appendChild(equation_val)
      }
      else{
        var equation_val = doc.createTextNode(((obv_eq_l).mkString("+")))
        equation.appendChild(equation_val)
      }
      //equation.appendChild(equation_val)

      obv_func.appendChild(obsVar)
      obv_func.appendChild(equation)

      root.appendChild(obv_func)
    }
    """obv_eq_l1 = []
      |    for item in state_list[:32]:
      |    obv_eq_l1.append("((%s*%s)^%s)*%s_awar%s"%(item,scaling,power,item,state_suffix))
      |    """

    //transistion Function
    for (item <- state_list){
      var transitionFunction = doc.createElement("transitionFunction")

      var stateVar = doc.createElement("stateVar")
      var stateVar_val = doc.createTextNode((item.toString+state_suffix))
      stateVar.appendChild(stateVar_val)

      var equation = doc.createElement("equation")
      //if item == "awarness":
      if (transistionMap.contains(item)){
        var teq = transistionMap.get(item)
        var equation_val = doc.createTextNode((teq).toString) //custom transistion equation
        equation.appendChild(equation_val)
      }
      else{
        var equation_val = doc.createTextNode((item.toString+state_suffix))   //random walk
        equation.appendChild(equation_val)
      }
      //equation.appendChild(equation_val)

      transitionFunction.appendChild(stateVar)
      transitionFunction.appendChild(equation)

      root.appendChild(transitionFunction)

    }
    //xml = doc.toxml()

    // write the content into xml file
    var transformerFactory = TransformerFactory.newInstance();
    var transformer = transformerFactory.newTransformer();
    var source = new DOMSource(doc);
    var result = new StreamResult(new File(filename.asInstanceOf[String]));
    //var result = new StreamResult(new File("E:\\file.xml"));

    // Output to console for testing
    // StreamResult result = new StreamResult(System.out);

    transformer.transform(source, result);
  }

  def main(arg: Array[String]){

    //execDef("1","2","3","4","E:\\file.xml","6","7","8")
    //ModelInitXml(List(1,2),List(1,2),List(1,2),List(1,2),List(1,2),List(1,2),List(1,2),List(1,2),"E:\\file1.xml","Hell")
    GetPass.get()
  }

}
