import streamlit as st

# talk to google
from other_pages.googleapi import download_data,upload_data
import json
import pandas as pd
import pandas as pd


class login_Class:
    def __init__(self):
        
        # page map
        self.page_config = {'page_title': "Login Page",
                            'page_icon':'☔',
                            'layout':'centered'}
        self.page_map = {
            'active':'home',
            
            'home':self.home,
            'reg':self.registration
        }
                
        self.login_helper = {'center':'bdv',
                            'username':'',
                            'password':''}
        self.reg_helper = {'submission_status':'pending',#done
                           }


        # Sheets related informations
        self.USER_CREDENTIALS = 'creds_v2!A2:S'

        # User credentials
        self._creds_db = None
        self._creds_db_refresh = True

    @property
    def userdb(self):
        """
        * center_df, user_df,
        * voice_group_list
        * new_reg_row
        * user_pass_all_dict,user_pass_verified_dict
        """
        if self._creds_db_refresh:
            # refresh the data
            
            # this is 2D array
            raw_data = download_data(db_id=1,range_name=self.USER_CREDENTIALS)
            raw_df = pd.DataFrame(raw_data[1:], columns=raw_data[0])
            
            centre_columns = ['center_full_name',
                                'center_short_name',
                                'poc_name',
                                'poc_number']
            user_columns = ['db_row',
                            'center_name',
                            'username',
                            'full_username',
                            'password',
                            'full_name',
                            'phone_number',
                            'voice_group',
                            'councellor_name',
                            'verified',
                            
                            'global_roles',
                            'center_roles',
                            
                            'vani_syllabus_status']
            center_df = raw_df[centre_columns].query("center_full_name!=''").copy(deep=True)
            user_df = raw_df[user_columns].query("center_name!=''").copy(deep=True)
            verified_user_df = user_df.query("verified=='yes'").copy(deep=True)
            
            voice_group_list = raw_df[['voice_group_list']].query("voice_group_list!=''")['voice_group'].tolist()
            new_reg_row = raw_df[['new_registrations']].query("new_registrations!=''")['new_registrations'].tolist()[0]
            
            # save
            self._creds_db = {
                'center_df':center_df,
                'user_df':user_df,
                
                'voice_group_list':voice_group_list,
                'new_reg_row':new_reg_row,
                
                'user_pass_all_dict':dict(zip(user_df['full_username'],
                                         user_df['password'])),                
                'user_pass_verified_dict':dict(zip(verified_user_df['full_username'],
                                              verified_user_df['password'])),
                'center_dict':dict(zip(center_df['center_short_name'],
                                       center_df['center_full_name']))
            }
            # set refresh to false
            self._userdb_refresh = False
            
        return self._creds_db

    @property
    def bdvapp(self):
        return st.session_state.get("bdv_app",None)
    
    def perform_login(self,username,password,callmode):
        """
        * perform following if callmode=submit
        * update self.userinfo
        * update self._userdb['dfself']
        * update self.sp_sindhu_df
        
        * if callmode = ask
        * returns 
        * 0 for pending username
        * -1 for invalid username
        * 1 for wrong password
        * 2 if valid username and password
        """
        _user_is_valid = None
        _password_is_correct = 0
        _userinfo = None
        
        if username in self.userdb['user_pass_verified_dict'].keys():
            _user_is_valid = 1
            if password == self.userdb['user_pass_verified_dict'][username]:
                _password_is_correct = 2
                # _userinfo = define the dictionary
                _userinfo = self.userdb['user_df']\
                .query(f"full_username =='{username}' ")\
                .reset_index(drop=True).to_dict(orient='index')[0]

        elif username in self.userdb['user_pass_all_dict'].keys():
            _user_is_valid = 0
        else :
            _user_is_valid = -1
        
        if callmode == 'ask':
            return _user_is_valid + _password_is_correct
        elif callable =='submit':
            # perform login action
            if _user_is_valid + _password_is_correct == 2:
                self.bdvapp.userinfo = _userinfo                                        
    
    def home(self):
        
        login_container = st.empty()
        with login_container.container():
            st.header(":green[Please Login to Continue]")
            
            st.button('Barasana Dhaam VOICE',
                      on_click=lambda x: self.login_helper.__setitem__('group',x),
                      args=['bdv'],
                      type="primary" if self.login_helper['group'] == 'bdv' else "secondary",
                      key='center_name_btn'
            )
            
            input_user_name = st.text_input("Enter Username",
                                            key='username_input_text',
                                            value=self.login_helper['username'],
                                            ).strip()
            
            input_user_name = f"{self.login_helper['center']}_{input_user_name}"
            
            input_password = st.text_input("Enter Password",
                                            type='password',
                                            value=self.login_helper['password'],
                                            key='password_input_text').strip()
        
        ## Verify username and password
        login_response = self.perform_login(input_user_name,input_password,'ask')
        
        if login_response==-1:
            st.caption(":red[no user found 😐!!]")
            
        elif login_response == 0:
            st.info("Your registration is pending!!")
            
        elif login_response ==1:
            st.caption(":red[Incorrect Password!!]")
        elif login_response ==2:
            
                login_container.empty()
                with login_container.container():
                    st.header(":rainbow[Jai!! You have logged in]")
                    st.image("./other_pages/images/SSNN_blue.png")
                
                def switch_to_page(username,password,):
                    self
                
                # # for all devotees of HG PrGP
                # if 'hgprgp_councelle' in self.bdvapp.userinfo['group']:
                #     st.markdown('#### :green[Kindly Choose the seva]')
                #     st.button("Sadhana Card",on_click=takemein,args=['sadhana_card'])
                
                
                
                # # for voice Devotees
                # if 'bdv' in self.bdvapp.userinfo['group']:
                #     st.markdown('#### :green[How may I serve you?]')
                #     left,middle,right = st.columns(3)
                #     with left:
                #         st.button('Settlements 💸',on_click=takemein,args=['settlement'],key='direct_login_settlement')
                    
                #     with middle:
                #         st.button("Finder 🔍",on_click=takemein,args=['finder'],key='direct_login_finder')
                    
                #     with right:
                #         # st.write(user_roles)
                #         st.button("Class Notes",on_click=takemein,args=['revision'],key='direct_login_revision')
                #         if 'acc_ic' in self.bdvapp.userinfo['roles']:
                #             st.button("Accounts 📝",on_click=takemein,args=['dpt_accounts'],key='direct_login_accounts')
                
                
                
                # # just for developer
                # if self.bdvapp.userinfo['username'] == 'Shiven':
                #     st.markdown("#### :orange[Services in progress]")
                #     st.button("Article_tagging",on_click=takemein,args=['article_tag'])
                #     st.button("Shloka and Songs",on_click=takemein,args=['ssong'])
                #     st.button("Hearing Tracker",on_click=takemein,args=['sp_hearing'])
        
        else :
            pass
        #----------------------------------------
        st.button("New Registration",
                  on_click=lambda x: self.login_helper.__setitem__('active', x),
                  args=['reg'],
                  type="primary",
                  key='new registration button')
        

    def registration(self):
        
        st.markdown(":rainbow[Hare Krishna]")
        if self.reg_helper['submission_status']=='done':
            st.success("You have successfully registered")
            return
        # steps. 1. fill the form, 2. center admin approves, 3. success
        center_name = st.radio("Select Center",
                               options=self.userdb['center_dict'].keys(),
                               horizontal=True,
                               format_func=lambda x: self.userdb['center_dict'][x],
                               key='center_name_radio')
        
        group_name = st.radio("Select Group",
                               options=self.userdb['voice_group_list'],
                               index=1,
                               horizontal=True,
                               format_func=lambda x: x.title(),
                               key='group_name_radio')
        
        _valid_username = False
        _valid_password = False
        _valid_phone_number = False
        
        full_name = st.text_input("Enter first name (withour ys etc)",
                                  max_chars=10)
        if full_name:
            
            user_name = st.text_input("Enter a unique Username",
                                      max_chars=10).strip()
            
            if user_name:
                full_user_name = f"{center_name}_{user_name}"
                existing_username_list = self.userdb['user_df']['full_username'].tolist()
                
                if full_user_name in existing_username_list:
                    st.caption(":red[Username already exists!!]")
                    st.caption(f"someone at {self.userdb['center_dict'][center_name]} have taken this username")
                else:
                    st.caption(":green[All good!!]")
                    _valid_username = True
            
        if _valid_username:
            user_password = st.text_input("Enter Password",
                          type='password',
                          key='password_input',
                          max_chars=10,
                          ).strip()
            if user_password:
                if len(user_password)<4:
                    st.caption(":red[Password should be atleast 4 characters]")
                else:
                    st.caption(":green[All good!!]")
                    _valid_password = True
        
        if _valid_password:
            phone_number = st.number_input("Enter your Phone Number",
                            key='phone_number_input',
                            step=1)
            phone_number = str(phone_number)
            
            with st.popover("Why are we asking phone number"):
                st.markdown("1\. To protect against robotic attacks")
                st.markdown("2\. To have a unique id of user")
                st.markdown("2\. To connect with you if any problems 🤝")
            
            if phone_number:
                if len(phone_number) !=10:
                    st.error("Please enter 10 digit number")
                elif not all([i in '0123456789' for i in phone_number]):
                    st.error("Only Numbers are allowed")
                
                elif phone_number in self.userdb['user_df']['phone_number'].tolist():
                    st.error("A user already exists with this number")
                else:
                    st.caption(":green[All good!!]")
                    _valid_phone_number = True
        
        def reg_form_submit(form_dict):
            registration_column_order =['center_name',
                                        'username',
                                        'full_username',
                                        'password',
                                        'full_name',
                                        'phone_number',
                                        'voice_group',
                                        'councellor_name',
                                        'verified',
                                        'global_roles',
                                        'center_roles']
            upload_array = [form_dict[i] for i in registration_column_order]
            upload_array = [[str(i) for i in upload_array]]
            row_2_add = self.userdb['new_reg_row']
            upload_data(db_id=1,
                        range_name=f"creds_v2!H{row_2_add}:R{row_2_add}",
                        value=upload_array)
            self.reg_helper['submission_status'] = 'done'
            
            
        if _valid_phone_number:
            st.button("Submit",
                    on_click=reg_form_submit,
                    args=[{'center_name':center_name,
                            'username':user_name,
                            'full_username':full_user_name,
                            'password':user_password,
                            'full_name':full_name,
                            'phone_number':phone_number,
                            'voice_group':group_name,
                            'councellor_name':'',
                            'verified':'no',
                            'global_roles':'',
                            'center_roles':'',
                            }],
                    type="primary",
                    key='submit_button')
        
        
        st.divider()
        st.header("For the admins")
        if self.bdvapp.user_exists:
            # if 'admin' in self.bdvapp.userinfo['global_roles'] or \
                # 'admin' in self.bdvapp.userinfo['center_roles']:
            if 'admin' in self.bdvapp.userinfo['global_roles']:
                pending_df = self.userdb['user_df'].query("verified=='no'")
                if pending_df.shape[0]=0:
                    st.success("All registrations are approved")
                else:
                    st.header(f"{len(pending_df)} pending Registrations")
                    
                    for _, row in pending_df.iterrows():
                        st.markdown(f"## :green[{row['center_name']} -- :blue[{row['full_name']}]]")
                        with st.expander("show details"):
                            st.write(row.to_dict())
                            st.button("Approve",
                                    on_click=self.userdb['approve_user'],
                                    args=[row['full_username']],
                                    type="primary",
                                    key=f"approve_{row['full_username']}")
            
        
        
        
        
        
    def run(self):
        """
        main handler
        """
        self.page_map[self.current_page]()