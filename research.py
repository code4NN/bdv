import streamlit as st
import pandas as pd

def insert_new_category(parent_column,active_value):
    """
    parent_column: the column for which we have put the filter
    active value: the value in the column
    a new column will be generated with active_value
    """
    mdata = st.session_state['mydb']['mdata']
    df = st.session_state['mydb']['df']
    new_col_id = int(st.session_state['mydb']['new_col_id'])
    
    # previous_prefix = parent_column.split("$")[0]
    # depth,_ = previous_prefix.split("_")
    # sibling_order = len(mdata[parent_column])
    # new_column_id = mdata['']
    new_column_name = f"{new_col_id}${active_value}"
    
    mdata[parent_column][active_value] = new_column_name
    mdata[new_column_name] = {}
        
    st.session_state['mydb']['mdata'] = mdata.copy()
    st.session_state['mydb']['new_col_id'] = new_col_id + 1
    
    insert_index = df.columns.get_loc(parent_column) + 1
    df.insert(insert_index,new_column_name,None)
    st.session_state['mydb']['df'] = df.copy()
    
if 'mydb' not in st.session_state:
    sample_database = {"df":pd.DataFrame(
                                        # {'category':[],
                                        #   'amount':[],
                                        #   'date':[],
                                        #   'remark':[]}
                                        {'1$category':[None],
                                          'amount':[1],
                                          'date':[2],
                                          'remark':[3]}
                                        ),
                        "mdata":{'1$category':{}},
                        "new_col_id":2,
                        'root_bucket':['Kitchen',
                                       'Preaching',
                                        'Maintenance']}
    st.session_state['mydb'] = sample_database
    for column_name in sample_database['root_bucket']:
      insert_new_category('1$category',column_name)

db = st.session_state['mydb']
root_columns = db['root_bucket']
mdata = db['mdata']
df = db['df']
# st.write(st.session_state['mydb']['mdata'])

def filter_dashboard(column_name,
                     input_df,
                     is_first_call,
                     ):
    """
    returns
        - query_list
        - selection_list
    """
    unique_values = list(mdata[column_name].keys())
    unique_values = ['agg','raw',*unique_values] if is_first_call else ['agg','raw',*unique_values,'+']
        
    user_selection = st.radio(column_name.split("$")[1],
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
        if new_category_name:
            st.button("Add",on_click=insert_new_category,args=[column_name,new_category_name])
        
        return [],[[column_name,user_selection]]
    
        
    # sub_category possible
    else:
        next_column = mdata[column_name][user_selection]
        next_data = input_df.query(f"`{column_name}` == '{user_selection}' ")
        
        q2, s2 = filter_dashboard(column_name=next_column,
                                  input_df=next_data,
                                  is_first_call=False
                                  )
        return [f"(`{column_name}`=='{user_selection}')",*q2],[[column_name,user_selection],*s2]
                            
queries,selections = filter_dashboard(
                column_name='1$category',
                input_df = df,
                is_first_call = True
                )
# st.write(selections)
column_name,action =  selections[-1]
is_last_column = len(mdata[column_name])==0
is_last_column
# st.write(queries)
# st.write(selections)
# st.caption(action)
if action in ['agg','+']:
    st.info(f"Show aggregate values on {column_name}")
    
elif action == 'raw':
    if is_last_column:
        st.info("Show raw values")
    else:
        st.info("get all the sub columns and show uptil raw")
else:
  pass
# st.write(queries)

def get_user_choice(option,choice_dict):
  if len(choice_dict) == 1:
    # user_selection = list(choice_dict.values())[0]
    user_selection = st.radio(option,options=choice_dict.keys(),horizontal=True,disabled=True)
    user_selection = choice_dict[user_selection]
  else:
    user_selection = st.radio(option,options=choice_dict.keys(),horizontal=True)
    user_selection = choice_dict[user_selection]
    
  if len(mdata[user_selection])==0:
    return {option:user_selection}
  else:
    return {option:user_selection,**get_user_choice(user_selection,mdata[user_selection])}
  
st.divider()
requestbody = {}
for hits in selections[:-1]:
  column_name,choice = hits
  requestbody[column_name] = choice
  
current_column = selections[-1][0]
st.write(requestbody)
if not is_last_column:
  remaining_option = get_user_choice(current_column,mdata[current_column])
# regular things
st.text_input("Agenda")
st.date_input("date")
st.number_input('Amount')
st.radio("from",options=['voice','other'])
