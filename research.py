from datetime import datetime
import json
import streamlit as st
import pandas as pd

from other_pages.googleapi import download_data, upload_data

class monthdbclass:
  def __init__(self):
      
      # local copy of the display database
      self.data_defined = False
      self.df = None
      self.metadata = None
      self.new_column_id = None
      self.root_buckets = None
      self._change_in_df = 0

      # cloud connect
      self._expense_database = None
      self._expense_database_refresh = True
      self._expense_database_range = 'expense!A:D'
      self._template_database_range = 'expense!B11'
      
      # active month
      self._have_active_month_db = False
      self.active_month_db = None
   
  @property
  def current_database(self):
    dfjson = self.df.to_json(orient='index')
    metadatajson = json.dumps(self.metadata)
    newcolidjson = json.dumps(self.new_column_id)
    buckets = json.dumps(self.root_buckets)
    finaldf = json.dumps({'df':dfjson,'metadata':metadatajson,'new_column_id':newcolidjson,
                          'root_bucket':buckets},indent=None)
    return finaldf  
  
  @property
  def expense_database(self):
        """
        1. downloads the data if refresh is True
        2. else returns the database
        Actions
            1. download and save in the class
            3. set the refresh to False
            4. return
        """
        if self._expense_database_refresh:
            # download a fresh data
            # update database and refresh to False
            # return
            _expense_database = download_data(4,self._expense_database_range)
            _expense_database = pd.DataFrame(_expense_database[1:],columns=_expense_database[0])
            
            # get the metadata out of it
            metadata = _expense_database[['key','value']].copy(deep=True)
            metadata = dict(zip(metadata['key'],metadata['value']))

            # get the template month_database
            template_monthdb = json.loads(metadata['template_db'])
            template_monthdf = pd.read_json(template_monthdb['df'],orient='index')
            # template_monthdf.insert(len(template_monthdf.columns),'paid_by',None)
            
            template_monthdb['df'] = template_monthdf
            template_monthdb['metadata'] = json.loads(template_monthdb['metadata'])
            template_monthdb['new_column_id'] = int(template_monthdb['new_column_id'])
            template_monthdb['root_bucket'] = json.loads(template_monthdb['root_bucket'])

            # get the current month data
            allmonthdata = _expense_database.data.tolist()[:int(metadata['db_len'])]
            allmonthname = _expense_database.month.tolist()[:int(metadata['db_len'])]

            self._expense_database = {'mdata':metadata,
                                      'templatedb':template_monthdb,
                                      'months':allmonthname,
                                      'datas':allmonthdata}
            self._expense_database_refresh = False

            return self._expense_database
        else:
            return self._expense_database
  
  def parse_month_db(self,monthdb):
    # get the dict
    monthdb = json.loads(monthdb)
    # monthdb = json.loads
    df = pd.read_json(monthdb['df'],orient='index')
    metadata = json.loads(monthdb['metadata'])
    new_column_id = int(monthdb['new_column_id'])
    root_bucket = json.loads(monthdb['root_bucket'])
    self.active_month_db= {'df':df.copy(deep=True),
                          'metadata':metadata,
                          'new_column_id':new_column_id,
                          'root_bucket':root_bucket}
    self._have_active_month_db = True

  def insert_new_category(self,parent_column,active_value):
    """
    parent_column: the column for which we have put the filter
    active value: the value in the column
    a new column will be generated with active_value
    """
    new_col_id = int(self.new_column_id)
    
    new_column_name = f"{new_col_id}Q{active_value}"
    
    st.write(self.metadata)
    st.write(parent_column,active_value)
    self.metadata[parent_column][active_value] = new_column_name
    self.metadata[new_column_name] = {}
        
    # st.session_state['mydb']['mdata'] = mdata.copy()
    self.new_column_id = new_col_id + 1
    
    insert_index = self.df.columns.get_loc(parent_column) + 1
    self.df.insert(insert_index,new_column_name,None)
    self._change_in_df += 1
      
  def filter_dashboard(self,
                       column_name,
                       input_df,
                       is_first_call,
                      ):
      """
      returns
          - query_list
          - selection_list
      """
      unique_values = list(self.metadata[column_name].keys())
      unique_values = ['agg','raw',*unique_values] if is_first_call else ['agg','raw',*unique_values,'+']
          
      user_selection = st.radio(column_name.split("Q")[1],
                                  options=unique_values,
                                  horizontal=True,
                                  # label_visibility='hidden',
                                  format_func=lambda x: {'agg':":orange[Σ]",
                                                        'raw':':green[i]',
                                                        '+':":blue[\+]"}.get(x,f":gray[{x}]"))
      
      # Show aggregate values on column_name
      if user_selection in ['agg','raw']:
          return [],[[column_name,user_selection]]
          
      # show aggregate values on column_name
      # Option to add sibling category
      elif user_selection =='+':
        with st.popover("Adding New category"):
          new_category_name = st.text_input("Category _name")
          if new_category_name and (not new_category_name.__contains__('Q')):
              st.button("Add",on_click=self.insert_new_category,args=[column_name,new_category_name])
          else:
             st.button("Add",disabled=True)
          return [],[[column_name,user_selection]]
      
          
      # sub_category possible
      else:
          next_column = self.metadata[column_name][user_selection]
          next_data = input_df.query(f"`{column_name}` == '{user_selection}' ")
          
          q2, s2 = self.filter_dashboard(column_name=next_column,
                                    input_df=next_data,
                                    is_first_call=False
                                    )
          return [f"(`{column_name}`=='{user_selection}')",*q2],[[column_name,user_selection],*s2]

  def get_user_choice(self,option,choice_dict):
    if len(choice_dict) == 1:
      # user_selection = list(choice_dict.values())[0]
      user_selection = st.radio(option,options=choice_dict.keys(),horizontal=True,disabled=True)
      user_selection = choice_dict[user_selection]
    else:
      user_selection = st.radio(option,options=choice_dict.keys(),horizontal=True)
      user_selection = choice_dict[user_selection]
      
    if len(self.metadata[user_selection])==0:
      return {option:user_selection}
    else:
      return {option:user_selection,**self.get_user_choice(user_selection,self.metadata[user_selection])}
  
  def insert_an_entry(self,records):
    newentry = {k:records[k] for k in self.df.keys()}
    newentrydf = pd.DataFrame.from_records(newentry)
    self.df = pd.concat([self.df, newentrydf],axis=0).reset_index(drop=True)
    self._change_in_df += 1
    st.session_state['enter_agenda'] = ''
  
  def display(self):
    expensedatbase = self.expense_database
    templatedb = expensedatbase['templatedb']
    
    month_list = expensedatbase['months']
    metadata = expensedatbase['mdata']
    data_list = expensedatbase['datas']
    
    sidebarpop = st.popover("⬅")
    left,_,right = st.columns([3,1,2])
    
    with sidebarpop:
      def refresh_db_copy():
        self.data_defined = False
        self.df = None
        self.metadata = None
        self.new_column_id = None
        self.root_buckets = None
        self._change_in_df = 0
        
        # parse the db
        self._have_active_month_db = False
        
      page = st.radio(":gray[Choose page]",options=['data','template'],index=0,on_change=refresh_db_copy)
      if page=='data':
        active_index = st.radio("Choose Month",options=list(range(len(month_list))),
                  format_func=lambda x: month_list[x],
                  index=len(month_list)-1,
                  on_change=refresh_db_copy)
        active_month_name = month_list[active_index]
        if not self._have_active_month_db:
          self.parse_month_db(data_list[active_index])
      else:
        assert page=='template'
        def update_next_month(metadata,month_list):
          active_index = len(month_list)
          
          next_meta_data = [[metadata['next_month']],
                          [metadata['next_year']],
                          [metadata['next_row']]]
          upload_data(4,'expense!B2:B4',next_meta_data)
          

          nextmonthdfjson = metadata['template_db']

          upload_data(4,f"expense!C{active_index+2}:D{active_index+2}",
                      [[metadata['next_month_name'],nextmonthdfjson]])
          self._expense_database_refresh=True
        st.button(f"Create data for {metadata['next_month_name']}",on_click=update_next_month,
                  args=[metadata,month_list],type='primary')
    
    if page == 'template':
      input_database = templatedb
      if not self.data_defined:
        self.df = input_database['df']
        self.metadata = input_database['metadata']
        self.new_column_id = input_database['new_column_id']
        self.root_buckets = input_database['root_bucket']
        # st.write(json.loads(self.root_buckets))
        self._change_in_df = 0
        
        # for column_name in self.root_buckets:
        #   self.insert_new_category('1Qcategory',column_name)
        self.data_defined = True
      
      with left:
        self.filter_dashboard("1Qcategory",
                              self.df.copy(deep=True),True)
        st.dataframe(self.df)
      with right:
        if self._change_in_df >0:
          def sync_templatedb():
            current_database = self.current_database
            upload_data(4,self._template_database_range,[[current_database]])
            self._change_in_df = 0
          st.button(f"Sync {self._change_in_df} changes",type='primary',on_click=sync_templatedb)
        else:
          st.success("All up to date")
        st.write(self.current_database)
    else:
      active_month_database = self.active_month_db
      
      if not self.data_defined:
        self.df = active_month_database['df']
        self.metadata = active_month_database['metadata']
        self.new_column_id = active_month_database['new_column_id']
        self.root_buckets = active_month_database['root_bucket']
        self._change_in_df = 0
        self.data_defined = True
        
      with left:
        queries, selections = self.filter_dashboard("1Qcategory",
                                                  self.df.copy(deep=True),
                                                  True)
        column_name,action =  selections[-1]
        is_last_column = len(self.metadata[column_name])==0
        if action in ['agg','+']:
            st.info(f"Show aggregate values on {column_name}")
            
        else:
          assert action == 'raw'
          if is_last_column:
              st.info("Show raw values")
          else:
              st.info("get all the sub columns and show uptil raw")
        
        displaybox = st.empty()
      with right:
        requestbody = {}
        for hits in selections[:-1]:
          column_name,choice = hits
          requestbody[column_name] = choice
          
        current_column = selections[-1][0]
        st.write(requestbody)
        remaining_option = {}
        if not is_last_column:
          remaining_option = self.get_user_choice(current_column,self.metadata[current_column])
          requestbody = {**requestbody,**remaining_option}
        
        # Typical inputs from user
        incomplete = 1
        requestbody['agenda'] = st.text_input("Agenda",key='enter_agenda')
        if not requestbody['agenda']:
          st.caption(":red[cannot be blank]")
          incomplete *=0
        requestbody['date'] = st.date_input("date").strftime("%d-%b (%a),%Y")
        requestbody['amount'] = st.number_input('Amount',step=100,min_value=1)
        requestbody['remark'] = st.text_input("Remark")
        if not requestbody['remark']:
          requestbody['remark'] = 'No remark'
        
        paidby = st.radio("from",options=['VOICE','other'])
        if paidby == 'other':
          paidby = st.text_input("Name")
          if not paidby:
            st.caption(":red[cannot be blank]")
            incomplete *=0
        requestbody['paid_by'] = paidby
        
        requestbody['timestamp'] = datetime.now().strftime("%d-%b-%y %H%M")
        
        if incomplete==0:
          st.button("Submit 🚀",disabled=True)
        else:
          st.button("Submit 🚀", on_click=self.insert_an_entry, args=[requestbody])
        # combine the results
        columns_to_show = [i for i in remaining_option.keys()]
        columns_to_show = [*columns_to_show,'agenda','amount','date','remark','paid_by','timestamp']
        
        st.caption("have columns")
        st.write(columns_to_show)
        unusedbody = {i:-1 for i in self.df if i not in requestbody.keys()}
        
        st.write(unusedbody)
        with displaybox:
          if action == 'raw':
            with st.popover("Customise columns"):
              display_columns = st.multiselect("Choose Columns to display",options=columns_to_show,
                                               default=columns_to_show)
              columns_to_show = [i for i in columns_to_show if i in display_columns]            
            st.dataframe(self.df)
                
        
        
        
        
      

if 'mydb' not in st.session_state:
    sample_database = {"df":pd.DataFrame(
                                        {'1Qcategory':[None],
                                          'amount':[1],
                                          'date':[2],
                                          'remark':[3]}
                                        ),
                        "mdata":{'1Qcategory':{}},
                        "new_col_id":2,
                        'root_bucket':['Kitchen',
                                       'Preaching',
                                        'Maintenance']}
    st.session_state['mydb'] = monthdbclass()
    

app = st.session_state['mydb']
app.display()

