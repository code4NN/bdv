import streamlit as st
import pandas as pd
# st.markdown(
#     """
#     <style>
#     [data-testid="baseButton-header"] {
#         visibility: hidden;
#     }
#     [data-testid="stHeader"] {
#     background-color: #365069;
#     color: white;
#     }
#     footer {
#     background-color: #365069;
#     color: white;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )




# df = pd.DataFrame({'category':[1,2],
#                            'amount':[2,'f'],
#                            'date':[3,'df'],
#                            'remark':[4,None]})
# st.dataframe(df)
# st.write(df.columns.get_loc("category"))
# df.insert(1,'newcolumn',-1)
# st.dataframe(df)

if 'mydb' not in st.session_state:
    sample_database = {"df":pd.DataFrame(
                                        # {'category':[],
                                        #   'amount':[],
                                        #   'date':[],
                                        #   'remark':[]}
                                        {'$category':[None],
                                          'amount':[1],
                                          'date':[2],
                                          'remark':[3]}
                                        ),
                        "mdata":{'$category':{}},
                        'root_bucket':['Kitchen',
                                       'Preaching',
                                        'Maintenance']}
    st.session_state['mydb'] = sample_database

st.caption("session_state")
st.write(st.session_state)

db = st.session_state['mydb']
root_columns = db['root_bucket']
mdata = db['mdata']
df = db['df']

def insert_new_category(parent_column,active_value):
    """
    parent_column: the column for which we have put the filter
    active value: the value in the column
    a new column will be generated with active_value
    """
    previous_prefix,column_name = parent_column.split("$")
    new_column_name = f"{previous_prefix+column_name[0].upper()}${active_value}"
    
    mdata[parent_column][active_value] = new_column_name
    mdata[new_column_name] = {}
        
    st.session_state['mydb']['mdata'] = mdata.copy()
    
    insert_index = df.columns.get_loc(parent_column) + 1
    df.insert(insert_index,new_column_name,None)
    st.session_state['mydb']['df'] = df.copy()

st.caption("df")
st.dataframe(df)

def filter_dashboard(column_name,
                     input_df,
                     is_first_call,
                     query_list = [],
                     selection_list = []):
    """
    returns
        - query_list
        - selection_list
    """
    unique_values = list(mdata[column_name].keys()) \
                if column_name in mdata.keys() else []
    unique_values = ['agg',*root_columns] if is_first_call else ['agg','raw',*unique_values,'+']
        
    user_selection = st.radio("label",
                                options=unique_values,
                                horizontal=True,
                                label_visibility='hidden',
                                format_func=lambda x: {'agg':":orange[Σ]",
                                                       'raw':':green[i]',
                                                       '+':":blue[\+ new]"}.get(x,f":gray[{x}]"))
    
    # Show aggregate values on column_name
    if user_selection == 'agg':
        return query_list,[*selection_list,'agg']
        
    # show aggregate values on column_name
    # Option to add sibling category
    elif user_selection =='+':
        new_category_name = st.text_input("Category _name")
        if new_category_name:
            st.button("Add",on_click=insert_new_category,args=[column_name,new_category_name])
        
        return query_list,[*selection_list,user_selection]
    
    elif user_selection == 'raw':
        return query_list,[*selection_list,'raw']
    
    # Show aggregate values on column_name
    # only comes on root_buckets
    elif user_selection not in mdata[column_name].keys():
        # this column is a leaf node
        # add the option to insert new column
        st.button("Add",on_click=insert_new_category,args=[column_name,user_selection])
        return query_list,[*selection_list,'raw']
    
    # sub_category possible
    else:
        next_column = mdata[column_name][user_selection]
        next_data = input_df.query(f"`{column_name}` == '{user_selection}' ")
        
        q2, s2 = filter_dashboard(column_name=next_column,
                        input_df=next_data,
                        is_first_call=False)
        return [f"(`{column_name}`=='{user_selection}')",*q2],[user_selection,*s2]
                            
# query,user_selection_list = filter_dashboard(
#                               column_name='category',
#                               input_df = df,
#                               is_first_call = True)
queries,selections = filter_dashboard(
                column_name='$category',
                input_df = df,
                is_first_call = True,
                selection_list=['$category'])
column_name,action = selections[-2:]
is_last_column = True if column_name not in mdata.keys() or mdata[column_name] else False
# st.write(queries)
# st.write(selections)
# st.caption(action)
if action in ['agg','+']:
    st.info(f"Show aggregate values on {column_name}")
elif action == 'raw':
    if is_last_column:
        st.info("Show raw values ")
    else:
        st.info("get all the sub columns and show uptil raw")
