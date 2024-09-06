import streamlit as st
# from other_pages.hearing_tracker import VANI_hearing_class as class_under_development
from other_pages.hearing_tracker import SP_hearing_Class as class_under_development

def process_query_parameters(app,qdict):
    """
    options for keys
    * mode(guest,user),user(username), pass(password)
    * target
    """
    usertype = qdict.get('mode', 'guest')
    target = qdict.get("target",'login')
    
    updated_qdict = qdict.copy()
    
    # for development this query params will keep processing
    # for production only once this function is called
    app.handled_query_params = True if target !='dev' else False
    
    
    
    # login handler for all pages
    # regarless of anything else
    if usertype == 'user':
        username = qdict.get('user')
        password = qdict.get('pass')
        login_class = app.page_map['login']
        correct_credentials = 2 ==login_class.perform_login(username, password,'ask')
        
        if correct_credentials:            
            login_class.perform_login(username, password, 'submit')
        updated_qdict.pop('user', None)
        updated_qdict.pop('pass', None)

    
    if target == 'dev':
        page = qdict['page']
        loginmode = qdict['mode'] # guest or user
        subpage = qdict.get('subpage','blank')
        refresh = qdict.get('refresh','yes')
        
        # login if login_mode is user
        if loginmode == 'user':
            username = qdict.get('username','Shiven')
            password = qdict.get('pass','mindit')
            
            app.scriptcial_login(username,password)
            
        
        # if refresh, create a fresh instance of the class
        if refresh == 'yes':
            newpage = class_under_development()
            # update subpage if available
            if subpage != 'blank':
                newpage.current_page = subpage
            app.page_map[page] = newpage        
        
        # update the bdv app
        app.current_page = page
        app.in_development = True
    
    # for productions we will have one of the following
    # elif target =='login':
    #     # login page
    #     username = qdict.get('user',"")
    #     password = qdict.get('pass','')
        
    #     app.scriptcial_login(username,password)
    
    elif target =='hear_now_vani':
        if usertype =='guest':
            app.current_page = 'login'
        # source = qdict.get("source")
        # lecture_id = qdict.get("id")
        # redirect_mode = qdict.get("mode",'guest')
        
        # if redirect_mode=='user':
        #     username = qdict.get('user')
        #     password = qdict.get('pass')
            
        # if source == 'sp_sindhu':
        #     app.current_page = 'sp_hearing'
        #     player = app.page_map['sp_hearing']
            
        #     # get lecture name
        #     lec_info = player.sp_sindhu_df.query(f"encrypt_id == '{lecture_id}'")
        #     lec_name = lec_info.name.tolist()[0]
        #     full_name = lec_info.full_name.tolist()[0]
        #     mega_id = lec_info.mega_id.tolist()[0]
        #     sp_id = lec_info['id'].tolist()[0]
            
        #     player.page_config = {'page_title': lec_name,
        #                         'page_icon':'🎧',
        #                         'layout':'wide'}
            
        #     player.current_page = 'SP_lec_player'
        #     player.play_now_info_dict = {'encrypt_id':lecture_id,
        #                                  'mega_id':mega_id,
        #                                  'sp_id':sp_id,
        #                                  'lecture_name':lec_name}
        #     st.rerun()
    
    
    
    
    
    # for updating query parameters
    st.query_params.clear()
    set.query_params.from_dict(updated_qdict)