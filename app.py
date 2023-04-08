import streamlit as st
import json
import webbrowser
from PIL import Image
from graph import Graph


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
if "hide_cluster" not in st.session_state:
    st.session_state.hide_cluster = False
if "hide_rank" not in st.session_state:
    st.session_state.hide_rank = False
if "rankdir_lr" not in st.session_state:
    st.session_state.rankdir_lr = False
if "show_graph" not in st.session_state:
    st.session_state.show_graph = False

# Add option to clear graph and load example
clear_example_cols = st.sidebar.columns(2)
clear_example_cols[0].markdown("## Reset")
if clear_example_cols[0].button("Clear Graph"):
    st.session_state.graph = Graph()
    st.session_state.subgraph_cluster_ids = []
    st.session_state.show_graph = True

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
    st.session_state.show_graph = True

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
        st.session_state.show_graph = True
        
# Determine if graph already has nodes, which will inform the layout
graph_has_nodes = len(st.session_state.graph.get_node_ids()) > 0

# Create layout columns for the app
if graph_has_nodes:
    node_col, edge_col = st.columns([3, 2])
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
        bottom_fix -= 1
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

    node_option_cols = st.columns(2)

    node_fillcolor = node_option_cols[0].text_input("Fill Color", 
                            value=node_values[st.session_state.graph.fillcolor_attr], 
                            key="node_fillcolor")
    node_fontcolor = node_option_cols[1].text_input("Font Color", 
                            value=node_values[st.session_state.graph.fontcolor_attr], 
                            key="node_fontcolor")
    node_shape = node_option_cols[0].text_input("Shape", 
                        value=node_values[st.session_state.graph.shape_attr], 
                        key="node_shape")
    node_style = node_option_cols[1].text_input("Style", 
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
        if node_col.button("Add", key="add_nodes"):
            st.session_state.graph.add_nodes(node_attr=node_attr)
            st.session_state.show_graph = True
    else:
        if node_col.button("Edit", key="edit_nodes"):
            st.session_state.graph.remove_nodes(node_id, edit_mode=True)
            st.session_state.graph.add_nodes(node_ids=node_id, node_attr=node_attr)

            st.session_state.subgraph_cluster_ids = [x for x in st.session_state.subgraph_cluster_ids if x in st.session_state.graph.get_cluster_ids()]
            st.session_state.show_graph = True

        if node_col.button("Remove", key="remove_nodes"):
            st.session_state.graph.remove_nodes(node_id)

            st.session_state.subgraph_cluster_ids = [x for x in st.session_state.subgraph_cluster_ids if x in st.session_state.graph.get_cluster_ids()]
            st.session_state.show_graph = True

# If graph has node add edges panel
if graph_has_nodes:

    # EDGES PANEL
    edge_col.markdown("## Edges")

    # Create layout columns for the edge configuration input fields
    edge_subcols = edge_col.columns(2)

    # Loop through through sides of edge
    from_to_select = {"from": {}, "to": {}}

    for i, from_to in enumerate(from_to_select.keys()):

        # Specify to from title
        from_to_title = f"{from_to.title()}"

        # Specify edge levels
        from_to_level_options = ["Cluster", "Rank", "Node"]

        # Specify edge type
        if auto_cluster:
            from_to_level_options.remove("Cluster")
        if auto_rank:
            from_to_level_options.remove("Rank")
        if len(from_to_level_options) == 1:
            from_to_level = "Node"
        else:
            from_to_level = edge_subcols[i].radio(f"{from_to_title} Level", from_to_level_options, index=len(from_to_level_options)-1, key=f"{from_to}_level")

        # Configure input fields for start and end nodes of edges
        if from_to_level=="Cluster" or from_to_level=="Rank":
            from_to_cluster_ids = edge_subcols[i].selectbox(f"{from_to_title} Cluster", st.session_state.graph.get_cluster_ids(), key=f"{from_to}_cluster_ids")
            if from_to_level == "Rank":
                from_to_rank_ids = edge_subcols[i].selectbox(f"{from_to_title} Rank", st.session_state.graph.get_cluster_rank_ids(from_to_cluster_ids), key=f"{from_to}_rank_ids")
                from_to_node_ids = st.session_state.graph.get_cluster_rank_node_ids(from_to_cluster_ids, from_to_rank_ids)
            else:
                from_to_node_ids = st.session_state.graph.get_cluster_node_ids(from_to_cluster_ids)
        elif from_to_level == "Node":    
            from_to_node_ids = edge_subcols[i].selectbox(f"{from_to_title} Node", st.session_state.graph.get_node_ids(), key=f"{from_to}_node_ids")
          
        from_to_select[from_to]["node_ids"] = from_to_node_ids
        from_to_select[from_to]["level"] = from_to_level
    
    # Extract selected to and from IDs
    from_node_ids = from_to_select["from"]["node_ids"]
    to_node_ids = from_to_select["to"]["node_ids"]
    from_level = from_to_select["from"]["level"]
    to_level = from_to_select["to"]["level"]

    # Specify edge attributes
    edge_attr_keys = [st.session_state.graph.label_attr, st.session_state.graph.color_attr]
    edge_optionals = {st.session_state.graph.label_attr:"",
                    st.session_state.graph.color_attr:"black"}
    edge_values = {}
    for attr_key in edge_attr_keys:
        if attr_key in list(edge_optionals.keys()):
            edge_val = edge_optionals[attr_key]
        else:
            edge_val = ""
        if (from_level == "Node") and (to_level == "Node"):
            if st.session_state.graph.join_edge_id(from_node_ids, to_node_ids) in st.session_state.graph.get_edge_ids():
                if st.session_state.graph.is_edge_attr(from_node_ids, to_node_ids, attr_key):
                    edge_val = st.session_state.graph.get_edge_attr(from_node_ids, to_node_ids, attr_key)
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
    if edge_col.button("Add/Edit", key="add_edges"):
        st.session_state.graph.add_edges(from_node_ids, to_node_ids, edge_attr=edge_attr)
        st.session_state.show_graph = True

    if edge_col.button("Remove", key="remove_edges"):
        st.session_state.graph.remove_edges(from_node_ids, to_node_ids)
        st.session_state.show_graph = True

# Expander to rename clusters or ranks
if graph_has_nodes:
    edge_col.markdown("## Clusters")
    with edge_col.expander("Rename Input"):

        rename_level = st.radio("Level", ["Cluster", "Rank"], horizontal=True)

        rename_cols = st.columns(2)

        old_cluster_id = rename_cols[0].selectbox("Old Cluster", st.session_state.graph.get_cluster_ids(), key="old_cluster_id")
        new_cluster_id = rename_cols[1].text_input("New Cluster", key="new_cluster_id")

        if rename_level == "Rank":
            old_rank_id = rename_cols[0].selectbox("Old Rank", st.session_state.graph.get_cluster_rank_ids(old_cluster_id), key="old_rank_id")
            new_rank_id = rename_cols[1].text_input("New Rank", key="new_rank_id")

        if new_cluster_id != "":
            if (rename_level == "Cluster" and old_cluster_id != new_cluster_id) or (rename_level == "Rank" and new_rank_id != "" and old_rank_id != new_rank_id):
                if st.button("Rename"):
                    if rename_level == "Cluster":
                        st.session_state.graph.rename_cluster_id(old_cluster_id, new_cluster_id) 
                        st.session_state.subgraph_cluster_ids = list(set(map(lambda x: x.replace(old_cluster_id, 
                                                                                                new_cluster_id), 
                                                                                                st.session_state.subgraph_cluster_ids)))
                    else:                                                            
                        st.session_state.graph.rename_cluster_rank_id(old_cluster_id, old_rank_id, new_cluster_id, new_rank_id)
                        st.session_state.subgraph_cluster_ids = list(set(map(lambda x: x.replace(old_cluster_id, 
                                                                                                    new_cluster_id), 
                                                                                                    st.session_state.subgraph_cluster_ids)))
                    st.session_state.show_graph = True

# Add a divider before subgraph section
st.markdown("---")

# SUBGRAPH SECTION
st.markdown("## Visualization")

# Multiselect widget to select clusters for subgraph generation
subgraph_cols = st.columns([2, 1, 1])

subgraph_cluster_ids = subgraph_cols[0].multiselect("Select Clusters", 
                                                                        st.session_state.graph.get_cluster_ids(), 
                                                                        default=st.session_state.subgraph_cluster_ids, 
                                                                        key="select_clusters")
if subgraph_cluster_ids != st.session_state.subgraph_cluster_ids:
    st.session_state.subgraph_cluster_ids = subgraph_cluster_ids
    st.session_state.show_graph = True

subgraph_node_ids = []
for cluster_id in st.session_state.subgraph_cluster_ids:
    for rank_id in st.session_state.graph.get_cluster_rank_ids(cluster_id):
        subgraph_node_ids += st.session_state.graph.get_cluster_rank_node_ids(cluster_id, rank_id)

# Generate a subgraph based on selected clusters
subgraph = st.session_state.graph.get_subgraph(subgraph_node_ids)

# Layout radio buttons to select graph layout direction
rankdir_lr = subgraph_cols[1].radio("Layout", ["Top/Bottom", "Left/Right"], horizontal=True) == "Left/Right"
if rankdir_lr != st.session_state.rankdir_lr:
    st.session_state.rankdir_lr = rankdir_lr
    st.session_state.show_graph = True

# Add option to hide cluster or rank
hide_cluster = subgraph_cols[2].checkbox("Hide Cluster Background", value=auto_cluster)
if hide_cluster != st.session_state.hide_cluster:
    st.session_state.hide_cluster = hide_cluster
    st.session_state.show_graph = True

hide_rank = subgraph_cols[2].checkbox("Hide Rank Background", value=auto_rank)
if hide_rank != st.session_state.hide_rank:
    st.session_state.hide_rank = hide_rank
    st.session_state.show_graph = True

# Specify cluster and rank colors
cluster_fillcolor = "lightgrey"
cluster_fontcolor = "black"
rank_fillcolor = "white"
rank_fontcolor = "black"

# Optional input for graph
with st.expander("Optional Input"):

    visual_option_cols = st.columns(2)
    if hide_cluster:
        cluster_fillcolor = "white"
        cluster_fontcolor = "white"
        if not hide_rank:
            rank_fillcolor = "lightgrey"
            rank_fontcolor = "black"
    else:
        cluster_fillcolor = visual_option_cols[0].text_input("Cluster Fill Color", 
                                value=cluster_fillcolor, 
                                key="cluster_fillcolor")
        cluster_fontcolor = visual_option_cols[1].text_input("Cluster Font Color", 
                                value=cluster_fontcolor, 
                                key="cluster_fontcolor")
    if hide_rank:
        if hide_cluster:
            rank_fillcolor = "white"
            rank_fontcolor = "white"
        else:
            rank_fillcolor = cluster_fillcolor
            rank_fontcolor = cluster_fillcolor
    else:
        rank_fillcolor = visual_option_cols[0].text_input("Rank Fill Color", 
                                value=rank_fillcolor, 
                                key="rank_fillcolor")
        rank_fontcolor = visual_option_cols[1].text_input("Rank Font Color", 
                                value=rank_fontcolor, 
                                key="rank_fontcolor") 

    words_per_node = visual_option_cols[0].number_input("Words Per Node", 
                            value=5, 
                            key="words_per_node")
    words_per_node_line= visual_option_cols[1].number_input("Words Per Node Line", 
                            value=3, 
                            key="words_per_node_line")
    
    if st.button("Update Visualization"):
        st.session_state.show_graph = True

    st.markdown("See [Graphviz](https://graphviz.org) for details.")
    

# Display the subgraph diagram if there are selected clusters
if len(subgraph_node_ids) > 0 and st.session_state.show_graph:
    st.graphviz_chart(st.session_state.graph.build_digraph(graph=subgraph,
                        cluster_fillcolor=cluster_fillcolor,
                        cluster_fontcolor=cluster_fontcolor,
                        rank_fillcolor=rank_fillcolor,
                        rank_fontcolor=rank_fontcolor,
                        words_per_node=words_per_node, 
                        words_per_node_line=words_per_node_line,
                        rankdir_lr=rankdir_lr))
    st.session_state.show_graph = False
    

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
st.markdown("Copyright \u00A9 2023 Mitchell Isaac Parker")
