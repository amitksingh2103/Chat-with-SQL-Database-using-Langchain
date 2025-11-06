import streamlit as st
from pathlib import Path
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_community.agent_toolkits.sql.base import SQLDatabaseToolkit 
from sqlalchemy import create_engine
import sqlite3
from langchain_groq import ChatGroq
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv

SQLDatabaseToolkit.model_rebuild()
load_dotenv() 

st.title("Langchain: Chat with SQL Database")

LOCALDB='USE_LOCALDB'
MYSQLDB='USE_MYSQL'

radio_option=['Use SQLite3 Database(student.db)','Connect To MySQL Database']

selected_option=st.sidebar.radio("Choose the DB you want to chat with",options=radio_option)

if selected_option=='Connect To MySQL Database':
    db_uri=MYSQLDB
    mysql_host=st.sidebar.text_input("Provide MySQL Hostname",value="localhost")
    mysql_user=st.sidebar.text_input("Provide MySQL Username",value='root')
    mysql_password=st.sidebar.text_input("Provide MySQL Password",type='password')
    mysql_db=st.sidebar.text_input("Provide MySQL Database Name")

else:
    db_uri=LOCALDB

groq_api=st.sidebar.text_input("Provide with the Groq API Key:",type='password')

if not groq_api:
    st.info("Please Provide your Groq API Key to continue")
    st.stop()

model=ChatGroq(model='llama-3.3-70b-versatile',groq_api_key=groq_api,streaming=True)

@st.cache_resource(ttl=7200)
def configure_db(db_uri,mysql_host=None,mysql_user=None,mysql_password=None,mysql_db=None):
    if db_uri==LOCALDB:
        dbfilepath=(Path(__file__).parent/"student.db").absolute()
        creator=lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro",uri=True)
        return SQLDatabase(create_engine("sqlite:///",creator=creator))

    elif db_uri==MYSQLDB:
        if not(mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please Provide all MySQL connection Details")
            st.stop()  
        
        encoded_password=quote_plus(mysql_password)
        connection_str=f"mysql+mysqlconnector://{mysql_user}:{encoded_password}@{mysql_host}/{mysql_db}"

        try:
            db=SQLDatabase(create_engine(connection_str))
            st.success("Successfully Connected To MYSQL Database !")
            return db

        except Exception as e:
            st.error(f"Failed to connect to Mysql:{e}")
            st.stop()

if db_uri==MYSQLDB:
    db=configure_db(db_uri,mysql_host,mysql_user,mysql_password,mysql_db)
else:
    db=configure_db(db_uri)

toolkit=SQLDatabaseToolkit(db=db,llm=model)

agent = create_sql_agent(llm=model, toolkit=toolkit, verbose=True,agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,)

if "messages" not in st.session_state or st.sidebar.button("clear message history"):
    st.session_state['messages']=[{"role":"Assistant","content":"How can I help you ?"}]
    
    for msg in st.session_state['messages']:
        st.chat_message(msg['role']).write(msg['content'])

user_query=st.chat_input(placeholder='Ask anything from the database...')

if user_query:
    st.session_state['messages'].append({'role':'user','content':user_query})
    st.chat_message('user').write(user_query)

    with st.chat_message("Assistant"):
        streamlit_callback=StreamlitCallbackHandler(st.container())
        response=agent.run(user_query,callbacks=[streamlit_callback])
        st.session_state['messages'].append({'role':'Assistant','content':response})
        st.write(response)