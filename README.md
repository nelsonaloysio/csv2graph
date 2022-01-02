# csv2graph

Simple python code to build graphs from CSV files using **NetworkX** and **Pandas**.

```
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
```

