import streamlit as st
import pandas as pd

def mycheckbox(question_data, showhelp):
    title = question_data["title"]
    helptext = question_data["helptext"]

    if not showhelp:
        return st.checkbox(label=title, value=False)
    else:
        return st.checkbox(label=title, help=helptext, value=False)

def mynuminput(question_data, showhelp):
    title = question_data["title"]
    lower_limit = int(question_data["min"])
    upper_limit = question_data["max"]
    helptext = question_data["helptext"]
    if showhelp:
        value = st.number_input(title, min_value=lower_limit, help=helptext, step=1)
    else:
        value = st.number_input(title, min_value=lower_limit, step=1)
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

def mytimeinput(question_data, showhelp):
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
            st.caption(displaytime)
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

def daily_filling(qnadict, show_help_text=False):

    result = {}
    incomplete = False
    # morning program
    with st.expander("Morning Program", expanded=True):
        cols = st.columns(4)
        for i, item in enumerate(["on_time", "sa", "morning_class", "mangal_aarti"]):
            with cols[i]:
                result[item] = mycheckbox(qnadict[item], show_help_text)

    result["japa_time"] = mytimeinput(qnadict["japa_time"], show_help_text)

    # reading
    with st.expander("Reading", expanded=True):
        left, right = st.columns(2)
        with left:
            result["sp_books"] = mynuminput(qnadict["sp_books"], show_help_text)
        with right:
            result["about_sp"] = mynuminput(qnadict["about_sp"], show_help_text)
    # hearing
    with st.expander("Hearing", expanded=True):
        left, middle, right = st.columns(3)
        with left:
            result["hearing_sp"] = mynuminput(qnadict["hearing_sp"], show_help_text)
            result["hearing_councellor"] = mynuminput(
                qnadict["hearing_councellor"], show_help_text
            )

        with middle:
            result["hearing_hhrnsm"] = mynuminput(
                qnadict["hearing_hhrnsm"], show_help_text
            )
            result["hearing_other"] = mynuminput(
                qnadict["hearing_other"], show_help_text
            )

        with right:
            result["hearing_hgrsp"] = mynuminput(
                qnadict["hearing_hgrsp"], show_help_text
            )
    # shloka
    result["shloka"] = st.radio(
        qnadict["shloka"]["title"], options=[0, 1, 2, 3], horizontal=True
    )
    result["shayan_kirtan"] = mycheckbox(qnadict["shayan_kirtan"], show_help_text)

    # body
    with st.expander("Shayan", expanded=True):
        columns = st.columns(3)
        with columns[0]:
            result["wake_up"] = mytimeinput(qnadict["wake_up"], show_help_text)
        with columns[1]:
            result["to_bed"] = mytimeinput(qnadict["to_bed"], show_help_text)
        with columns[2]:
            result["day_rest"] = mynuminput(qnadict["day_rest"], show_help_text)

    with st.expander("", expanded=True):
        left, right = st.columns(2)
        with left:
            result["pc"] = mycheckbox(qnadict["pc"], show_help_text)
        with right:
            result["fsc"] = mycheckbox(qnadict["fsc"], show_help_text)

    required_columns = ["japa_time", "wake_up", "to_bed"]
    for column in required_columns:
        if result[column] == -1:
            incomplete = True
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
        ontime, sa, mc, ma = (
            row["on_time"],
            row["sa"],
            row["morning_class"],
            row["mangal_aarti"]
        )
        if ontime * sa * ma * mc == 1:
            fullmark = dictstd["full_mp"]["mark"] / 4
            return pd.Series([fullmark, fullmark, fullmark, fullmark],dtype='float')
        else:
            return pd.Series([
                dictstd[i]["mark"]
                for i in ["on_time", "sa", "morning_class", "mangal_aarti"]
            ],dtype='float')
    st.dataframe(weekdf)
    weekdf[['on_time','sa','morning_class','mangal_aarti']] = weekdf.apply(mpscore, axis=1)
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



    # reading
    for i in ["sp_books", "about_sp"]:
        scorepercent[i] = {"value": weekdf[i].sum(), "maxs": dictstd[i]["mark"]}
        scorepercent[i]["score"] = scorepercent[i]["maxs"] * min(
            1, scorepercent[i]["value"] / dictstd[i]["value"]
        )

    # hearing scores
    for i in ["hearing_sp", "hearing_hhrnsm", "hearing_hgrsp", "hearing_councellor"]:
        scorepercent[i] = {"value": weekdf[i].sum(),"maxs": dictstd[i]["mark"],}
        scorepercent[i]["score"] = scorepercent[i]["maxs"] * min(
            1, scorepercent[i]["value"] / dictstd[i]["value"]
        )
    scorepercent["hearing_other"] = {"value": weekdf["hearing_other"].sum(),}
    
    
    # Shloka
    scorepercent["shloka"] = {"value": weekdf["shloka"].sum(), 
                              "maxs": dictstd["shloka"]["mark"]}
    scorepercent["shloka"]["score"] = scorepercent["shloka"]["maxs"] * \
        min(1,scorepercent["shloka"]["value"] / dictstd["shloka"]["value"])
    
    
    # personal cleanliness, filling sadhana card
    for i in ["pc", "fsc"]:
        scorepercent[i] = {"value": weekdf[i].sum(), "maxs": 7*dictstd[i]["mark"]}
        scorepercent[i]["score"] = (scorepercent[i]["maxs"]*scorepercent[i]['value'])/7


    # Shayan kirtan
    scorepercent['shayan_kirtan'] = {"value": weekdf["shayan_kirtan"].sum()}
    def slookup(name,value):
        sdf = dfstd.query(f"name == '{name}'").copy()
        sdf[['value','mark']] = sdf[['value','mark']].astype('float')
        sdf.sort_values(by=['value'],inplace=True)
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
    print(summary['hearing']['achieved'])
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