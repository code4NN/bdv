import streamlit as st

def mycheckbox(question_data,showhelp):
    title = question_data['title']
    helptext = question_data['helptext']

    if not showhelp:    
        return st.checkbox(label=title,value=False)
    else:
        return st.checkbox(label=title,help=helptext,value=False)

def mynuminput(question_data,showhelp):
    title = question_data['title']
    lower_limit = int(question_data['min'])
    upper_limit = question_data['max']
    helptext = question_data['helptext']
    if showhelp:
        value = st.number_input(title,min_value=lower_limit,help=helptext,step=1)
    else:
        value = st.number_input(title,min_value=lower_limit,step=1)
    return value

def mytimeinput(question_data,showhelp):
    title = question_data['title']
    helptext = question_data['helptext']
    if showhelp:
        value = st.number_input(title,min_value=0,max_value=2359,help=helptext)
    else:
        value = st.number_input(title,min_value=0,max_value=2359)
    if value:
        return value
    else:
        st.caption(":red[Cannot be blank]")
        return -1

def daily_filling(qnadict,show_help_text=False):

    result = {}
    incomplete = False
    # morning program
    with st.expander("Morning Program",expanded=True):
        cols = st.columns(4)
        for i,item in enumerate(['on_time','sa','morning_class','mangal_aarti']):
            with cols[i]:
                result[item]= mycheckbox(qnadict[item],show_help_text)
    
    result['japa_time'] = mytimeinput(qnadict['japa_time'],show_help_text)

    # reading
    with st.expander("Reading",expanded=True):
        left,right = st.columns(2)
        with left:
            result['sp_books'] = mynuminput(qnadict['sp_books'],show_help_text)
        with right:
            result['about_sp'] = mynuminput(qnadict['about_sp'],show_help_text)
    # hearing
    with st.expander("Hearing",expanded=True):
        left,middle,right = st.columns(3)
        with left:
            result['hearing_sp'] = mynuminput(qnadict['hearing_sp'],show_help_text)
            result['hearing_councellor'] = mynuminput(qnadict['hearing_councellor'],show_help_text)

        with middle:
            result['hearing_hhrnsm'] = mynuminput(qnadict['hearing_hhrnsm'],show_help_text)
            result['hearing_other'] = mynuminput(qnadict['hearing_other'],show_help_text)

        with right:
            result['hearing_hgrsp'] = mynuminput(qnadict['hearing_hgrsp'],show_help_text)
    # shloka
    result['shloka'] = st.radio(qnadict['shloka']['title'],options=[0,1,2,3],horizontal=True)
    result['shayan_kirtan'] = mycheckbox(qnadict['shayan_kirtan'],show_help_text)

    # body
    with st.expander("Shayan",expanded=True):
        columns = st.columns(3)
        with columns[0]:
            result['wake_up'] = mytimeinput(qnadict['wake_up'],show_help_text)
        with columns[1]:
            result['to_bed'] = mytimeinput(qnadict['to_bed'],show_help_text)
        with columns[2]:
            result['day_rest'] = mynuminput(qnadict['day_rest'],show_help_text)
    
    with st.expander("",expanded=True):
        left,right = st.columns(2)
        with left:
            result['pc'] = mycheckbox(qnadict['pc'],show_help_text)
        with right:
            result['fsc'] = mycheckbox(qnadict['fsc'],show_help_text)

    required_columns = ['japa_time','wake_up','to_bed']
    for column in required_columns:
        if result[column] == -1:
            incomplete = True
            break
    return incomplete,result