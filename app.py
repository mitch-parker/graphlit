import streamlit as st
import json
from graph import Graph

def main():

    st.title("Graphlit")

    uploaded_file = st.sidebar.file_uploader("Upload JSON (Optional)")
    if uploaded_file is not None:
        if st.sidebar.button("Load JSON"):
            uploaded_json = json.loads(uploaded_file.read())
            st.session_state.graph = Graph(clusters=uploaded_json["clusters"],
                            nodes=uploaded_json["nodes"],
                            edges=uploaded_json["edges"])
            
    if "graph" not in st.session_state:
        st.session_state.graph = Graph()
   
    node_col, edge_col = st.columns([2, 1])

    node_col.subheader("Nodes")

    node_subcols = node_col.columns([1, 1, 1])
    
    node_id = str(node_subcols[0].number_input("ID", min_value=0, step=1, key="add_node_id"))

    label_val = ""
    rank_val = ""
    text_val = ""
    if node_id in st.session_state.graph.get_node_ids():
        label_val = st.session_state.graph.get_node_label(node_id)
        rank_val = st.session_state.graph.get_node_rank(node_id)
        text_val = st.session_state.graph.get_node_text(node_id)

    label = node_subcols[1].text_input("Label", value=label_val, key="add_label")   
    rank = node_subcols[2].text_input("Rank", value=rank_val, key="add_rank")   
    text = node_col.text_area("Text", value=text_val, key="add_text")
    
    if node_id in st.session_state.graph.get_node_ids():  
        if node_col.button("Edit", key="edit_node"):   
            st.session_state.graph.remove_node(node_id)
            st.session_state.graph.add_node(node_id, node_attr={st.session_state.graph.label_attr: label, st.session_state.graph.rank_attr: rank, st.session_state.graph.text_attr: text})

        if node_col.button("Remove", key="remove_node"):     
            st.session_state.graph.remove_node(node_id)
    else:
        if node_col.button("Add", key="add_node"):
            st.session_state.graph.add_node(node_id, node_attr={st.session_state.graph.label_attr: label, st.session_state.graph.rank_attr: rank, st.session_state.graph.text_attr: text})


    edge_col.subheader("Edges")

    edge_subcols = edge_col.columns([1, 1])

    from_node_id = edge_subcols[0].selectbox("From ID", st.session_state.graph.get_node_ids(), key="from_node_id")
    to_node_id = edge_subcols[1].selectbox("To ID", st.session_state.graph.get_node_ids(), key="to_node_id")
        
    if edge_col.button("Add", key="add_edge"):   
        st.session_state.graph.add_edge(from_node_id, to_node_id)
        
    if edge_col.button("Remove", key="remove_edge"):
        st.session_state.graph.remove_edge(from_node_id, to_node_id)
          
    st.subheader("Subgraph")
    if "selected_labels" not in st.session_state:
        st.session_state.selected_labels = []

    graphcols = st.columns(2)
    selected_labels = graphcols[0].multiselect("Select Labels", st.session_state.graph.get_cluster_labels(), default=st.session_state.selected_labels, key="labels_select")
    st.session_state.selected_labels = selected_labels

    st.session_state.subgraph = st.session_state.graph.get_labels_subgraph(selected_labels)
    
    rankdir_lr = False
    if graphcols[1].radio("Layout", ["Top/Bottom", "Left/Right"]) == "Left/Right":
        rankdir_lr = True

    if len(selected_labels) > 0:
        st.graphviz_chart(st.session_state.graph.build_digraph(digraph=st.session_state.subgraph, rankdir_lr=rankdir_lr))

    st.subheader("JSON")
    st.json(st.session_state.subgraph, expanded=False)

    st.download_button("Download Subgraph JSON", json.dumps(st.session_state.subgraph ), "subgraph.json")
    st.sidebar.download_button("Download Graph JSON", json.dumps(st.session_state.graph.graph), "graph.json")
    

if __name__ == "__main__":
    main()