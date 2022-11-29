import pandas as pd
import numpy as np

#data viz
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()



# woe_discrete function is adapted from the 365 datascience class material.
# more information on woe calculation can be found on
# https://www.listendata.com/2015/03/weight-of-evidence-woe-and-information.html
def woe_discrete(df,discrete_variable_name,good_bad_variable_df):
  """
  a function to calculate WoE and IV of categorical features
  The function takes 3 arguments: a dataframe (inputs_train_prepr), a string (column name), and a dataframe (target_train_prepr).
  """
  #1 creating the concat dataframe
  df = pd.concat([df[discrete_variable_name],good_bad_variable_df],axis=1)
  #2 concating group by count + mean
  df = pd.concat ([df.groupby(df.columns.values[0], as_index = False) [df.columns.values[1]].count(),
                  df.groupby(df.columns.values[0], as_index = False) [df.columns.values[1]].mean()],
                 axis =1)
  #3 keeping three columns since one column is repated after concat
  df = df.iloc[:, [0,1,3]]
  #4 renaming the column names
  df.columns =[df.columns.values[0], 'n_obs','prop_good']
  #5 calculating the proportion of observation amounts
  df['prop_n_obs'] = df['n_obs'] / df['n_obs'].sum()
  #6 calculating the number of good and bad observations
  df['n_good']= df['prop_good'] * df['n_obs']
  df['n_bad'] = (1 - df['prop_good'])*df['n_obs']
  #7 calculating the proportion of good and  bad columns
  df['prop_n_good'] = df ['n_good'] / df['n_good'].sum()
  df['prop_n_bad'] = df ['n_bad'] / df['n_bad'].sum()
  #8 calculating the weight of evidence WoE
  df['WoE'] = np.log(df['prop_n_good']/df['prop_n_bad'])
  #9 sorting the alues
  df = df.sort_values(['WoE'])
  df = df.reset_index(drop = True)
  #10 additional columns to see how WoE changes from one cat to another
  df ['diff_prop_good'] = df['prop_good'].diff().abs()
  df['diff_WoE'] = df['WoE'].diff().abs()
  #11 calculating information value
  df['IV'] = (df['prop_n_good']-df['prop_n_bad'])*df['WoE']
  df['IV'] = df['IV'].sum()
  return df

def woe_ordered_continuous(df,discrete_variable_name,good_bad_variable_df):
  """
  a function to calculate WoE and IV of continuous features
  The function takes 3 arguments: a dataframe (inputs_train_prepr), a string (column name), and a dataframe (target_train_prepr).
  """
  #1 creating the concat dataframe
  df = pd.concat([df[discrete_variable_name],good_bad_variable_df],axis=1)
  #2 concating group by count + mean
  df = pd.concat ([df.groupby(df.columns.values[0], as_index = False) [df.columns.values[1]].count(),
                  df.groupby(df.columns.values[0], as_index = False) [df.columns.values[1]].mean()],
                 axis =1)
  #3 keeping three columns since one column is repated
  df = df.iloc[:, [0,1,3]]
  #4 renaming the column names
  df.columns =[df.columns.values[0], 'n_obs','prop_good']
  #5 calculating the proportion of observation amounts
  df['prop_n_obs'] = df['n_obs'] / df['n_obs'].sum()
  #6 calculating the number of good and bad observations
  df['n_good']= df['prop_good'] * df['n_obs']
  df['n_bad'] = (1 - df['prop_good'])*df['n_obs']
  #7 calculating the proportion of good and  bad columns
  df['prop_n_good'] = df ['n_good'] / df['n_good'].sum()
  df['prop_n_bad'] = df ['n_bad'] / df['n_bad'].sum()
  #8 calculating the weight of evidence WoE
  df['WoE'] = np.log(df['prop_n_good']/df['prop_n_bad'])
  #9 sorting the values - note that for the continous variables we want to keep the order of classes
  #df = df.sort_values(['WoE'])
  #df = df.reset_index(drop = True)
  #10 additional columns to see how WoE changes from one cat to another
  df ['diff_prop_good'] = df['prop_good'].diff().abs()
  df['diff_WoE'] = df['WoE'].diff().abs()
  #11 calculating information value
  df['IV'] = (df['prop_n_good']-df['prop_n_bad'])*df['WoE']
  df['IV'] = df['IV'].sum()
  return df

def plot_by_woe(df_WoE,rotation_x_axis_labels=0):
  """
  Function to graph Weight of Evidence evaluation over different categories
  """
  x= np.array(df_WoE.iloc[:,0].apply(str))
  y= df_WoE ['WoE']
  plt.figure(figsize= (12,4))
  plt.plot(x, y, marker = 'o', linestyle ='--',color = 'k')
  plt.xlabel(df_WoE.columns[0])
  plt.ylabel('Weight of Evidence')
  plt.title(str('Weight of Evidence by ' + df_WoE.columns[0]))
  plt.xticks(rotation = rotation_x_axis_labels)

def preproc_input(loan_data):
  # Preprocessing - Target
  #if the result == 'Charged Off', 'Default', 'Does not meet the credit policy. Status: Charged Off.',
  #                   'Late (31-120 days)', We take 0 (Bad). Otherwise = 1 (Good)
  bad_def = ['Charged Off', 'Default','Does not meet the credit policy. Status: Charged Off.',
            'Late (31-120 days)']

  #good is 1, bad is 0
  loan_data['good_bad'] = np.where(loan_data['loan_status'].isin(bad_def), 0, 1) 
  return loan_data
  
def preproc_input(df_inputs_prepr):
  # Preprocessing - Input
  #1
  df_inputs_prepr['home_ownership:RENT_OTHER_NONE_ANY'] = sum ([df_inputs_prepr['home_ownership:RENT'], df_inputs_prepr['home_ownership:OTHER'],
                                                                df_inputs_prepr['home_ownership:NONE'], df_inputs_prepr['home_ownership:ANY'],])
  #2 
  if ['addr_state:ND'] in df_inputs_prepr.columns.values:
    pass
  else:
    df_inputs_prepr['addr_state:ND'] = 0

  #3
  # We create the following categories:
  # 'ND' 'NE' 'IA' NV' 'FL' 'HI' 'AL'
  # 'NM' 'VA'
  # 'NY'
  # 'OK' 'TN' 'MO' 'LA' 'MD' 'NC'
  # 'CA'
  # 'UT' 'KY' 'AZ' 'NJ'
  # 'AR' 'MI' 'PA' 'OH' 'MN'
  # 'RI' 'MA' 'DE' 'SD' 'IN'
  # 'GA' 'WA' 'OR'
  # 'WI' 'MT'
  # 'TX'
  # 'IL' 'CT'
  # 'KS' 'SC' 'CO' 'VT' 'AK' 'MS'
  # 'WV' 'NH' 'WY' 'DC' 'ME' 'ID'

  # 'IA_NV_HI_ID_AL_FL' will be the reference category.

  df_inputs_prepr['addr_state:ND_NE_IA_NV_FL_HI_AL'] = sum([df_inputs_prepr['addr_state:ND'], df_inputs_prepr['addr_state:NE'],
                                                df_inputs_prepr['addr_state:IA'], df_inputs_prepr['addr_state:NV'],
                                                df_inputs_prepr['addr_state:FL'], df_inputs_prepr['addr_state:HI'],
                                                            df_inputs_prepr['addr_state:AL']])

  df_inputs_prepr['addr_state:NM_VA'] = sum([df_inputs_prepr['addr_state:NM'], df_inputs_prepr['addr_state:VA']])

  df_inputs_prepr['addr_state:OK_TN_MO_LA_MD_NC'] = sum([df_inputs_prepr['addr_state:OK'], df_inputs_prepr['addr_state:TN'],
                                                df_inputs_prepr['addr_state:MO'], df_inputs_prepr['addr_state:LA'],
                                                df_inputs_prepr['addr_state:MD'], df_inputs_prepr['addr_state:NC']])

  df_inputs_prepr['addr_state:UT_KY_AZ_NJ'] = sum([df_inputs_prepr['addr_state:UT'], df_inputs_prepr['addr_state:KY'],
                                                df_inputs_prepr['addr_state:AZ'], df_inputs_prepr['addr_state:NJ']])

  df_inputs_prepr['addr_state:AR_MI_PA_OH_MN'] = sum([df_inputs_prepr['addr_state:AR'], df_inputs_prepr['addr_state:MI'],
                                                df_inputs_prepr['addr_state:PA'], df_inputs_prepr['addr_state:OH'],
                                                df_inputs_prepr['addr_state:MN']])

  df_inputs_prepr['addr_state:RI_MA_DE_SD_IN'] = sum([df_inputs_prepr['addr_state:RI'], df_inputs_prepr['addr_state:MA'],
                                                df_inputs_prepr['addr_state:DE'], df_inputs_prepr['addr_state:SD'],
                                                df_inputs_prepr['addr_state:IN']])

  df_inputs_prepr['addr_state:GA_WA_OR'] = sum([df_inputs_prepr['addr_state:GA'], df_inputs_prepr['addr_state:WA'],
                                                df_inputs_prepr['addr_state:OR']])

  df_inputs_prepr['addr_state:WI_MT'] = sum([df_inputs_prepr['addr_state:WI'], df_inputs_prepr['addr_state:MT']])

  df_inputs_prepr['addr_state:IL_CT'] = sum([df_inputs_prepr['addr_state:IL'], df_inputs_prepr['addr_state:CT']])

  df_inputs_prepr['addr_state:KS_SC_CO_VT_AK_MS'] = sum([df_inputs_prepr['addr_state:KS'], df_inputs_prepr['addr_state:SC'],
                                                df_inputs_prepr['addr_state:CO'], df_inputs_prepr['addr_state:VT'],
                                                df_inputs_prepr['addr_state:AK'], df_inputs_prepr['addr_state:MS']])

  df_inputs_prepr['addr_state:WV_NH_WY_DC_ME_ID'] = sum([df_inputs_prepr['addr_state:WV'], df_inputs_prepr['addr_state:NH'],
                                                df_inputs_prepr['addr_state:WY'], df_inputs_prepr['addr_state:DC'],
                                                df_inputs_prepr['addr_state:ME'], df_inputs_prepr['addr_state:ID']])
                          
  #4
  # We combine 'educational', 'small_business', 'wedding', 'renewable_energy', 'moving', 'house' in one category: 'educ__sm_b__wedd__ren_en__mov__house'.
  # We combine 'other', 'medical', 'vacation' in one category: 'oth__med__vacation'.
  # We combine 'major_purchase', 'car', 'home_improvement' in one category: 'major_purch__car__home_impr'.
  # We leave 'debt_consolidtion' in a separate category.
  # We leave 'credit_card' in a separate category.
  # 'educ__sm_b__wedd__ren_en__mov__house' will be the reference category.
  df_inputs_prepr['purpose:educ__sm_b__wedd__ren_en__mov__house'] = sum([df_inputs_prepr['purpose:educational'], df_inputs_prepr['purpose:small_business'],
                                                                  df_inputs_prepr['purpose:wedding'], df_inputs_prepr['purpose:renewable_energy'],
                                                                  df_inputs_prepr['purpose:moving'], df_inputs_prepr['purpose:house']])
  df_inputs_prepr['purpose:oth__med__vacation'] = sum([df_inputs_prepr['purpose:other'], df_inputs_prepr['purpose:medical'],
                                              df_inputs_prepr['purpose:vacation']])
  df_inputs_prepr['purpose:major_purch__car__home_impr'] = sum([df_inputs_prepr['purpose:major_purchase'], df_inputs_prepr['purpose:car'],
                                                          df_inputs_prepr['purpose:home_improvement']])

  #5
  # We create the following categories: '0', '1', '2 - 4', '5 - 6', '7 - 9', '10'
  # '0' will be the reference category
  df_inputs_prepr['emp_length:0'] = np.where(df_inputs_prepr['emp_length_int'].isin([0]), 1, 0)
  df_inputs_prepr['emp_length:1'] = np.where(df_inputs_prepr['emp_length_int'].isin([1]), 1, 0)
  df_inputs_prepr['emp_length:2-4'] = np.where(df_inputs_prepr['emp_length_int'].isin(range(2, 5)), 1, 0)
  df_inputs_prepr['emp_length:5-6'] = np.where(df_inputs_prepr['emp_length_int'].isin(range(5, 7)), 1, 0)
  df_inputs_prepr['emp_length:7-9'] = np.where(df_inputs_prepr['emp_length_int'].isin(range(7, 10)), 1, 0)
  df_inputs_prepr['emp_length:10'] = np.where(df_inputs_prepr['emp_length_int'].isin([10]), 1, 0)

  #6
  # WoE is monotonically decreasing with income, so we split income in 10 equal categories, each with width of 15k.
  df_inputs_prepr['annual_inc:<20K'] = np.where((df_inputs_prepr['annual_inc'] <= 20000), 1, 0)
  df_inputs_prepr['annual_inc:20K-30K'] = np.where((df_inputs_prepr['annual_inc'] > 20000) & (df_inputs_prepr['annual_inc'] <= 30000), 1, 0)
  df_inputs_prepr['annual_inc:30K-40K'] = np.where((df_inputs_prepr['annual_inc'] > 30000) & (df_inputs_prepr['annual_inc'] <= 40000), 1, 0)
  df_inputs_prepr['annual_inc:40K-50K'] = np.where((df_inputs_prepr['annual_inc'] > 40000) & (df_inputs_prepr['annual_inc'] <= 50000), 1, 0)
  df_inputs_prepr['annual_inc:50K-60K'] = np.where((df_inputs_prepr['annual_inc'] > 50000) & (df_inputs_prepr['annual_inc'] <= 60000), 1, 0)
  df_inputs_prepr['annual_inc:60K-70K'] = np.where((df_inputs_prepr['annual_inc'] > 60000) & (df_inputs_prepr['annual_inc'] <= 70000), 1, 0)
  df_inputs_prepr['annual_inc:70K-80K'] = np.where((df_inputs_prepr['annual_inc'] > 70000) & (df_inputs_prepr['annual_inc'] <= 80000), 1, 0)
  df_inputs_prepr['annual_inc:80K-90K'] = np.where((df_inputs_prepr['annual_inc'] > 80000) & (df_inputs_prepr['annual_inc'] <= 90000), 1, 0)
  df_inputs_prepr['annual_inc:90K-100K'] = np.where((df_inputs_prepr['annual_inc'] > 90000) & (df_inputs_prepr['annual_inc'] <= 100000), 1, 0)
  df_inputs_prepr['annual_inc:100K-120K'] = np.where((df_inputs_prepr['annual_inc'] > 100000) & (df_inputs_prepr['annual_inc'] <= 120000), 1, 0)
  df_inputs_prepr['annual_inc:120K-140K'] = np.where((df_inputs_prepr['annual_inc'] > 120000) & (df_inputs_prepr['annual_inc'] <= 140000), 1, 0)
  df_inputs_prepr['annual_inc:>140K'] = np.where((df_inputs_prepr['annual_inc'] > 140000), 1, 0)

  #7
  # Categories: Missing, 0-3, 4-30, 31-56, >=57
  df_inputs_prepr['mths_since_last_delinq:Missing'] = np.where((df_inputs_prepr['mths_since_last_delinq'].isnull()), 1, 0)
  df_inputs_prepr['mths_since_last_delinq:0-3'] = np.where((df_inputs_prepr['mths_since_last_delinq'] >= 0) & (df_inputs_prepr['mths_since_last_delinq'] <= 3), 1, 0)
  df_inputs_prepr['mths_since_last_delinq:4-30'] = np.where((df_inputs_prepr['mths_since_last_delinq'] >= 4) & (df_inputs_prepr['mths_since_last_delinq'] <= 30), 1, 0)
  df_inputs_prepr['mths_since_last_delinq:31-56'] = np.where((df_inputs_prepr['mths_since_last_delinq'] >= 31) & (df_inputs_prepr['mths_since_last_delinq'] <= 56), 1, 0)
  df_inputs_prepr['mths_since_last_delinq:>=57'] = np.where((df_inputs_prepr['mths_since_last_delinq'] >= 57), 1, 0)

  #8 
  # Categories:
  df_inputs_prepr['dti:<=1.4'] = np.where((df_inputs_prepr['dti'] <= 1.4), 1, 0)
  df_inputs_prepr['dti:1.4-3.5'] = np.where((df_inputs_prepr['dti'] > 1.4) & (df_inputs_prepr['dti'] <= 3.5), 1, 0)
  df_inputs_prepr['dti:3.5-7.7'] = np.where((df_inputs_prepr['dti'] > 3.5) & (df_inputs_prepr['dti'] <= 7.7), 1, 0)
  df_inputs_prepr['dti:7.7-10.5'] = np.where((df_inputs_prepr['dti'] > 7.7) & (df_inputs_prepr['dti'] <= 10.5), 1, 0)
  df_inputs_prepr['dti:10.5-16.1'] = np.where((df_inputs_prepr['dti'] > 10.5) & (df_inputs_prepr['dti'] <= 16.1), 1, 0)
  df_inputs_prepr['dti:16.1-20.3'] = np.where((df_inputs_prepr['dti'] > 16.1) & (df_inputs_prepr['dti'] <= 20.3), 1, 0)
  df_inputs_prepr['dti:20.3-21.7'] = np.where((df_inputs_prepr['dti'] > 20.3) & (df_inputs_prepr['dti'] <= 21.7), 1, 0)
  df_inputs_prepr['dti:21.7-22.4'] = np.where((df_inputs_prepr['dti'] > 21.7) & (df_inputs_prepr['dti'] <= 22.4), 1, 0)
  df_inputs_prepr['dti:22.4-35'] = np.where((df_inputs_prepr['dti'] > 22.4) & (df_inputs_prepr['dti'] <= 35), 1, 0)
  df_inputs_prepr['dti:>35'] = np.where((df_inputs_prepr['dti'] > 35), 1, 0)

  #9
  # Categories: 'Missing', '0-2', '3-20', '21-31', '32-80', '81-86', '>86'
  df_inputs_prepr['mths_since_last_record:Missing'] = np.where((df_inputs_prepr['mths_since_last_record'].isnull()), 1, 0)
  df_inputs_prepr['mths_since_last_record:0-2'] = np.where((df_inputs_prepr['mths_since_last_record'] >= 0) & (df_inputs_prepr['mths_since_last_record'] <= 2), 1, 0)
  df_inputs_prepr['mths_since_last_record:3-20'] = np.where((df_inputs_prepr['mths_since_last_record'] >= 3) & (df_inputs_prepr['mths_since_last_record'] <= 20), 1, 0)
  df_inputs_prepr['mths_since_last_record:21-31'] = np.where((df_inputs_prepr['mths_since_last_record'] >= 21) & (df_inputs_prepr['mths_since_last_record'] <= 31), 1, 0)
  df_inputs_prepr['mths_since_last_record:32-80'] = np.where((df_inputs_prepr['mths_since_last_record'] >= 32) & (df_inputs_prepr['mths_since_last_record'] <= 80), 1, 0)
  df_inputs_prepr['mths_since_last_record:81-86'] = np.where((df_inputs_prepr['mths_since_last_record'] >= 81) & (df_inputs_prepr['mths_since_last_record'] <= 86), 1, 0)
  df_inputs_prepr['mths_since_last_record:>=86'] = np.where((df_inputs_prepr['mths_since_last_record'] > 86), 1, 0)
  return df_inputs_prepr