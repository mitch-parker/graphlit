from graphviz import Digraph
import random

class Graph():
    def __init__(self, clusters={}, nodes={}, edges=[]):
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
        self.from_key = "from"
        self.to_key = "to"

        # Graph structure
        self.graph = {self.clusters_key: clusters, self.nodes_key: nodes, self.edges_key: edges}

    def get_clusters(self):
        # Returns dictionary of clusters
        return self.graph[self.clusters_key]

    def get_nodes(self):
        # Returns dictionary of nodes
        return self.graph[self.nodes_key]

    def get_edges(self):
        # Returns list of edges
        return self.graph[self.edges_key]
    
    def is_node_attr(self, node_id, attr_key):
        # Returns boolean indicating if an attribute(attr_key) belongs to the node with ID(node_id)
        return attr_key in list(self.get_nodes()[node_id].keys())

    def get_node_attr(self, node_id, attr_key):
        # Returns the value of the attribute(attr_key) for the node with ID(node_id)
        return self.get_nodes()[node_id][attr_key]

    def get_node_cluster(self, node_id):
        # Returns the cluster of the node with ID(node_id)
        return self.get_node_attr(node_id, self.cluster_attr)

    def get_node_rank(self, node_id):
        # Returns the rank of the node with ID(node_id)
        return self.get_node_attr(node_id, self.rank_attr)

    def get_node_text(self, node_id):
        # Returns the text of the node with ID(node_id)
        return self.get_node_attr(node_id, self.text_attr)
    
    def get_node_fillcolor(self, node_id):
        # Returns the fillcolor of the node with ID(node_id)
        return self.get_node_attr(node_id, self.fillcolor_attr)
    
    def get_node_fontcolor(self, node_id):
        # Returns the fontcolor of the node with ID(node_id)
        return self.get_node_attr(node_id, self.fontcolor_attr)
    
    def get_node_shape(self, node_id):
        # Returns the shape of the node with ID(node_id)
        return self.get_node_attr(node_id, self.shape_attr)
    
    def get_node_style(self, node_id):
        # Returns the style of the node with ID(node_id)
        return self.get_node_attr(node_id, self.style_attr)

    def get_cluster_ids(self):
        # Returns list of clusters
        return list(self.get_clusters().keys())

    def get_cluster_rank_ids(self, cluster):
        # Returns list of ranks for a given cluster
        return list(self.graph[self.clusters_key][cluster].keys())

    def get_cluster_rank_node_ids(self, cluster, rank):
        # Returns list of node IDs for given cluster and rank
        return list(self.graph[self.clusters_key][cluster][rank])

    def get_node_ids(self):
        # Returns list of node IDs
        return list(self.get_nodes().keys())

    def add_node(self, node_attr, node_id=None):

        ### Generate random node ID(node_id) if none is provided
        if node_id == None:
            node_id = str(0)
            while node_id in self.get_node_ids():
                node_id = str(random.randint(0, len(self.get_node_ids())+1))

        # Adds a node with ID(node_id) and attributes(node_attr) to the graph
        self.graph[self.nodes_key][node_id] = node_attr

        cluster_id = self.get_node_cluster(node_id)
        rank_id = self.get_node_rank(node_id)

        # Add node to the corresponding cluster and rank
        if cluster_id not in self.get_cluster_ids():
            self.graph[self.clusters_key][cluster_id] = {}
        if rank_id not in self.get_cluster_rank_ids(cluster_id):
            self.graph[self.clusters_key][cluster_id][rank_id] = []

        if node_id not in self.get_cluster_rank_node_ids(cluster_id, rank_id):
            self.graph[self.clusters_key][cluster_id][rank_id] += [node_id]

    def remove_node(self, node_id):
        # Removes a node with ID(node_id) from the graph
        cluster_id = self.get_node_cluster(node_id)
        rank_id = self.get_node_rank(node_id)

        if node_id in self.get_node_ids():
            del self.graph[self.nodes_key][node_id]

            # Remove edges connected to the node
            self.graph[self.edges_key] = [
                edge for edge in self.get_edges() if edge[self.from_key] != node_id and edge[self.to_key] != node_id
            ]

            # Remove node from its corresponding cluster and rank
            if cluster_id in self.get_cluster_ids():
                if rank_id in self.get_cluster_rank_ids(cluster_id):
                    self.graph[self.clusters_key][cluster_id][rank_id] = [node for node in self.get_cluster_rank_node_ids(cluster_id, rank_id) if node != node_id]

    def add_edge(self, from_id, to_id):
        # Adds an edge between nodes with IDs(from_id) and IDs(to_id)
        self.graph[self.edges_key].append({self.from_key: from_id, self.to_key: to_id})

    def remove_edge(self, from_id, to_id):
        # Removes an edge between nodes with IDs(from_id) and IDs(to_id)
        self.graph[self.edges_key] = [edge for edge in self.get_edges() if not (edge[self.from_key] == from_id and edge[self.to_key] == to_id)]

    def get_subgraph_clusters(self, clusters):
        # Returns a subgraph containing only the specified subgraph_clusters
        subgraph = {self.clusters_key: {}, self.nodes_key: {}, self.edges_key: []}

        subgraph_node_ids = []

        for cluster_id in clusters:
            cluster_ranks = self.graph[self.clusters_key][cluster_id]
            subgraph[self.clusters_key][cluster_id] = cluster_ranks
            for rank_id in list(cluster_ranks.keys()):
                rank_node_ids = cluster_ranks[rank_id]
                for node_id in rank_node_ids:
                    subgraph[self.nodes_key][node_id] = self.graph[self.nodes_key][node_id]
                subgraph_node_ids += rank_node_ids

        subgraph_edges = []

        if len(self.get_edges()) > 0:
            for edge in self.graph[self.edges_key]:
                if (edge[self.from_key] in subgraph_node_ids) and (edge[self.to_key] in subgraph_node_ids):
                    subgraph_edges += [edge]
            subgraph[self.edges_key] = subgraph_edges

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


    def build_digraph(self, digraph=None, 
                      cluster_fillcolor='lightgrey', cluster_fontcolor='black', 
                      rank_fillcolor='white', rank_fontcolor='black', 
                      node_fillcolor='black', node_fontcolor='white', 
                      node_shape='box', node_style='rounded,filled',
                      rankdir_lr=True, words_per_node=5, words_per_node_line=3):
        # Builds a Digraph object from the graph
        dot = Digraph()
        if digraph == None:
            digraph = self.graph

        # Set graph rank direction to left-to-right if rankdir_lr is True
        if rankdir_lr:
            dot.graph_attr['rankdir'] = 'LR'

        # Create cluster and rank clusters
        for cluster_id, cluster_ranks in digraph[self.clusters_key].items():
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
                                if self.is_node_attr(node_id, attr):
                                    node_attr[attr] = self.get_node_attr(node_id, attr)

                            rank_sub.node(node_id, f"{self.prep_text(digraph[self.nodes_key][node_id][self.text_attr], words_per_text_line=words_per_node_line, words_per_text=words_per_node)}\n(ID: {node_id})", 
                                          style=node_attr[self.style_attr], fillcolor=node_attr[self.fillcolor_attr], 
                                          fontcolor=node_attr[self.fontcolor_attr], shape=node_attr[self.shape_attr], 
                                          penwidth='0', group=cluster_rank_name)
                        rank_sub.graph_attr[self.rank_attr] = 'same'

        # Create edges
        for edge in digraph[self.edges_key]:
            dot.edge(edge[self.from_key], edge[self.to_key])

        return dot