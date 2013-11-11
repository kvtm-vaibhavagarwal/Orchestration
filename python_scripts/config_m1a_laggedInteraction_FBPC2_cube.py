import getpass
username       = getpass.getuser()


ivfile      = '/Users/%s/production/resources/model1a_laggedInteraction_FBPC2_inputdata.csv'%username
outfile     = 'inf_intecept_convert_q4_m1a.csv'
finalresult = '/tmp/finalresult_09_26_model1a_laggedinteraction_FBPC2_milkbone_cube.csv'
filteralgo  = 'ckf'
optalgo     = 'bfgs'

######################### Maps ######################################################################
observations_list = ['sales']
required_optimization = { }
procnoise_map = {}
init_map       = {  
                    'TV':20,
                    'Print':1.14,
                    'Incremental':0.044,
                    'sales_lag':0.7,
                    'Social_Media_total_Impression':1.7,
                    'Digital_Impressions':0.5,
                    'SEM_impressions':1.4,
                    'decay':0.95,
                    'carryover':0.9,
					'intercept':0.8,
					'awarness':0.3,
					'Google_trends':0.58,
				#	'Non_FSI_CouponRedeemed ':-0.27,
				#	'IOpack_10LbBox_CouponRedeemed ':-0.03,
				#	'IOpack_TrailMix_CouponRedeemed ':1.25,
				#	'IOpack_HF_CouponRedeemed ':3.01,
                 }

init_var_map  = {
                    'TV':100,
                    'Print':20,
                    'sales_lag':5,
                    'Social_Media_total_Impression':50,
                    'Digital_Impressions':50,
                    'SEM_impressions':50,
                    'intercept':20,
					'awarness':20,
					'Google_trends':20,
				#	'Non_FSI_CouponRedeemed ':-0.27,
				#	'IOpack_10LbBox_CouponRedeemed ':-0.03,
				#	'IOpack_TrailMix_CouponRedeemed ':1.25,
				#	'IOpack_HF_CouponRedeemed ':3.01,
				}


scalingEq_map = {
                  'sales':['10^-4',1],
                  'sales_lag':['10^-4',1],
                  'TV':['10^-4',0.3],
                  'Print':['10^-4',0.3],
				  'Digital_Impressions':['10^-4',0.3],
                  'SEM_impressions':['10^-4',0.3],
                  'Social_Media_total_Impression':['10^-4',0.3],
				  'DFSI_Total_CouponRedeemed':['10^-3',1],
				  'NDFSI_Total_CouponRedeemed':['10^-3',1],
				  'InPack_Total_CouponPrinted':['10^-3',1],
	#			'FB_PC1':['10^-4',1],
				'FBPC2':['10^-4',1],
	#			'FB_PC3':['10^-4',1],
	#			'FB_PC4':['10^-4',1],
				  'FBPC5_lag4':['10^-3',1],
              }

observationMap = {}
transistionMap = {}
#####################################################################################################

######################### Sliding window & require optimizationconfigs ##############################
window = 10
start = 0
optimization = True
intercept = 0
#####################################################################################################

################################### Annealing config ################################################
annealing_size = 4
anneal_pnt = 1 
#####################################################################################################

################################### Noise Values ################################################
obvnoise = 20
procnoise = 2
istate_default = 0.12
ivar_default = 100
#####################################################################################################

def execute(varmap={},rev_varmap={}):

   ###################################### Observaton Equation ##########################################
   obvlist = []
   for k,v in varmap.items():
      obvlist.append('%s*%s_eff' %(k,k))

   observationMap['sales'] =  '%s'%('+'.join(obvlist))  

   #####################################################################################################

   ###################################### Transistion Equations ########################################     

   awarness_transistion_str = '0.95*%s_eff'%(rev_varmap.get('awarness'))
   eqlist = [awarness_transistion_str]

   iglist = ['timestamp','sales','awarness','SPFB_Index','SPFB_Index_Lag',
             'intercept','Google_trends','sales_lag','latent_sales']
   '''
   for k,v in varmap.items():
      if v not in iglist and '_awar' not in v and '_b2' not in v:
         eqlist.append('%s*%s_eff' %(k,rev_varmap.get('%s_awar'%(v))))  
   '''

   eqlist.append('%s*%s_eff' %(1,rev_varmap.get('sales_lag')))       


   transistionMap[rev_varmap.get('awarness')] = '+'.join(eqlist)
   #####################################################################################################

