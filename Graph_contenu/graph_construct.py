from collections import defaultdict
from tqdm import tqdm
from multiprocessing import Pool
from functools import partial
import networkx as nx
import multiprocessing as mp
import spacy


nlp = spacy.load('en_core_web_lg')

def wiki_spacy_extract_chunk(d):
    nlp = spacy.load('en_core_web_lg')
    nlp.add_pipe("entityLinker", last=True)

    kw2chunk = defaultdict(set)
    chunk2kw = defaultdict(set)
    title2chunk = defaultdict(set)
    chunk2title = defaultdict(set)

    for title, chunk in tqdm(d['title_chunks']):
        doc = nlp(chunk)
        entities = doc._.linkedEntities
        for entity in entities[:10]:
            entity = entity.get_span().text

            kw2chunk[entity].add(chunk)
            chunk2kw[chunk].add(entity)

        title2chunk[title].add(chunk)
        chunk2title[chunk].add(title)

    for key in kw2chunk:
        kw2chunk[key] = list(kw2chunk[key])

    for key in chunk2kw:
        chunk2kw[key] = list(chunk2kw[key])

    for key in title2chunk:
        title2chunk[key] = list(title2chunk[key])

    for key in chunk2title:
        chunk2title[key] = list(chunk2title[key])

    d['kw2chunk'] = kw2chunk
    d['chunk2kw'] = chunk2kw
    d['title2chunk'] = title2chunk
    d['chunk2title'] = chunk2title

    return d


def wiki_spacy_extract(data, num_processes):
    # partial assign parameter to process_d
    func = partial(wiki_spacy_extract_chunk)

    with Pool(num_processes) as p:
        data = list(tqdm(p.imap(func, data), total=len(data)))

    return data


def kw_graph_construct(d):
    # idx, d = i_d

    G = nx.MultiGraph()

    chunk2id = {}
    for i, chunk in enumerate(d['title_chunks']):
        _, chunk = chunk

        G.add_node(i, chunk=chunk)
        chunk2id[chunk] = i

    for kw, chunks in d['kw2chunk'].items():
        for i in range(len(chunks)):
            for j in range(i+1, len(chunks)):
                G.add_edge(chunk2id[chunks[i]], chunk2id[chunks[j]], kw=kw)

    return G


def kw_process_graph(docs):
    pool = mp.Pool(mp.cpu_count())
    graphs = [None] * len(docs)

    for idx, G in tqdm(pool.imap_unordered(kw_graph_construct, enumerate(docs)),total=len(docs)):
        graphs[idx] = G

    pool.close()
    pool.join()

    return graphs
