import streamlit as st
import pandas as pd


















# df = pd.DataFrame({'category':[1,2],
#                            'amount':[2,'f'],
#                            'date':[3,'df'],
#                            'remark':[4,None]})
# st.dataframe(df)
# st.write(df.columns.get_loc("category"))
# df.insert(1,'newcolumn',-1)
# st.dataframe(df)
st.markdown(
        f"""
        <div style="position:relative;">
            <input type="text" value="some random cate" id="copyText" readonly style="opacity:0;pointer-events:none;position:absolute;left:0;top:0;height:0;width:0;z-index:-1;">
            <button onclick="copyToClipboard()" style="background-color:#4CAF50;color:white;padding:10px 20px;text-align:center;text-decoration:none;display:inline-block;font-size:16px;margin:4px 2px;cursor:pointer;border-radius:5px;">Copy Text</button>
        </div>
        <script>
            function copyToClipboard() {{
                var copyText = document.getElementById("copyText");
                copyText.select();
                copyText.setSelectionRange(0, 99999);
                document.execCommand("copy");
                alert("Text copied to clipboard: " + copyText.value);
            }}
        </script>
        """,
        unsafe_allow_html=True
    )

if 'mydb' not in st.session_state:
    sample_database = {"df":pd.DataFrame(
                                        # {'category':[],
                                        #   'amount':[],
                                        #   'date':[],
                                        #   'remark':[]}
                                        {'category':[None],
                                          'amount':[1],
                                          'date':[2],
                                          'remark':[3]}
                                        ),
                        "mdata":{'category':{'empty':True}},
                        'root_bucket':['Kitchen',
                                    #    'Preaching',
                                        'Maintenance']}
    st.session_state['mydb'] = sample_database
    
st.write(st.session_state)

db = st.session_state['mydb']
root_columns = db['root_bucket']
mdata = db['mdata']
df = db['df']

def insert_new_category(parent_column,active_value):
    if mdata[parent_column]['empty']:
        mdata[parent_column] = {'empty':False,
                                active_value:active_value}
    else:
        mdata[parent_column][active_value] = active_value
    st.session_state['mydb']['mdata'] = mdata.copy()
    
    insert_index = df.columns.get_loc(parent_column) + 1
    df.insert(insert_index,active_value,None)
    st.session_state['mydb']['df'] = df.copy()

st.dataframe(df)
st.write(df.category.unique().tolist())

def ui_option_to_add_category(parent_name,option_selected):
    pass
    # if st.checkbox("Crete new Category"):
        # if option_selected:
        # if user_selection in input_df.columns:
        #     st.caption(f":red[a column named `{user_selection}` already exists]")
        #     st.caption("please modify the name")
        #     new_category_name = left.text_input("category name",value=user_selection)
        #     if new_category_name in input_df.columns:
        #         st.caption("this name also already exists")
        #     else:
        #         right.button(f"+ {new_category_name} in {column_name}",on_click=insert_new_category,
        #                 args=[column_name,new_category_name])
        # else:
        #     right.button(f"+ {user_selection} in {column_name}",on_click=insert_new_category,
        #             args=[column_name,user_selection])

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
    mydata = input_df.copy()
    unique_values = mydata[column_name].unique().tolist() if mydata[column_name].nunique()>0 else []
    unique_values = ['all',*unique_values] if is_first_call else ['all',*unique_values,'+']
        
    user_selection = st.radio("label",
                                options=unique_values,
                                horizontal=True,
                                label_visibility='hidden')
    
    
    if mdata[column_name]['empty']:
        # this column is a leaf node
        # add the option to insert new column
        return [],[user_selection]
    # 
    if user_selection == 'all':
        query_list = [*query_list]
        selection_list = [*selection_list]
        return query_list,selection_list
    
    elif user_selection == '+':
        pass
    else:
        query_list = query_list.append(f" (`{column_name}` == '{user_selection}') ")
        
        next_data = mydata.query(query_list[-1])
        next_column = mdata[user_selection]
        next_unique_values = mydata[mdata].unique()
        
query,user_selection_list = filter_dashboard(
                                column_name='category',
                              input_df = df,
                              is_first_call = True)
