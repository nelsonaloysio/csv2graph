#!/usr/bin/env python3

"""
usage: csv2graph [-h] [-e EDGE_ATTRS] [-n NODE_ATTRS] [-i NODE_INDEX]
                 [-o OUTPUT_NAME] [--delimiter DELIMITER] [--engine ENGINE]
                 [--extension OUTPUT_FORMAT] [--hashtags] [--mentions]
                 [--no-explosion] [--self-loops] [--undirected] [--unweighted]
                 file_name source target

positional arguments:
  file_name             Input file in CSV format
  source                Source column as found in header
  target                Target columns as found in header (comma separated)

optional arguments:
  -h, --help            show this help message and exit
  -e EDGE_ATTRS, --edge-attrs EDGE_ATTRS
                        Embed edge data from columns (comma separated)
  -n NODE_ATTRS, --node-attrs NODE_ATTRS
                        Embed node data from columns (comma separated)
  -i NODE_INDEX, --node-index NODE_INDEX
                        Specify node index column for attributes (default:
                        source)
  -o OUTPUT_NAME, --output-name OUTPUT_NAME
                        Graph file name to write
  --delimiter DELIMITER
                        Specify file field delimiter
  --engine ENGINE       Pandas engine: 'c' (default), 'python' or 'python-fwf'
  --extension OUTPUT_FORMAT
                        Graph format supported by NetworkX (default: GraphML)
  --hashtags            Find #-tags on target data
  --mentions            Find @-mentions on target data
  --no-explosion        Do not expand lists of values
  --self-loops          Allow edges from a node to itself
  --undirected          Set graph edges as directionless
  --unweighted          Set graph edges as weightless
"""

from argparse import ArgumentParser
from os.path import basename, splitext
from re import findall

import networkx as nx
import pandas as pd


def convert_to_graph(
    file_name: str,
    source: str,
    target: list,
    edge_attrs: list = [],
    node_attrs: list = [],
    node_index: str = None,
    output_name: str = None,
    output_format: str = 'graphml',
    source_map = lambda x: x,
    target_map = lambda x: x,
    delimiter: str = None,
    directed: bool = True,
    engine: str = 'c',
    explode: bool = False,
    self_loops: bool = True,
    weighted: bool = True,
) -> nx.Graph:
    '''
    Build graph from file and write in output format.
    '''
    target = target.split(',') if type(target) == str else target
    node_attrs = node_attrs.split(',') if type(node_attrs) == str else node_attrs
    edge_attrs = edge_attrs.split(',') if type(edge_attrs) == str else edge_attrs

    df = pd.read_csv(
        file_name,
        engine=engine,
        delimiter=delimiter or get_file_delimiter(file_name),
        usecols=[source] + target + (node_index or []) + (node_attrs or []) + (edge_attrs or []),
    )

    df[source] = df[source].astype(str).apply(source_map)
    df[target] = df[target].astype(str).applymap(target_map)

    if explode:
        for column in [source] + target:
            df = df.explode(column)

    E = pd.concat(
        [pd.DataFrame(df[[source, t]].dropna(subset=[t]).values)
         for t in target],
    )

    if not self_loops:
        E = E[E.iloc[:, 0] != E.iloc[:, 1]]

    if weighted:
        weights = E.value_counts()
        E['weight'] = [weights.loc[x, y] for x, y in zip(E.iloc[:, 0], E.iloc[:, 1])]

    G = nx\
        .convert_matrix\
        .from_pandas_edgelist(
            E,
            source=0,
            target=1,
            create_using=nx.DiGraph if directed else nx.Graph,
            edge_attr=(['weight'] if weighted else []) + (edge_attrs if edge_attrs else []),
    )

    for attr in (node_attrs or []):
        nx.set_node_attributes(
            G,
            pd.Series(df[attr].values.tolist(), index=df[(node_index or source)].values.tolist())
            .drop_duplicates()
            .to_dict(),
            attr,
        )

    if output_name is True:
        output_name = basename(splitext(file_name)[0])

    if output_name is not None:
        getattr(nx, f'write_{output_format}')(G, f"{output_name.rstrip(f'.{output_format}')}.{output_format}")

    return G


def find_mentions(x) -> list:
    '''
    Mentions are preceeded by an @-sign and may include
    letters, numbers and underscores to a max. of 30 chars.
    '''
    # regexp = r"@[a-zA-Z0-9_]{0,50}"
    # mentions = findall(regexp, x.lower()) if isinstance(x, str) else []
    mentions = [_ for _ in x.lower().split() if _.startswith("@")]
    return [mention.lstrip("@") for mention in mentions if len(mention)>1]


def find_hashtags(x) -> list:
    '''
    Mentions are preceeded by an @-sign and may include
    letters, numbers and underscores to a max. of 30 chars.
    '''
    # regexp = r"#[a-zA-Z0-9_]{0,50}"
    # hashtags = findall(regexp, x.lower()) if isinstance(x, str) else []
    hashtags = [_ for _ in x.lower().split() if _.startswith("#")]
    return [hashtag for hashtag in hashtags if len(hashtag)>2]


def get_file_delimiter(input_name):
    '''
    Returns character delimiter from file.
    '''
    with open(input_name, 'rt') as input_file:
        header = input_file.readline()

    for d in ['|', '\t', ';', ',']:
        if d in header: # \\t != \t
            return d

    return '\n'


def args() -> dict:
    '''
    Returns dictionary of parameters for execution.
    '''
    argparser = ArgumentParser()

    argparser.add_argument("file_name",
                           help="Input file in CSV format")

    argparser.add_argument("source",
                           help="Source column as found in header")

    argparser.add_argument("target",
                           help="Target columns as found in header (comma separated)")

    argparser.add_argument("-e", "--edge-attrs",
                           help="Embed edge data from columns (comma separated)")

    argparser.add_argument("-n", "--node-attrs",
                           help="Embed node data from columns (comma separated)")

    argparser.add_argument("-i", "--node-index",
                           help="Specify node index column for attributes (default: source)")

    argparser.add_argument("-o", "--output-name",
                           default=True,
                           help="Graph file name to write")

    argparser.add_argument("--delimiter",
                           help="Specify file field delimiter")

    argparser.add_argument("--engine",
                           default="c",
                           help="Pandas engine: 'c' (default), 'python' or 'python-fwf'")

    argparser.add_argument("--extension",
                           default="graphml",
                           dest="output_format",
                           help="Graph format supported by NetworkX (default: GraphML)")

    argparser.add_argument("--hashtags",
                           action="store_const",
                           default=lambda x: x,
                           const=find_hashtags,
                           dest="target_map",
                           help="Find #-tags on target data")

    argparser.add_argument("--mentions",
                           action="store_const",
                           default=lambda x: x,
                           const=find_mentions,
                           dest="target_map",
                           help="Find @-mentions on target data")

    argparser.add_argument("--no-explosion",
                           action="store_false",
                           dest="explode",
                           help="Do not expand lists of values")

    argparser.add_argument("--self-loops",
                           action="store_true",
                           dest="self_loops",
                           help="Allow edges from a node to itself")

    argparser.add_argument("--undirected",
                           action="store_false",
                           dest="directed",
                           help="Set graph edges as directionless")

    argparser.add_argument("--unweighted",
                           action="store_false",
                           dest="weighted",
                           help="Set graph edges as weightless")

    return vars(argparser.parse_args())


if __name__ == "__main__":
    convert_to_graph(**args())
