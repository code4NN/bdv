import streamlit as st
# from other_pages.hearing_tracker import VANI_hearing_class as class_under_development
from other_pages.song_shloka import shlokaloka as class_under_development

def process_query_parameters(app,qdict):
    """
    options for keys
    * mode(guest,user),user(username), pass(password)
    * keepQuery (yes,no)
    * target
    """
    usertype = qdict.get('mode', 'guest')
    target = qdict.get("target",'login')
    
    updated_qdict = {k:v for k,v in qdict.items()}
    
    # for development this query params will keep processing
    # for production only once this function is called
    app.handled_query_params = True if target !='dev' else False
    
    
    
    # login handler for all pages
    # regarless of anything else
    # user : clears the mode, user, pass
    if usertype =='user':
        username = qdict.get('user')
        password = qdict.get('pass')
        login_class = app.page_map['login']
        _login_response_code = login_class.perform_login(username, password,'ask')
        correct_credentials = 2 == _login_response_code
        
        if correct_credentials:
            login_class.perform_login(username, password, 'submit')
        updated_qdict.pop('user', None)
        updated_qdict.pop('pass', None)
        updated_qdict.pop('mode', None)

    
    if target == 'dev':
        page = qdict['page']
        subpage = qdict.get('subpage','blank')
        refresh = qdict.get('refresh','yes')
        
        # if refresh, create a fresh instance of the class
        if refresh == 'yes':
            newpage = class_under_development()
            # update subpage if available
            app.page_map[page] = newpage
        
        # update the bdv app
        app.current_page = page
    
    
    elif target =='hear_vani':
        app.current_page = 'vani_hearing'
        
        lecture_id = qdict.get("id")
        
        vani_class = app.page_map['vani_hearing']
        vani_class.page_map['active'] = 'hearnow'
        vani_class.page_hearnow['status'] = 'pending'
        vani_class.page_hearnow['id'] = lecture_id
            
    
    elif target=='vani':
        # user must have already logged in by the url
        # if not they will be triggered by the vani app
        app.current_page = 'vani_hearing'

    # for updating query parameters
    # update only if keepQuery parameter is either "no" or absent
    if qdict.get("keepQuery",'no') == 'no':
        st.query_params.clear()
        st.query_params.from_dict(updated_qdict)