import streamlit as st
from openai import OpenAI
from langchain.graphs import Neo4jGraph
import os
from langchain.vectorstores.neo4j_vector import Neo4jVector
from langchain.embeddings.openai import OpenAIEmbeddings
from neo4j import GraphDatabase
import re
from utils import questionA
from langchain.graphs import Neo4jGraph
from tqdm import tqdm
from neo4j import GraphDatabase

os.environ['OPENAI_API_KEY'] = ""

url = "bolt://localhost:7687"  # Replace with your Neo4j server URI
username = ""
password = ""
db1_name = ''
db2_name = ''

driver = GraphDatabase.driver(url, auth=(username, password))
client = OpenAI()


vector_index = Neo4jVector.from_existing_graph(
    OpenAIEmbeddings(),
    url=url,
    username=username,
    password=password,
    index_name='tasks',
    node_label="Content",
    text_node_properties=['contenu'],
    embedding_node_property='embedding',
)

st.title("CHatbot Expert in medical questions")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask a question:"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

# Display assistant response in chat message container
    with st.chat_message("assistant"):
        # Generate text
        output = questionA(client, vector_index, driver, db1_name, db2_name, prompt)
        response = st.write(output)
        st.session_state.messages.append({"role": "assistant", "content": output})
