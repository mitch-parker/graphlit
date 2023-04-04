import streamlit as st
import json
import webbrowser
from PIL import Image
from graph import Graph


# Main function for the app
def main():

    # Set the app's title
    title_cols = st.columns([1, 3])
    image = Image.open(f"{__file__.rsplit('/', 1)[0]}/logo.png")
    title_cols[0].image(image)
    title_cols[1].markdown("# Graphlit")
    title_cols[1].markdown("#### A Streamlit app for creating, editing, and visualizing graphs")

    # Add summary of app in sidebar
    st.sidebar.markdown("## Summary")
    st.sidebar.markdown("Graphlit is a Streamlit app for creating, editing, and visualizing graphs. Users can upload JSON files with graph structures or build graphs from scratch using the input fields provided.")
    st.sidebar.markdown("See our [GitHub Page](https://github.com/mitch-parker/graphlit) for further details.")
    st.sidebar.markdown("[![Twitter URL](https://img.shields.io/twitter/url/https/twitter.com/bukotsunikki.svg?style=social&label=Follow%20%40Mitch_P)](https://twitter.com/Mitch_P)")

    with st.sidebar.expander("Features"):
        st.markdown(
            '''
            1. Upload JSON files containing graph structure (clusters, nodes, edges).
            2. Add, edit, or remove nodes and edges.
            3. Create and visualize subgraphs by selecting clusters.
            4. Export subgraphs or entire graph structures as JSON files.
            '''
        )

    # Add a divider under the app's title
    st.markdown("---")

    # Allow user to upload a JSON file
    st.sidebar.markdown("## Upload")
    uploaded_file = st.sidebar.file_uploader("Upload JSON (Optional)")

    # If a JSON file is uploaded, load the file into a Graph object
    if uploaded_file is not None:
        if st.sidebar.button("Load JSON"):
            uploaded_json = json.loads(uploaded_file.read())
            st.session_state.graph = Graph(clusters=uploaded_json["clusters"],
                                           nodes=uploaded_json["nodes"],
                                           edges=uploaded_json["edges"])

    # Initialize an empty Graph object if one has not been loaded
    if "graph" not in st.session_state:
        st.session_state.graph = Graph()

    # Create layout columns for the app
    node_col, edge_col = st.columns([2, 1])

    # NODES PANEL
    node_col.markdown("## Nodes")

    # Determine the mode (add or edit/remove) based on user's selection
    total_node_cols = 2
    node_col_fix = 0
    add_mode = True
    if len(st.session_state.graph.get_node_ids()) > 0:
        if node_col.radio("Options", ["Add", "Edit/Remove"]) == "Edit/Remove":
            total_node_cols += 1
            node_col_fix += 1
            add_mode = False

    # Create layout columns for the node configuration input fields
    node_subcols = node_col.columns(total_node_cols)

    # Configure input fields for node ID, cluster, rank, and text
    if not add_mode:
        node_id = node_subcols[0].selectbox("ID", st.session_state.graph.get_node_ids(), key="node_id")

    attr_keys = [st.session_state.graph.cluster_attr, st.session_state.graph.rank_attr,
                  st.session_state.graph.text_attr, st.session_state.graph.fillcolor_attr,
                  st.session_state.graph.fontcolor_attr, st.session_state.graph.shape_attr,
                  st.session_state.graph.style_attr]
    node_vals = {}
    for attr in attr_keys:
        val = ""
        if not add_mode:
            if st.session_state.graph.is_node_attr(node_id, attr):
                val = st.session_state.graph.get_node_attr(node_id, attr)
        node_vals[attr] = val

    cluster = node_subcols[0+node_col_fix].text_input("Cluster", 
                                                      value=node_vals[st.session_state.graph.cluster_attr], 
                                                      key="node_cluster")
    rank = node_subcols[1+node_col_fix].text_input("Rank", 
                                                   value=node_vals[st.session_state.graph.rank_attr], 
                                                   key="node_rank")
    text = node_col.text_area("Text", 
                              value=node_vals[st.session_state.graph.text_attr], 
                              key="node_text")

    node_attr = {st.session_state.graph.cluster_attr: cluster, 
                st.session_state.graph.rank_attr: rank, 
                st.session_state.graph.text_attr: text}

    with node_col.expander("Optional Input"):

        fillcolor = st.text_input("Fill Color", 
                                  value=node_vals[st.session_state.graph.fillcolor_attr], 
                                  key="node_fillcolor")
        fontcolor = st.text_input("Font Color", 
                                  value=node_vals[st.session_state.graph.fontcolor_attr], 
                                  key="node_fontcolor")
        shape = st.text_input("Shape", 
                              value=node_vals[st.session_state.graph.shape_attr], 
                              key="node_shape")
        style = st.text_input("Style", 
                              value=node_vals[st.session_state.graph.style_attr], 
                              key="node_style")
        
        st.markdown("See [Graphviz](https://graphviz.org) for details.")
        
        for attr, val in {st.session_state.graph.fillcolor_attr: fillcolor,
                          st.session_state.graph.fontcolor_attr: fontcolor,
                          st.session_state.graph.shape_attr: shape,
                          st.session_state.graph.style_attr: style}.items():
            if val != "":
                node_attr.update({attr: val})

    # Create buttons to add, edit, and remove nodes
    if len([x for x in [cluster, rank, text] if x == ""]) != 0:
        node_col.info("Please input cluster, rank, and text.")
    else:
        if add_mode:
            if node_col.button("Add", key="add_node"):
                st.session_state.graph.add_node(node_attr=node_attr)
        else:
            if node_col.button("Edit", key="edit_node"):
                st.session_state.graph.add_node(node_id=node_id, node_attr=node_attr)

            if node_col.button("Remove", key="remove_node"):
                st.session_state.graph.remove_node(node_id)

    # EDGES PANEL
    edge_col.markdown("## Edges")

    # Create layout columns for the edge configuration input fields
    edge_subcols = edge_col.columns(2)

    # Configure input fields for start and end nodes of edges
    from_node_id = edge_subcols[0].selectbox("From ID", st.session_state.graph.get_node_ids(), key="from_node_id")
    to_node_id = edge_subcols[1].selectbox("To ID", st.session_state.graph.get_node_ids(), key="to_node_id")

    # Create buttons to add and remove edges
    if edge_col.button("Add", key="add_edge"):
        st.session_state.graph.add_edge(from_node_id, to_node_id)

    if edge_col.button("Remove", key="remove_edge"):
        st.session_state.graph.remove_edge(from_node_id, to_node_id)

    # Add a divider before subgraph section
    st.markdown("---")

    # SUBGRAPH SECTION
    st.markdown("## Visualization")

    # Initialize selected clusters state variable if not set
    if "selected_clusters" not in st.session_state:
        st.session_state.selected_clusters = []

    # Multiselect widget to select clusters for subgraph generation
    graphcols = st.columns(2)
    selected_clusters = graphcols[0].multiselect("Select Clusters", st.session_state.graph.get_cluster_ids(), default=st.session_state.selected_clusters, key="clusters_select")
    st.session_state.selected_clusters = selected_clusters

    # Generate a subgraph based on selected clusters
    st.session_state.subgraph = st.session_state.graph.get_subgraph_clusters(selected_clusters)

    # Layout radio buttons to select graph layout direction
    rankdir_lr = False
    if graphcols[1].radio("Layout", ["Top/Bottom", "Left/Right"]) == "Left/Right":
        rankdir_lr = True

    # Optional input for graph
    with st.expander("Optional Input"):
        cluster_fillcolor = st.text_input("Cluster Fill Color", 
                              value="lightgrey", 
                              key="cluster_fillcolor")
        cluster_fontcolor = st.text_input("Cluster Font Color", 
                              value="black", 
                              key="cluster_fontcolor")
        rank_fillcolor = st.text_input("Rank Fill Color", 
                              value="white", 
                              key="rank_fillcolor")
        rank_fontcolor = st.text_input("Rank Font Color", 
                              value="black", 
                              key="rank_fontcolor")

        st.markdown("See [Graphviz](https://graphviz.org) for details.")
        

    # Display the subgraph diagram if there are selected clusters
    if len(selected_clusters) > 0:
        st.graphviz_chart(st.session_state.graph.build_digraph(digraph=st.session_state.subgraph, 
                                                               cluster_fillcolor=cluster_fillcolor,
                                                               cluster_fontcolor=cluster_fontcolor,
                                                               rank_fillcolor=rank_fillcolor,
                                                               rank_fontcolor=rank_fontcolor,
                                                               rankdir_lr=rankdir_lr))

    # Make columns for subgraph JSON
    json_cols = st.columns(2)
    # Display the subgraph JSON
    json_cols[0].markdown("## JSON")
    json_cols[0].json(st.session_state.subgraph, expanded=False)

    # Offer download buttons for the subgraph JSON and full graph JSON
    json_cols[1].markdown("## Download")
    json_cols[1].download_button("Download Subgraph JSON", json.dumps(st.session_state.subgraph), "subgraph.json")

    st.sidebar.markdown("## Download")
    st.sidebar.download_button("Download Graph JSON", json.dumps(st.session_state.graph.graph), "graph.json")


    # Add links to relevant web pages in sidebar 
    st.sidebar.markdown("## Links")

    github_url = "https://github.com/mitch-parker/graphlit"
    graphviz_url = "https://graphviz.org"

    url_dict = {"GitHub Page": github_url, "GraphViz Site": graphviz_url}
    for name, url in url_dict.items():
        if st.sidebar.button(name):
            webbrowser.open_new_tab(url)

    # Put app closer
    st.markdown("---")
    st.markdown("Copyright (c) 2023 Mitchell Isaac Parker")


# Run the main function
if __name__ == "__main__":
    main()