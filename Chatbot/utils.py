from openai import OpenAI
from langchain.graphs import Neo4jGraph
import os
from langchain.vectorstores.neo4j_vector import Neo4jVector
from langchain.embeddings.openai import OpenAIEmbeddings
from neo4j import GraphDatabase
import re

def stringify_result(result):
    result_str = ""
    for record in result:
        for key in record.keys():
            result_str += f"{key}: {record[key]}\n"
    return result_str

def schema_extraction(driver, database_name):
    with driver.session(database = database_name) as session:
        schema_visualisation = session.run("call db.schema.visualization")
        rel_properties = session.run("call db.schema.relTypeProperties")
        node_properties = session.run("call db.schema.nodeTypeProperties")
        schema_visualisation = stringify_result(schema_visualisation)
        rel_properties = stringify_result(rel_properties)
        node_properties = stringify_result(node_properties)
        
        return schema_visualisation, rel_properties, node_properties


def questionAnswering(question, driver, database_name, client):
  ##EXTRACTION SCHEMA DU GRAPH
  schema_visualisation, rel_properties, node_properties = schema_extraction(driver, database_name)
  
  ##GENERATION DE LA REQUETE CYPHER
  query_result = ""
  assistant = "Here is the graph schema: " + str(schema_visualisation) + "\n Here is the properties of the relations of the graph: " + str(rel_properties) + "\n Here is the properties of the nodes of the graph:" + str(node_properties)
  prompt_template = """
    give me a cypher Query to response to this:
    Question: {}
    """.format(question)
  messages = [ {"role": "system", "content": "You are an expert in generating Cypher Query"},
            {"role": "user", "content": prompt_template},
            {"role": "assistant", "content": assistant}
            ]

  response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=messages,
    temperature=0
  )
  ##EXTRACTION DE LA REQUETE CYPHER DE LA REPONSE DE GPT

  contenu_entre_backticks = re.findall(r"```(.*?)```", str(response.choices[0].message.content), re.DOTALL)
  if contenu_entre_backticks:
    for i, contenu in enumerate(contenu_entre_backticks, start=1):

        contenu = contenu.replace("<-", "-").replace("->", "-")
        with driver.session(database = database_name) as session:
          query_result = query_result + stringify_result(session.run(contenu))
  else:
    contenu = response.choices[0].message.content.replace("<-", "-").replace("->", "-")
    with driver.session(database = database_name) as session:
      query_result =  stringify_result(session.run(contenu))
  ##GENERATION DE LA REPONSE A LA QUESTION
  assistant = "This is the result of the question: \n" + query_result + "\n"
  question2 =  assistant + "Generate a response to this question: " + question
  messages =  [{"role" : "system", "content" : "You are an expert in Answering generation using ONLY the given set of facts."},
              {"role": "user", "content": question2 }

              ]
  response = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=messages,
      temperature=0
  )
  return response.choices[0].message.content


def run_cypher_query(query, driver, database_name):
    with driver.session(database = database_name) as session:
      result = session.run(query)
      return list(result)


def voisin_reponses(question,vector_index, driver, database_name):
  response = vector_index.similarity_search(question)
  reponses = []
  for res in response:
      texte_recherche = res.page_content.split("contenu: ")[1]
      reponses.append(texte_recherche)
      cypher_query = f"MATCH (c:Content)-[:has_commun_entity]->(e:Content) WHERE c.contenu = '{texte_recherche}' RETURN DISTINCT e.contenu as contenu;"
      resultats = run_cypher_query(cypher_query, driver, database_name)
      for record in resultats[:10]:
          reponses.append(record["contenu"])
  return list(set(reponses))


def reponse_question(question,vector_index, client,driver, database_name):
  facts = voisin_reponses(question,vector_index, driver, database_name)
  assistant = "here's a set of facts: " + str(facts)
  prompt_template = """
    give me an answer to this question based only on the set of facts: {}.
    Some fo these facts may not contain information necessery to the answer, you can ignore them.
    Dont add information from your knowledge, if you dont have the information in the set of facts dont add answer from your own.
    """.format(question)

  messages = [
              {"role": "user", "content": prompt_template},
              {"role": "assistant", "content": assistant},
              ]

  response = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=messages,
      temperature=0
  )
  return response.choices[0].message.content


def questionA(client, vector_index, driver, database_name, database_name2, question):
  answer1 = questionAnswering(question, driver, database_name, client)
  answer2 = reponse_question(question,vector_index, client, driver, database_name2)

  question2 = "Generate a response to this question: "+ question+"\n Using the given set of facts: \n" + answer1 + "\n" + answer2

  messages =  [{"role" : "system", "content" : "You are an expert in Answering generation using ONLY the given set of facts."},
              {"role": "user", "content": question2 },
              ]
  response = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=messages,
      temperature=0
  )
  return (response.choices[0].message.content)


