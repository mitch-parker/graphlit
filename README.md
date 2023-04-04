# Graphlit

Graphlit is a Streamlit app for creating, editing, and visualizing graphs. Users can upload JSON files with graph structures or build graphs from scratch using the input fields provided.

## Features

1. Upload JSON files containing graph structure (clusters, nodes, edges).
2. Add, edit, or remove nodes and edges.
3. Create and visualize subgraphs by selecting clusters.
4. Export subgraphs or entire graph structures as JSON files.

## Usage

1. Run the app: `streamlit run app.py`
2. Upload an optional JSON file in the app sidebar.
3. Add, edit, or remove nodes and edges using the interface.
4. Select clusters for subgraph visualization.
5. Download subgraph and full graph JSON files.

## Requirements

- Python 3.7+
- Streamlit
- graphviz

## Installation

1. Install dependencies: `pip install streamlit graphviz`

## JSON Format

```json
{
  "clusters": {
    "Cluster_1": {"Rank_1": ["Node_1"], "Rank_2": ["Node_2"]},
    "Cluster_2": {"Rank_3": ["Node_3", "Node_4"]}
  },
  "nodes": {
    "Node_1": {"cluster": "Cluster_1", "rank": "Rank_1", "text": "Node 1 Text"},
    "Node_2": {"cluster": "Cluster_1", "rank": "Rank_2", "text": "Node 2 Text"},
    ...
  },
  "edges": [
    {"from": "Node_1", "to": "Node_2"},
    {"from": "Node_2", "to": "Node_3"},
    ...
  ]
}
```

- `clusters`: Maps unique clusters to dictionaries of nodes categorized by rank.
- `nodes`: Maps unique node IDs to dictionaries with node attributes (cluster, rank, text, etc.).
- `edges`: List of dictionaries representing graph edges (with 'from' and 'to' keys for node IDs).

## Contributing

Contributions, issues, and feature requests are welcome. Check the [issues page](https://github.com/mitch-parker/graphlit/issues) to contribute.

## License

Apache-2.0. See [LICENSE](https://github.com/mitch-parker/graphlit/blob/main/LICENSE) for details.