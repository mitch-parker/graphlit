import streamlit as st
import json
import webbrowser
from PIL import Image
from graph import Graph


# Main function for the app
def main():

    # Set page config
    st.set_page_config(page_title="Graphlit", page_icon="🔍", layout="wide")

    # Set the app's title
    title_cols = st.columns([1, 4])

    title_cols[1].markdown("# Graphlit 🔍")
    title_cols[1].markdown("#### A Streamlit app for creating, editing, and visualizing graphs")
    title_cols[1].markdown("**Developed by Mitchell Parker**")

    image = Image.open(f"{__file__.rsplit('/', 1)[0]}/logo.png")
    title_cols[0].image(image)
    title_cols[0].markdown("Powered by [GraphViz](https://graphviz.org).")

    # Add summary of app in sidebar
    st.sidebar.markdown("## Summary")
    st.sidebar.markdown("Graphlit is a Streamlit app for creating, editing, and visualizing graphs. Users can upload JSON files with graph structures or build graphs from scratch using the input fields provided.")

    with st.sidebar.expander("Features"):
        st.markdown(
            '''
            1. Upload JSON files containing graph structure (clusters, nodes, edges).
            2. Add, edit, or remove nodes and edges.
            3. Create and visualize subgraphs by selecting clusters.
            4. Export subgraphs or entire graph structures as JSON files.
            '''
        )

    st.sidebar.markdown("See our [GitHub Page](https://github.com/mitch-parker/graphlit) for further details.")
    st.sidebar.markdown("[![Twitter URL](https://img.shields.io/twitter/url/https/twitter.com/bukotsunikki.svg?style=social&label=Follow%20%40Mitch_P)](https://twitter.com/Mitch_P)")

    # Add a divider under the app's title
    st.markdown("---")

    # Initialize session state items
    if "graph" not in st.session_state:
        st.session_state.graph = Graph()
    if "subgraph_cluster_ids" not in st.session_state:
        st.session_state.subgraph_cluster_ids = []

    # Add option to clear graph and load example
    clear_example_cols = st.sidebar.columns(2)
    clear_example_cols[0].markdown("## Reset")
    if clear_example_cols[0].button("Clear Graph"):
        st.session_state.graph = Graph()
        st.session_state.subgraph_cluster_ids = []

    clear_example_cols[1].markdown("## Example")  
    if clear_example_cols[1].button("Load Graph", key="load_example"):  
        st.session_state.graph = Graph(clusters={
                                        "Cluster 1": {"Rank 1": ["1"], "Rank 2": ["2"]},
                                        "Cluster 2": {"Rank 3": ["3", "4"]}
                                    },
                                    nodes={
                                        "1": {"cluster": "Cluster 1", "rank": "Rank 1", "text": "Node 1"},
                                        "2": {"cluster": "Cluster 1", "rank": "Rank 2", "text": "Node 2"},
                                        "3": {"cluster": "Cluster 2", "rank": "Rank 3", "text": "Node 3"},
                                        "4": {"cluster": "Cluster 2", "rank": "Rank 3", "text": "Node 4"},
                                    },
                                    edges={
                                        "1->2": {},
                                        "1->3": {},
                                        "2->4": {},
                                    })
        st.session_state.subgraph_cluster_ids = []

    # Allow user to upload a JSON file
    st.sidebar.markdown("## Upload")
    uploaded_file = st.sidebar.file_uploader("Upload JSON (Optional)")

    # If a JSON file is uploaded, load the file into a Graph object
    if uploaded_file is not None:
        if st.sidebar.button("Load Graph", key="load_file"):
            uploaded_json = json.loads(uploaded_file.read())
            st.session_state.graph = Graph(clusters=uploaded_json["clusters"],
                                           nodes=uploaded_json["nodes"],
                                           edges=uploaded_json["edges"])
            st.session_state.subgraph_cluster_ids = []
            
    # Determine if graph already has nodes, which will inform the layout
    graph_has_nodes = len(st.session_state.graph.get_node_ids()) > 0

    # Create layout columns for the app
    if graph_has_nodes:
        node_col, edge_col = st.columns([2, 1])
    else:
        node_col = st

    # NODES PANEL
    node_col.markdown("## Nodes")

    # Determine if user want to automatically cluster or rank all nodes together, which will inform layout
    top_fix = 0
    if graph_has_nodes:
        top_fix += 1 
        
    top_node_subcols = node_col.columns(2)

    auto_cluster = top_node_subcols[0+top_fix].checkbox("Auto Cluster", value=False, key="auto_cluster")
    auto_rank = top_node_subcols[1].checkbox("Auto Rank", value=False, key="auto_rank")

    # Determine the mode (add or edit/remove) based on user's selection, which will inform layout
    total_bottom = 2
    bottom_fix = 0
    add_mode = True
    if graph_has_nodes:
        if top_node_subcols[0].radio("Options", ["Add", "Edit/Remove"], horizontal=True) == "Edit/Remove":
            total_bottom += 1
            bottom_fix += 1
            add_mode = False

    if add_mode:
        if auto_cluster or auto_rank:
            total_bottom -= 1
            bottom_fix -= 1
    else:
        if auto_cluster:
            total_bottom -= 1
        if auto_rank:
            total_bottom -= 1

    # Create layout columns for the node configuration input fields
    bottom_node_subcols = node_col.columns(total_bottom)

    # Configure input fields for node ID, cluster, rank, and text
    if not add_mode:
        node_id = bottom_node_subcols[0].selectbox("Node", st.session_state.graph.get_node_ids(), key="node_id")

    node_attr_keys = [st.session_state.graph.cluster_attr, st.session_state.graph.rank_attr,
                  st.session_state.graph.text_attr, st.session_state.graph.fillcolor_attr,
                  st.session_state.graph.fontcolor_attr, st.session_state.graph.shape_attr,
                  st.session_state.graph.style_attr]
    
    node_optionals = {st.session_state.graph.fillcolor_attr: "black",
                      st.session_state.graph.fontcolor_attr: "white",
                      st.session_state.graph.shape_attr: "box",
                      st.session_state.graph.style_attr: "rounded,filled",
                      }
    node_values = {}
    for attr_key in node_attr_keys:
        if attr_key in list(node_optionals.keys()):
            node_val = node_optionals[attr_key]
        else:
            node_val = ""
        if not add_mode:
            if st.session_state.graph.is_node_attr(node_id, attr_key):
                node_val = st.session_state.graph.get_node_attr(node_id, attr_key)
        node_values[attr_key] = node_val

    node_cluster = "Cluster"
    if not auto_cluster:
        node_cluster = bottom_node_subcols[0+bottom_fix].text_input("Cluster", 
                                                        value=node_values[st.session_state.graph.cluster_attr], 
                                                        key="node_cluster")
    
    node_rank = "Rank"
    if not auto_rank:
        node_rank = bottom_node_subcols[1+bottom_fix].text_input("Rank", 
                                                    value=node_values[st.session_state.graph.rank_attr], 
                                                    key="node_rank")

    node_text = node_col.text_area("Text", 
                              value=node_values[st.session_state.graph.text_attr], 
                              key="node_text")

    node_attr = {st.session_state.graph.cluster_attr: node_cluster, 
                st.session_state.graph.rank_attr: node_rank, 
                st.session_state.graph.text_attr: node_text}

    with node_col.expander("Optional Input"):

        node_fillcolor = st.text_input("Fill Color", 
                                  value=node_values[st.session_state.graph.fillcolor_attr], 
                                  key="node_fillcolor")
        node_fontcolor = st.text_input("Font Color", 
                                  value=node_values[st.session_state.graph.fontcolor_attr], 
                                  key="node_fontcolor")
        node_shape = st.text_input("Shape", 
                              value=node_values[st.session_state.graph.shape_attr], 
                              key="node_shape")
        node_style = st.text_input("Style", 
                              value=node_values[st.session_state.graph.style_attr], 
                              key="node_style")
        
        st.markdown("See [Graphviz](https://graphviz.org) for details.")
        
        for attr_key, attr_val in {st.session_state.graph.fillcolor_attr: node_fillcolor,
                          st.session_state.graph.fontcolor_attr: node_fontcolor,
                          st.session_state.graph.shape_attr: node_shape,
                          st.session_state.graph.style_attr: node_style}.items():
            if attr_val not in ["", node_optionals[attr_key]]:
                node_attr.update({attr_key: attr_val})

    # Create buttons to add, edit, and remove nodes
    if len([x for x in [node_cluster, node_rank, node_text] if x == ""]) != 0:
        node_col.info("Please input cluster, rank, and text.")
    else:
        if add_mode:
            if node_col.button("Add", key="add_node"):
                st.session_state.graph.add_node(node_attr=node_attr)
        else:
            if node_col.button("Edit", key="edit_node"):
                st.session_state.graph.remove_node(node_id)
                st.session_state.graph.add_node(node_id=node_id, node_attr=node_attr)

            if node_col.button("Remove", key="remove_node"):
                st.session_state.graph.remove_node(node_id)

    # If graph has node add edges panel
    if graph_has_nodes:

        # EDGES PANEL
        edge_col.markdown("## Edges")
        
        # Specify edge type
        edge_level_options = ["Cluster", "Rank", "Node"]
        if auto_cluster:
            edge_level_options.remove("Cluster")
        if auto_rank:
            edge_level_options.remove("Rank")
        if len(edge_level_options) == 1:
            edge_level = "Node"
        else:
            edge_level = edge_col.radio("Level", edge_level_options, index=len(edge_level_options)-1, horizontal=True, key="edge_level")

        # Create layout columns for the edge configuration input fields
        edge_subcols = edge_col.columns(3)

        # Configure input fields for start and end nodes of edges
        if edge_level=="Cluster" or edge_level=="Rank":
            from_cluster_id = edge_subcols[0].selectbox("From Cluster", st.session_state.graph.get_cluster_ids(), key="from_cluster_id")
            to_cluster_id = edge_subcols[1].selectbox("To Cluster", st.session_state.graph.get_cluster_ids(), key="to_cluster_id")
            if edge_level == "Rank":
                from_rank_id = edge_subcols[0].selectbox("From Rank", st.session_state.graph.get_cluster_rank_ids(from_cluster_id), key="from_rank_id")
                to_rank_id = edge_subcols[1].selectbox("To Rank", st.session_state.graph.get_cluster_rank_ids(to_cluster_id), key="to_rank_id")
        elif edge_level == "Node":    
            from_node_id = edge_subcols[0].selectbox("From Node", st.session_state.graph.get_node_ids(), key="from_node_id")
            to_node_id = edge_subcols[1].selectbox("To Node", st.session_state.graph.get_node_ids(), key="to_node_id")

        edge_attr_keys = [st.session_state.graph.label_attr, st.session_state.graph.color_attr]
        edge_optionals = {st.session_state.graph.label_attr:"",
                        st.session_state.graph.color_attr:"black"}
        edge_values = {}
        for attr_key in edge_attr_keys:
            if attr_key in list(edge_optionals.keys()):
                edge_val = edge_optionals[attr_key]
            else:
                edge_val = ""
            if edge_level == "Node":
                if st.session_state.graph.join_edge_id(from_node_id, to_node_id) in st.session_state.graph.get_edge_ids():
                    if st.session_state.graph.is_edge_attr(from_node_id, to_node_id, attr_key):
                        edge_val = st.session_state.graph.get_edge_attr(from_node_id, to_node_id, attr_key)
            edge_values[attr_key] = edge_val

        edge_attr = {}
        with edge_col.expander("Optional Input"):
            edge_label = st.text_input("Label", value=edge_values[st.session_state.graph.label_attr],
                                    key="edge_label")
            edge_color = st.text_input("Color", value=edge_values[st.session_state.graph.color_attr],
                                    key="edge_color")
            
            st.markdown("See [Graphviz](https://graphviz.org) for details.")

            for attr_key, attr_val in {st.session_state.graph.label_attr: edge_label,
                            st.session_state.graph.color_attr: edge_color}.items():
                if attr_val not in ["", edge_optionals[attr_key]]:
                    edge_attr.update({attr_key: attr_val})

        # Create buttons to add and remove edges
        if edge_col.button("Add/Edit", key="add_node_edge"):
            if edge_level == "Cluster":
                st.session_state.graph.add_cluster_edge(from_cluster_id, to_cluster_id, edge_attr=edge_attr)
            elif edge_level == "Rank":
                st.session_state.graph.add_cluster_rank_edge(from_cluster_id, from_rank_id, to_cluster_id, to_rank_id, edge_attr=edge_attr)
            elif edge_level == "Node":
                st.session_state.graph.add_node_edge(from_node_id, to_node_id, edge_attr=edge_attr)

        if edge_col.button("Remove", key="remove_node_edge"):
            if edge_level == "Cluster":
                st.session_state.graph.remove_cluster_edge(from_cluster_id, to_cluster_id)
            elif edge_level == "Rank":
                st.session_state.graph.remove_cluster_rank_edge(from_cluster_id, from_rank_id, to_cluster_id, to_rank_id)
            elif edge_level == "Node":
                st.session_state.graph.remove_node_edge(from_node_id, to_node_id)

    # Add a divider before subgraph section
    st.markdown("---")

    # SUBGRAPH SECTION
    st.markdown("## Visualization")

    # Multiselect widget to select clusters for subgraph generation
    subgraph_cols = st.columns([2, 1, 1])

    st.session_state.subgraph_cluster_ids = subgraph_cols[0].multiselect("Select Clusters", 
                                                                         st.session_state.graph.get_cluster_ids(), 
                                                                         default=st.session_state.subgraph_cluster_ids, 
                                                                         key="select_clusters")

    subgraph_node_ids = []
    for cluster_id in st.session_state.subgraph_cluster_ids:
        for rank_id in st.session_state.graph.get_cluster_rank_ids(cluster_id):
            subgraph_node_ids += st.session_state.graph.get_cluster_rank_node_ids(cluster_id, rank_id)

    # Generate a subgraph based on selected clusters
    subgraph = st.session_state.graph.get_subgraph(subgraph_node_ids)

    # Layout radio buttons to select graph layout direction
    rankdir_lr = False
    if subgraph_cols[1].radio("Layout", ["Top/Bottom", "Left/Right"], horizontal=True) == "Left/Right":
        rankdir_lr = True

    # Specify cluster and rank colors
    cluster_fillcolor_val = "lightgrey"
    cluster_fontcolor_val = "black"
    rank_fillcolor_val = "white"
    rank_fontcolor_val = "black"

    # Add option to hide cluster or rank
    hide_cluster = subgraph_cols[2].checkbox("Hide Cluster Background", value=auto_cluster)
    hide_rank = subgraph_cols[2].checkbox("Hide Rank Background", value=auto_rank)

    if hide_cluster:
        cluster_fillcolor_val = "white"
        cluster_fontcolor_val = "white"

    if hide_rank:
        if hide_cluster:
            rank_fillcolor_val = "white"
            rank_fontcolor_val = "white"
        else:
            rank_fillcolor_val = cluster_fillcolor_val
            rank_fontcolor_val = cluster_fillcolor_val


    # Optional input for graph
    with st.expander("Optional Input"):
        cluster_fillcolor = st.text_input("Cluster Fill Color", 
                              value=cluster_fillcolor_val, 
                              key="cluster_fillcolor")
        cluster_fontcolor = st.text_input("Cluster Font Color", 
                              value=cluster_fontcolor_val, 
                              key="cluster_fontcolor")
        rank_fillcolor = st.text_input("Rank Fill Color", 
                              value=rank_fillcolor_val, 
                              key="rank_fillcolor")
        rank_fontcolor = st.text_input("Rank Font Color", 
                              value=rank_fontcolor_val, 
                              key="rank_fontcolor") 
        words_per_node = st.number_input("Words Per Node", 
                              value=5, 
                              key="words_per_node")
        words_per_node_line= st.number_input("Words Per Node Line", 
                              value=3, 
                              key="words_per_node_line")

        st.markdown("See [Graphviz](https://graphviz.org) for details.")
        

    # Display the subgraph diagram if there are selected clusters
    if len(subgraph_node_ids) > 0:
        st.graphviz_chart(st.session_state.graph.build_digraph(graph=subgraph,
                            cluster_fillcolor=cluster_fillcolor,
                            cluster_fontcolor=cluster_fontcolor,
                            rank_fillcolor=rank_fillcolor,
                            rank_fontcolor=rank_fontcolor,
                            words_per_node=words_per_node, 
                            words_per_node_line=words_per_node_line,
                            rankdir_lr=rankdir_lr))
        

    # Add under the subgraphs section
    st.markdown("---")

    # Make columns for subgraph JSON
    json_cols = st.columns(2)

    # Display the subgraph JSON
    json_cols[0].markdown("## JSON")
    json_cols[0].json(subgraph, expanded=True)

    # Offer download buttons for the subgraph JSON and full graph JSON
    json_cols[1].markdown("## Download")
    json_cols[1].download_button("Download Subgraph JSON", json.dumps(subgraph), "subgraph.json")
    json_cols[1].download_button("Download Graph JSON", json.dumps(st.session_state.graph.graph), "graph.json")

    # Add links to relevant web pages in sidebar 
    st.sidebar.markdown("## Links")

    github_url = "https://github.com/mitch-parker/graphlit"
    graphviz_url = "https://graphviz.org"

    url_dict = {"GitHub Page": github_url, "GraphViz Site": graphviz_url}
    url_cols = st.sidebar.columns(2)
    i = 0
    for name, url in url_dict.items():
        name_url_col = url_cols[i]
        i += 1
        if i == len(url_cols):
            i = 0
        if name_url_col.button(name):
            webbrowser.open_new_tab(url)

    # Put app closer
    st.markdown("---")
    st.markdown("Copyright (c) 2023 Mitchell Isaac Parker")

# Run the main function
if __name__ == "__main__":
    main()