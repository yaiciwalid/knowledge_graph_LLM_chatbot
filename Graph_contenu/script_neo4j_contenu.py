import json


def kw_graph_construct(file, d):

    with open(file, "w") as f:
        chunk2id = {}
        for i, chunk in enumerate(d['title_chunks']):
            _, chunk = chunk
            chunk_sans_guillemet = chunk
            if '"' in chunk:
                chunk_sans_guillemet = chunk.replace('"', '')
            f.write('MERGE (:Content {contenu:"' + chunk_sans_guillemet + '", id:'
                    + str(i) + '});\n')
            chunk2id[chunk] = i

        for kw, chunks in d['kw2chunk'].items():
            for i in range(len(chunks)):
                for j in range(i+1, len(chunks)):
                    f.write("MATCH (node1:Content), (node2:Content)\n")
                    f.write("WHERE node1.id = "+str(chunk2id[chunks[i]])+" AND node2.id = "+str(chunk2id[chunks[j]])+"\n")
                    f.write('MERGE (node1)-[:has_commun_entity{entity:"'+kw+'"}]-(node2);\n')

        for kw, chunks in d['title2chunk'].items():
            for i in range(len(chunks)):
                for j in range(i+1, len(chunks)):
                    f.write("MATCH (node1:Content), (node2:Content)\n")
                    f.write("WHERE node1.id = "+str(chunk2id[chunks[i]])+" AND node2.id = "+str(chunk2id[chunks[j]])+"\n")
                    f.write('MERGE (node1)-[:has_commun_title{title:"'+kw+'"}]-(node2);\n')
