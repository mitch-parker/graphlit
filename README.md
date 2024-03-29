# Graphlit 🔍 - A Streamlit app for creating, editing, and visualizing graphs

[![mitch-parker - graphlit](https://img.shields.io/static/v1?label=mitch-parker&message=graphlit&color=blue&logo=github)](https://github.com/mitch-parker/graphlit "Go to GitHub repo")
[![stars - graphlit](https://img.shields.io/github/stars/mitch-parker/graphlit?style=social)](https://github.com/mitch-parker/graphlit)
[![forks - graphlit](https://img.shields.io/github/forks/mitch-parker/graphlit?style=social)](https://github.com/mitch-parker/graphlit)

[![GitHub tag](https://img.shields.io/github/tag/mitch-parker/graphlit?include_prereleases=&sort=semver&color=blue)](https://github.com/mitch-parker/graphlit/releases/)
[![License](https://img.shields.io/badge/License-Apache--2.0-blue)](#license)
[![issues - graphlit](https://img.shields.io/github/issues/mitch-parker/graphlit)](https://github.com/mitch-parker/graphlit/issues)

## Summary

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

1. Install dependencies: 

```bash
$ conda create -n graphlit_env python=3.10
$ conda activate graphlit_env
$ pip install streamlit graphviz
```

## JSON Format

```json
{
  "clusters": {
      "Cluster 1": {"Rank 1": ["1"], "Rank 2": ["2"]},
      "Cluster 2": {"Rank 3": ["3", "4"]}
  },
  "nodes": {
      "1": {"cluster": "Cluster 1", "rank": "Rank 1", "text": "Node 1"},
      "2": {"cluster": "Cluster 1", "rank": "Rank 2", "text": "Node 2"},
      "3": {"cluster": "Cluster 2", "rank": "Rank 3", "text": "Node 3"},
      "4": {"cluster": "Cluster 2", "rank": "Rank 3", "text": "Node 4"},
    ...
  },
  "edges": {
    "1->2": {},
    "1->3": {},
    "2->4": {},
    ...
  }
}
```

- `clusters`: Maps unique clusters to dictionaries of nodes categorized by rank.
- `nodes`: Maps unique node IDs to dictionaries with node attributes (cluster, rank, text, etc.).
- `edges`: List of dictionaries representing graph edges (with 'from' and 'to' keys for node IDs).

## Contributing

Contributions, issues, and feature requests are welcome. Check the [issues page](https://github.com/mitch-parker/graphlit/issues) to contribute.

## Authors

Please feel free to contact us with any suggestions, comments, or questions.

#### Mitchell Parker [![Twitter URL](https://img.shields.io/twitter/url/https/twitter.com/bukotsunikki.svg?style=social&label=Follow%20%40Mitch_P)](https://twitter.com/Mitch_P)

- Email: <mitch.isaac.parker@gmail.com>
- GitHub: https://github.com/mitch-parker

## License

Apache-2.0. See [LICENSE](https://github.com/mitch-parker/graphlit/blob/main/LICENSE) for details.