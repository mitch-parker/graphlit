# Graphlit

Graphlit is a Streamlit app designed to create, edit, and visualize graph structures from JSON input. You can upload an existing JSON file with optional graph structure, add or edit nodes and edges, and visualize a subgraph based on selected labels.

## Features

1. Upload an optional JSON file containing graph structure (clusters, nodes, and edges).
2. Add, edit, or remove nodes and edges.
3. Multiselect labels to create and visualize a subgraph.
4. Export the created subgraph or the entire graph structure as JSON files.

## Usage

1. Run the Streamlit app:

bash
streamlit run app.py

2. Upload an optional JSON file through the sidebar on the app.

3. Use the provided interface to add, edit, or remove nodes and edges.

4. Select the labels of the subgraph you want to visualize.

5. Download the JSON files for the subgraph and the complete graph using the provided download buttons.

## Requirements

- Python 3.7+
- Streamlit
- graphviz 

## Installation

1. Install the required dependencies:

bash
pip install streamlit graphviz

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check [issues page](https://github.com/mitch-parker/graphlit/issues) if you want to contribute.

## License

Apache-2.0 license. See [LICENSE](https://github.com/mitch-parker/graphlit/blob/main/LICENSE) for more information.