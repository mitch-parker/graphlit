from graphviz import Digraph
from copy import deepcopy
import random

class Graph():
    def __init__(self, clusters={}, nodes={}, edges={}):
        # Constants
        self.id_key = "id"
        self.clusters_key = "clusters"
        self.nodes_key = "nodes"
        self.edges_key = "edges"
        self.cluster_attr = "cluster"
        self.rank_attr = "rank"
        self.text_attr = "text"
        self.fillcolor_attr = "fillcolor"
        self.fontcolor_attr = "fontcolor"
        self.shape_attr = "shape"
        self.style_attr = "style"
        self.label_attr = "label"
        self.color_attr = "color"
        self.edge_sep = " -> "

        # Graph structure
        self.graph = {self.clusters_key: clusters, self.nodes_key: nodes, self.edges_key: edges}

    def get_clusters(self, graph=None):
        # Returns dictionary of clusters
        if graph is None:
            graph = self.graph
        return graph[self.clusters_key]

    def get_nodes(self, graph=None):
        # Returns dictionary of nodes
        if graph is None:
            graph = self.graph
        return graph[self.nodes_key]

    def get_edges(self, graph=None):
        # Returns list of edges
        if graph is None:
            graph = self.graph
        return graph[self.edges_key]
    
    def is_node_attr(self, node_id, attr_key, graph=None):
        # Returns boolean indicating if an attribute(attr_key) belongs to the node with ID(node_id)
        return attr_key in list(self.get_nodes(graph=graph)[node_id].keys())

    def get_node_attr(self, node_id, attr_key, graph=None):
        # Returns the value of the attribute(attr_key) for the node with ID(node_id)
        return self.get_nodes(graph=graph)[node_id][attr_key]

    def get_cluster_ids(self, graph=None):
        # Returns list of clusters
        return list(self.get_clusters(graph=graph).keys())

    def get_cluster_rank_ids(self, cluster, graph=None):
        # Returns list of ranks for a given cluster
        return list(self.get_clusters(graph=graph)[cluster].keys())

    def get_cluster_rank_node_ids(self, cluster, rank, graph=None):
        # Returns list of node IDs for given cluster and rank
        return list(self.get_clusters(graph=graph)[cluster][rank])

    def get_node_ids(self, graph=None):
        # Returns list of node IDs
        return list(self.get_nodes(graph=graph).keys())
    
    def get_edge_ids(self, graph=None):
        # Returns list of edge IDs
        return list(self.get_edges(graph=graph).keys())
    
    def join_edge_id(self, from_id, to_id):
        # Returns an edge IDs(edge ID) from IDs(from_id) and IDs(to_id)
        return f"{from_id}{self.edge_sep}{to_id}"

    def split_edge_id(self, edge_id):
        # Returns IDs(from_id) and IDs(to_id) from an edge IDs(edge ID)
        from_id = edge_id.split(self.edge_sep)[0]
        to_id = edge_id.split(self.edge_sep)[1]
        return from_id, to_id

    def add_node(self, node_attr, node_id=None, graph=None):

        ### Generate random node ID(node_id) if none is provided
        if node_id == None:
            node_id = str(0)
            while node_id in self.get_node_ids(graph=graph):
                node_id = str(random.randint(0, len(self.get_node_ids(graph=graph))+1))

        # Adds a node with ID(node_id) and attributes(node_attr) to the graph
        self.get_nodes(graph=graph)[node_id] = node_attr

        cluster_id = self.get_node_attr(node_id, self.cluster_attr, graph=graph)
        rank_id = self.get_node_attr(node_id, self.rank_attr, graph=graph)

        # Add node to the corresponding cluster and rank
        if cluster_id not in self.get_cluster_ids(graph=graph):
            self.get_clusters(graph=graph)[cluster_id] = {}
        if rank_id not in self.get_cluster_rank_ids(cluster_id, graph=graph):
            self.get_clusters(graph=graph)[cluster_id][rank_id] = []

        if node_id not in self.get_cluster_rank_node_ids(cluster_id, rank_id, graph=graph):
            self.get_clusters(graph=graph)[cluster_id][rank_id] += [node_id]

        if graph is not None:
            return graph

    def remove_node(self, node_id, graph=None):
        # Removes a node with ID(node_id) from the graph
        cluster_id = self.get_node_attr(node_id, self.cluster_attr, graph=graph)
        rank_id = self.get_node_attr(node_id, self.rank_attr, graph=graph)

        if node_id in self.get_node_ids(graph=graph):
            del self.get_nodes(graph=graph)[node_id]

            # Remove node from its corresponding cluster and rank
            if cluster_id in self.get_cluster_ids(graph=graph):
                cluster_rank_ids = self.get_cluster_rank_ids(cluster_id, graph=graph)
                if rank_id in cluster_rank_ids:
                    cluster_rank_node_ids = self.get_cluster_rank_node_ids(cluster_id, rank_id, graph=graph)
                    self.get_clusters(graph=graph)[cluster_id][rank_id] = [n for n in cluster_rank_node_ids if n != node_id]
                    if len(cluster_rank_node_ids) == 1:
                        del self.get_clusters(graph=graph)[cluster_id][rank_id]
                        if len(cluster_rank_ids) == 1:
                            del self.get_clusters(graph=graph)[cluster_id]

            # Remove edges connected to the node
            for edge_id in self.get_edge_ids(graph=graph):
                from_id, to_id = self.split_edge_id(edge_id)
                if node_id in [from_id, to_id]:
                    graph = self.remove_edge(from_id, to_id, graph=graph)

        if graph is not None:
            return graph

    def add_edge(self, from_id, to_id, edge_attr={}, graph=None):
        # Adds an edge between nodes with IDs(from_id) and IDs(to_id)
        self.get_edges(graph=graph)[self.join_edge_id(from_id, to_id)] = edge_attr

        if graph is not None:
            return graph

    def remove_edge(self, from_id, to_id, graph=None):
        # Removes an edge between nodes with IDs(from_id) and IDs(to_id)
        edge_id = self.join_edge_id(from_id, to_id)
        if edge_id in self.get_edge_ids(graph=graph):
            del self.get_edges(graph=graph)[edge_id]

        if graph is not None:
            return graph

    def get_subgraph(self, subgraph_node_ids):
        # Returns a subgraph containing only the specified subgraph_node_ids

        subgraph = {self.clusters_key: {}, self.nodes_key: {}, self.edges_key: {}}

        if len(subgraph_node_ids) > 0:
            subgraph = {self.clusters_key: deepcopy(self.get_clusters()), 
                        self.nodes_key: deepcopy(self.get_nodes()), 
                        self.edges_key: deepcopy(self.get_edges())}
            subgraph = deepcopy(self.graph)
            for node_id in self.get_node_ids():
                if node_id not in subgraph_node_ids:
                    subgraph = self.remove_node(node_id, graph=subgraph)

        return subgraph

    def prep_text(self, text, words_per_text=5, words_per_text_line=3):
        # Reformats a text string into chunks of words_per_text_line words, up to words_per_text total
        words = text.split()
        total_words = min(len(words), words_per_text)
        formatted_words = []

        for i in range(0, total_words, words_per_text_line):
            chunk = words[i:i + words_per_text_line]
            formatted_words.append(' '.join(chunk))

            if i + words_per_text_line >= words_per_text:
                formatted_words.append('...')
                break

        return '\n'.join(formatted_words)

    def build_digraph(self, graph=None,
                      cluster_fillcolor='lightgrey', cluster_fontcolor='black', 
                      rank_fillcolor='white', rank_fontcolor='black', 
                      node_fillcolor='black', node_fontcolor='white', 
                      node_shape='box', node_style='rounded,filled',
                      rankdir_lr=True, words_per_node=5, words_per_node_line=3):
        # Builds a Digraph object from the graph
        dot = Digraph()

        # Set graph rank direction to left-to-right if rankdir_lr is True
        if rankdir_lr:
            dot.graph_attr['rankdir'] = 'LR'

        # Create cluster and rank clusters
        for cluster_id, cluster_ranks in self.get_clusters(graph=graph).items():
            cluster_name = f"cluster_{cluster_id}"
            with dot.subgraph(name=cluster_name) as sub:
                sub.attr(label=cluster_id, labeljust='l', 
                         labelloc='t', style='rounded,filled', 
                         fillcolor=cluster_fillcolor, fontcolor=cluster_fontcolor, 
                         margin='10', penwidth='0', 
                         group=cluster_name)
                for rank_id, rank_node_ids in cluster_ranks.items():
                    cluster_rank_name = f"cluster_{cluster_id}_{rank_id}"
                    with sub.subgraph(name=cluster_rank_name) as rank_sub:
                        rank_sub.attr(label=rank_id, labeljust='l', 
                                      labelloc='t', style='rounded,filled', 
                                      fillcolor=rank_fillcolor, fontcolor=rank_fontcolor, 
                                      margin='10', penwidth='0', 
                                      group=cluster_rank_name)
                        for node_id in rank_node_ids:
                            node_attr = {self.fillcolor_attr: node_fillcolor,
                                         self.fontcolor_attr: node_fontcolor,
                                         self.shape_attr: node_shape,
                                         self.style_attr: node_style}
                            
                            for attr in list(node_attr.keys()):
                                if self.is_node_attr(node_id, attr, graph=graph):
                                    node_attr[attr] = self.get_node_attr(node_id, attr, graph=graph)

                            rank_sub.node(node_id, f"{self.prep_text(self.get_nodes(graph=graph)[node_id][self.text_attr], words_per_text_line=words_per_node_line, words_per_text=words_per_node)}\n(ID: {node_id})", 
                                          style=node_attr[self.style_attr], fillcolor=node_attr[self.fillcolor_attr], 
                                          fontcolor=node_attr[self.fontcolor_attr], shape=node_attr[self.shape_attr], 
                                          penwidth='0', group=cluster_rank_name)
                        rank_sub.graph_attr[self.rank_attr] = 'same'

        # Create edges
        for edge_id, edge_attr in self.get_edges(graph=graph).items():
            from_id, to_id = self.split_edge_id(edge_id)
            select_attr = [self.label_attr, self.color_attr]
            present_attr = {}
            for attr_key in select_attr:
                attr_val = ""
                if attr_key in list(edge_attr.keys()):
                    attr_val = edge_attr[attr_key]
                present_attr[attr_key] = attr_val
            dot.edge(from_id, to_id, label=present_attr[self.label_attr], color=present_attr[self.color_attr])

        return dot