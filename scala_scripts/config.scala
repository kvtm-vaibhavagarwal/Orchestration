/**
 * Created with IntelliJ IDEA.
 * User-> VaibhavAgarwal
 * Date-> 7/11/13
 * Time-> 11->43 AM
 * To change this template use File | Settings | File Templates.
 */
import net.darkmist.alib.console.GetPass
object config {
  val username = GetPass.get()

  val ivfile      = "/Users/"+username+"/production/resources/model1a_laggedInteraction_FBPC2_inputdata.csv"
  val outfile     = "inf_intecept_convert_q4_m1a.csv"
  val finalresult = "/tmp/finalresult_09_26_model1a_laggedinteraction_FBPC2_milkbone_cube.csv"
  val filteralgo  = "ckf"
  val optalgo     = "bfgs"

  //////////////////////////////////Maps////////////////////////////
  val observations_list = List("sales")
  val required_optimization = Map[Any,Any]()
  val procnoise_map = Map[Any,Any]()
  val init_map       = Map(
    "TV"->20,
    "Print"->1.14,
    "Incremental"->0.044,
    "sales_lag"->0.7,
    "Social_Media_total_Impression"->1.7,
    "Digital_Impressions"->0.5,
    "SEM_impressions"->1.4,
    "decay"->0.95,
    "carryover"->0.9,

    "intercept"->0.8,
    "awarness"->0.3,
    "Google_trends"->0.58
    //	"Non_FSI_CouponRedeemed "->-0.27,
    //	"IOpack_10LbBox_CouponRedeemed "->-0.03,
    //	"IOpack_TrailMix_CouponRedeemed "->1.25,
    //	"IOpack_HF_CouponRedeemed "->3.01,
  )

  val init_var_map  = (
    "TV"->100,
    "Print"->20,
    "sales_lag"->5,
    "Social_Media_total_Impression"->50,
    "Digital_Impressions"->50,
    "SEM_impressions"->50,
    "intercept"->20,

    "awarness"->20,
    "Google_trends"->20
    //	"Non_FSI_CouponRedeemed "->-0.27,
    //	"IOpack_10LbBox_CouponRedeemed "->-0.03,
    //	"IOpack_TrailMix_CouponRedeemed "->1.25,
    //	"IOpack_HF_CouponRedeemed "->3.01,
  )

  val scalingEq_map = Map(
    "sales"->List("10^-4",1),
    "sales_lag"->List("10^-4",1),
    "TV"->List("10^-4",0.3),
    "Print"->List("10^-4",0.3),
    
    "Digital_Impressions"->List("10^-4",0.3),
    
    "SEM_impressions"->List("10^-4",0.3),
    "Social_Media_total_Impression"->List("10^-4",0.3),
    
    "DFSI_Total_CouponRedeemed"->List("10^-3",1),
    "NDFSI_Total_CouponRedeemed"->List("10^-3",1),
    "InPack_Total_CouponPrinted"->List("10^-3",1),
    //			"FB_PC1"->List("10^-4",1),
    "FBPC2"->List("10^-4",1),
    //			"FB_PC3"->List("10^-4",1),
    //			"FB_PC4"->List("10^-4",1),
    "FBPC5_lag4"->List("10^-3",1)
  )

  var observationMap = scala.collection.mutable.Map[Any,Any]()
  var transistionMap = scala.collection.mutable.Map[Any,Any]()

  /////////////////////////////////////////////////////////////////////////////////////////

  //////////////////////////Sliding window & require optimizationconfigs///////////////////

  val window = 10
  val start = 0
  val optimization = true
  val intercept = 0

  /////////////////////////////////////////////////////////////////////////////////////////

  //////////////////////////Annealing config///////////////////////////////////////////////

  val annealing_size = 4
  val anneal_pnt = 1

  /////////////////////////////////////////////////////////////////////////////////////////

  //////////////////////////Noise Values//////////////////////////////////////////////////

  val obvnoise = 20
  val procnoise = 2
  val istate_default = 0.12
  val ivar_default = 100

  /////////////////////////////////////////////////////////////////////////////////////////

  def execute(varmap:Map[Any,Any]=Map[Any,Any](),rev_varmap:Map[Any,Any]=Map[Any,Any]()){

  ////////////////////////////////////// Observaton Equation //////////////////////////////////////////
  var obvlist = List[Any]()
  for ((k,v) <- varmap){
    obvlist::=(k+"*"+k+"_eff")
  }
  obvlist=obvlist.reverse

  observationMap("sales") =  (obvlist.mkString("+"))

  /////////////////////////////////////////////////////////////////////////////////////////////////////

  ////////////////////////////////////// Transistion Equations ////////////////////////////////////////

  val awarness_transistion_str = "0.95*"+(rev_varmap.get("awarness"))+"_eff"
  var eqlist = List(awarness_transistion_str)

  val iglist = List("timestamp","sales","awarness","SPFB_Index","SPFB_Index_Lag",
  "intercept","Google_trends","sales_lag","latent_sales")
  """
  for k,v in varmap.items():
  if v not in iglist and "_awar" not in v and "_b2" not in v:
    eqlist.append("%s*%s_eff" %(k,rev_varmap.get("%s_awar"%(v))))
  """

  eqlist::=(1+"*"+(rev_varmap.get("sales_lag"))+"_eff")


  transistionMap(rev_varmap.get("awarness")) = (eqlist.mkString("+"))
  /////////////////////////////////////////////////////////////////////////////////////////////////////
  }

  def main(arg: Array[String]){
    println("done")
  }
}

