import streamlit as st
import pandas as pd

def global_slookup(name,value,dfstd):
        sdf = dfstd.query(f"name == '{name}'").copy()
        sdf[['value','mark']] = sdf[['value','mark']].astype('float')
        sdf.sort_values(by=['value'],inplace=True)
        for _, row in sdf.iterrows():
            if value <= row['value']:
                return row['mark']
            
def mycheckbox(question_data, showhelp,show_mark,standard):
    title = question_data["title"]
    helptext = question_data["helptext"] if showhelp else None

    userinput = st.checkbox(label=title, value=False,help=helptext)
    if show_mark:
            fullmark = standard[question_data['key']]['mark']
            marks = fullmark if userinput else 0
            st.caption(marks)
    return userinput

def mynuminput(question_data, showhelp,show_mark=False,_standard_df=None):
    title = question_data["title"]
    lower_limit = int(question_data["min"])
    upper_limit = question_data["max"]
    helptext = question_data["helptext"] if showhelp else None
    value = st.number_input(title, min_value=lower_limit, help=helptext, step=1)
    if show_mark:
        mark = global_slookup(question_data['key'],value,_standard_df)
        st.caption(mark)
    return value

def verify_time(t):
    t = round(t)
    st = str(t)
    valid = True
    time = None
    
    if t < 0 or t > 2359:
        valid = False
    elif t < 10:
        time = f'midnight 00:0{st}'
    elif t<60:
        time = f'midnight 00:{st}'
    elif t < 100:
        valid = False
    # now t is in [100,2359]
    # case 1 t in [100,999]
    elif len(st) == 3:
        h,m = st[0],st[1:]
        if int(m) > 59:
            valid = False
        else:
            time = f'{h}:{m} am'
    # case 2 t i n[1000,2359]
    elif len(st) == 4:
        h,m = int(st[:2]), st[2:]
        if int(m) > 59:
            valid = False
        elif h < 13:
            time = f'{h}:{m} am'
        else:
            time = f'{h-12}:{m} pm'
    else:
        valid = False
    return [valid,time]

def mytimeinput(question_data, showhelp,showmarks,_standardf):
    title = question_data["title"]
    helptext = question_data["helptext"]
    
    if showhelp:
        value = st.number_input(title, min_value=0, max_value=2359, help=helptext)
    else:
        value = st.number_input(title, min_value=0, max_value=2359)
    if not value:
        st.caption(":red[Cannot be blank]")
        return -1
    else:
        valid,displaytime = verify_time(value)
        if not valid:
            st.caption("Invalid time input")
            st.caption("Put in 24 h format lik 1830 for 6:30 pm")
            return -1
        else:
            marks = global_slookup(question_data['key'],value,_standardf)
            if showmarks:
                st.caption(f"{displaytime} -- {marks}")
            else:
                st.caption(f"{displaytime}")
            return value

def display_weekly_filling(weekdf):
    batch = ['on_time','sa','morning_class','mangal_aarti','japa_time']
    dfdisplay = weekdf[batch]
    dfdisplay.columns = dfdisplay.columns.str.replace("_"," ").str.title()
    st.data_editor(dfdisplay,disabled=True)
    
    batch = ['sp_books','about_sp','hearing_sp','hearing_hhrnsm','hearing_hgrsp','hearing_councellor','hearing_other']
    dfdisplay = weekdf[batch]
    dfdisplay.columns = [i.replace("hearing_",'').replace('_'," ").upper() for i in dfdisplay.columns]
    st.data_editor(dfdisplay,disabled=True)
    
    batch = ['shloka','shayan_kirtan','wake_up','to_bed','day_rest','pc','fsc']
    dfdisplay = weekdf[batch]
    dfdisplay.columns = [i.replace('_'," ").upper() for i in dfdisplay.columns]
    st.data_editor(dfdisplay,disabled=True)
    st.markdown(f"##### :gray[birds eye view]")
    st.markdown(f"""* :gray[Srila Prabhupada:] :orange[{weekdf['hearing_sp'].sum()} min]""")
    st.markdown(f"* :gray[HH Radhanath Swami Maharaj:] :orange[{weekdf['hearing_hhrnsm'].sum()} min]")
    st.markdown(f"* :gray[HG Radheshyam Pr:] :orange[{weekdf['hearing_hgrsp'].sum()} min]")
    st.markdown(f"* :gray[Reading SP books: ] :orange[{weekdf['sp_books'].sum()} min]")
    st.markdown(f"* :gray[About SP: ] :orange[{weekdf['about_sp'].sum()} min]")
    st.markdown(f"* :gray[Shloka:] :orange[{weekdf['shloka'].sum()}]")
    st.markdown(f"* :gray[Total Day rest:] :orange[{weekdf['day_rest'].sum()} min]")

def display_group_all_summary(week_data_dict,filling_summary_dict,display_key):
    """
    input: data of a week in dictionary format
    output: displays"""
    # display the filling summary first
    fillingdf = pd.DataFrame.from_dict(filling_summary_dict,orient='index')
    fillingdf.index = fillingdf.index + " Pr"
    fillingdf.columns = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    
    def color_true_green_false_red(val):
        # color = 'green' if val else 'red'
        color = '#87ad7d' if val else '#e0a596'  # Green: #00FF00, Red: #FF0000        
        return f"background-color: {color}"

    # Apply style to DataFrame
    st.markdown("#### :gray[Sadhana Card filling summary]")
    st.data_editor(fillingdf.style.applymap(color_true_green_false_red),disabled=True,key=display_key+"_fill_table")

    fillingdf['total'] = fillingdf.astype('int').sum(axis=1)
    filled_7days = ":green[, ]".join([f":green[{i}]" for i in fillingdf.query("total==7").index.tolist()])
    filled_01days = ":red[, ]".join([f":green[{i}]" for i in fillingdf.query("total<2").index.tolist()])
    st.markdown(f"#### :green[Filled 7 days:] {filled_7days}")
    st.markdown(f"#### :red[Filled at max one day:] {filled_01days}")
    
    #---------------------------------------------------
    alddf = pd.DataFrame.from_dict(week_data_dict,orient='index')
    scorecard = st.empty()
    st.markdown("### Toppers")
    for i in ['Japa','Reading','Hearing','Total']:
        _topper = alddf.at[alddf[i].idxmax(),'Name']
        _value = alddf.loc[alddf['Name']==_topper,i].tolist()[0]
        if _value < 1:
            _value = f'{int(_value * 100)} %'
        st.markdown(f"#### {i}: :green[{_topper}] ({_value})")
    
    percentcols = ['Japa','Body','Soul','Total','To Bed','Wake Up','Day Rest']
    alddf[percentcols] = alddf[percentcols]*100        
    mycolumn_config = {col:st.column_config.NumberColumn(col,format="%.0f %%") for col in percentcols}
    
    mycolumn_config = {**mycolumn_config,
                        'Reading':st.column_config.NumberColumn("Reading",format="%.0f min"),
                        'Hearing':st.column_config.NumberColumn("Hearing",format="%.0f min"),
                        'Days filled':st.column_config.NumberColumn("days filled",format="%.0f days"),
                        }
    
    alddf.index = alddf['Name']
    with scorecard.container():
        st.markdown("#### :gray[Sadhana Card Summary]")
        st.data_editor(alddf.drop(columns='Name'),
                    disabled=True,
                    column_config=mycolumn_config,
                    key=display_key+"score_table",)

def daily_filling(qnadict, show_help_text,_show_marks,_standard_database):

    _standard_dict = _standard_database['dict']
    _standard_df = _standard_database['df']
    
    result = {}
    incomplete = False
    # morning program
    st.markdown("#### :violet[Morning Program]")
    cols = st.columns(4)
    for i, item in enumerate(["on_time", "sa", "morning_class", "mangal_aarti"]):
        with cols[i]:
            result[item] = mycheckbox(qnadict[item], show_help_text,_show_marks,_standard_dict)

    result["japa_time"] = mytimeinput(qnadict["japa_time"], show_help_text,_show_marks,_standard_df)

    # reading
    st.markdown(":violet[Reading]")
    left, right = st.columns(2)
    with left:
        result["sp_books"] = mynuminput(qnadict["sp_books"], show_help_text)
    with right:
        result["about_sp"] = mynuminput(qnadict["about_sp"], show_help_text)
    
    # hearing
    st.markdown("#### :violet[Hearing]")
    left, middle, right = st.columns(3)
    with left:
        result["hearing_sp"] = mynuminput(qnadict["hearing_sp"], show_help_text)

    with middle:
        result["hearing_hhrnsm"] = mynuminput(
            qnadict["hearing_hhrnsm"], show_help_text
        )
        result["hearing_hgrsp"] = mynuminput(
            qnadict["hearing_hgrsp"], show_help_text
        )

    with right:
        result["hearing_councellor"] = mynuminput(
            qnadict["hearing_councellor"], show_help_text
        )
        result["hearing_other"] = mynuminput(
            qnadict["hearing_other"], show_help_text
        )

    # shloka
    result["shloka"] = st.radio(
        qnadict["shloka"]["title"], options=[0, 1, 2, 3], horizontal=True
    )
    result["shayan_kirtan"] = mycheckbox(qnadict["shayan_kirtan"], show_help_text,False,_standard_dict)

    # body
    st.markdown("#### :violet[Shayan]")
    columns = st.columns(3)
    with columns[0]:
        result["wake_up"] = mytimeinput(qnadict["wake_up"], show_help_text,_show_marks,_standard_df)
    with columns[1]:
        result["to_bed"] = mytimeinput(qnadict["to_bed"], show_help_text,_show_marks,_standard_df)
    with columns[2]:
        result["day_rest"] = mynuminput(qnadict["day_rest"], show_help_text,_show_marks,_standard_df)

    st.divider()
    left, right = st.columns(2)
    with left:
        result["pc"] = mycheckbox(qnadict["pc"], show_help_text,_show_marks,_standard_dict)
    with right:
        result["fsc"] = mycheckbox(qnadict["fsc"], show_help_text,_show_marks,_standard_dict)

    required_columns = ["japa_time", "wake_up", "to_bed"]
    for column in required_columns:
        if result[column] == -1:
            incomplete = True
            st.caption(f"Prabhuji you have not filled :red[{column.replace('_',' ')}]")
            break
    return incomplete, result

def evaluate_weekly_summary(weekdata, standard):
    """function to evaluate weekly summary of the sadhana card.
    Args:
        weekdata (json): {day:{key:value, key1:value}}
        standard (standarddb): {'df':lt3hdf,
                                'dict':lt3hdict}
    returns
        summary in dict {'all':dict,
                        'summary':dict
                        }
    """
    dfstd = standard["df"]
    dictstd = standard["dict"]

    scorepercent = {}
    # Convert weekdata into dataframe
    weekdf = pd.DataFrame.from_dict(weekdata, orient="index").reset_index(drop=True)
    # convert data_types etc
    numeric_columns = [
        "japa_time",
        "sp_books",
        "about_sp",
        "hearing_sp",
        "hearing_hhrnsm",
        "hearing_hgrsp",
        "hearing_councellor",
        "hearing_other",
        "shloka",
        # "seva_number",
        "wake_up",
        "to_bed",
        "day_rest",
    ]
    checkbox_columns = [
        "on_time",
        "sa",
        "morning_class",
        "mangal_aarti",
        "shayan_kirtan",
        # 'seva_text',
        "pc",
        "fsc",
    ]

    weekdf[numeric_columns] = weekdf[numeric_columns].astype('float')
    weekdf[checkbox_columns] = weekdf[checkbox_columns].astype('float')

    # on time, Sa, MA, MC
    def mpscore(row):
        """ "Get the row and ontime, sa, mc, ma"""
        # we have done as_type ('float')
        # so it is 1 or 0 for True and False
        return pd.Series([
                dictstd[i]["mark"] if row[i] else 0
                for i in ["on_time", "sa", "morning_class", "mangal_aarti",'pc','fsc']
            ],dtype='float')
        
    # st.dataframe(weekdf)
    weekdf[['on_time','sa','morning_class','mangal_aarti','pc','fsc']] = weekdf.apply(mpscore, axis=1)
    # st.write(a)
    # print(a)
    
    scorepercent["on_time"] = {"score": weekdf['on_time'].sum(), 
                               "maxs": 7*dictstd["on_time"]["mark"]}
    scorepercent["sa"] = {"score": weekdf['sa'].sum(), 
                          "maxs": 7*dictstd["sa"]["mark"]}
    scorepercent["morning_class"] = {
        "score": weekdf['morning_class'].sum(),
        "maxs": 7*dictstd["morning_class"]["mark"],
    }
    scorepercent["mangal_aarti"] = {
        "score": weekdf['mangal_aarti'].sum(),
        "maxs": 7*dictstd["mangal_aarti"]["mark"],
    }
    
    # personal cleanliness and filling sadhana card
    scorepercent["pc"] = {
        "score": weekdf['pc'].sum(),
        "maxs": 7*dictstd["pc"]["mark"],
    }
    scorepercent["fsc"] = {
        "score": weekdf['fsc'].sum(),
        "maxs": 7*dictstd["fsc"]["mark"],
    }



    # reading
    for i in ["sp_books", "about_sp"]:
        scorepercent[i] = {"value": weekdf[i].sum(), "maxs": dictstd[i]["mark"]}
        scorepercent[i]["score"] = scorepercent[i]["maxs"] * min(
            1, scorepercent[i]["value"] / dictstd[i]["value"]
        )

    # hearing scores
    for i in ["hearing_sp", "hearing_hhrnsm", "hearing_hgrsp", "hearing_councellor"]:
        scorepercent[i] = {"value": weekdf[i].sum(),"maxs": dictstd[i]["mark"]}
        scorepercent[i]["score"] = scorepercent[i]["maxs"] * min(
            1, scorepercent[i]["value"] / dictstd[i]["value"]
        )
    scorepercent["hearing_other"] = {"value": weekdf["hearing_other"].sum()}
    
    
    # Shloka
    scorepercent["shloka"] = {"value": weekdf["shloka"].sum(), 
                              "maxs": dictstd["shloka"]["mark"]}
    scorepercent["shloka"]["score"] = scorepercent["shloka"]["maxs"] * \
        min(1,scorepercent["shloka"]["value"] / dictstd["shloka"]["value"])
    

    # Shayan kirtan
    scorepercent['shayan_kirtan'] = {"value": weekdf["shayan_kirtan"].sum()}
    
    
    def slookup(name,value):
        sdf = dfstd.query(f"name == '{name}'").copy()
        sdf[['value','mark']] = sdf[['value','mark']].astype('float')
        sdf.sort_values(by=['value'],ascending=True, inplace=True)        
        for _, row in sdf.iterrows():
            if value <= row['value']:
                return row['mark']
    
    # now evaluate the time bound things
    for i in ["japa_time", "wake_up", "to_bed",'day_rest']:
        score = sum([slookup(i,e) for e in  weekdf[i].tolist()])
        scorepercent[i] = {"score": score, "maxs": 7*dictstd[f"_{i}"]["mark"]}
    
    # --- prepare the summary report
    summary = {}
    # Body percent
    body = []
    for i in ["wake_up", "to_bed", "day_rest",'pc','fsc']:
        scorepercent[i]['%'] = round(scorepercent[i]["score"] / scorepercent[i]["maxs"],2)
        body.append(scorepercent[i]['%'])
    
    # soul percent
    soul = []
    for i in ['on_time','sa','morning_class','mangal_aarti',
              'sp_books','about_sp','japa_time',
              'hearing_sp','hearing_hhrnsm','hearing_hgrsp','hearing_councellor',
              'shloka']:
        scorepercent[i]['%'] = round(scorepercent[i]["score"] / scorepercent[i]["maxs"],2)
        soul.append(scorepercent[i]['%'])
    
    summary = {}
    summary['reading'] = {'target':dictstd['total_reading']['value'],
                          'achieved':scorepercent['sp_books']['value']+scorepercent['about_sp']['value']}
    summary['hearing'] = {'target':dictstd['total_hearing']['value'],
                          'achieved':scorepercent['hearing_sp']['value']
                                    +scorepercent['hearing_hhrnsm']['value']
                                    +scorepercent['hearing_hgrsp']['value']
                                    +scorepercent['hearing_councellor']['value']
                                    + scorepercent['hearing_other']['value']}
    
    summary['shloka'] = {'target':dictstd['shloka']['value'],'achieved':scorepercent["shloka"]['value']}
    summary['body'] = {'achieved':sum(body)/len(body)}
    summary['soul'] = {'achieved':sum(soul)/len(soul)}
    summary['filled_days'] = {"achieved":len(weekdf)}
    summary['total'] = {"achieved":round((summary['body']['achieved'] + summary['soul']['achieved'])/2,2)}
    # print(summary['hearing']['achieved'])
    return {
            "all":scorepercent,
            'summary':summary
            }

def extract_week_summary(name,wd):
    """
    """
    summary  =  {}
    summary['Name'] = f"{name} Pr"
    summary['Body'] = wd['summary']['body']['achieved']
    summary['Soul'] = wd['summary']['soul']['achieved']
    summary['Total'] = wd['summary']['total']['achieved']

    summary['To Bed'] = wd['all']['to_bed']['%']
    summary['Wake Up'] = wd['all']['wake_up']['%']
    summary['Day Rest'] = wd['all']['day_rest']['%']
    summary['Japa'] = wd['all']['japa_time']['%']

    summary['Reading'] = wd['summary']['reading']['achieved']
    summary['Hearing'] = wd['summary']['hearing']['achieved']
    summary['Days filled'] = wd['summary']['filled_days']['achieved']
    
    return summary