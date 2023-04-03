from graphviz import Digraph

class Graph():
    def __init__(self, clusters={}, nodes={}, edges=[]):
        # Constants
        self.id_key = "id"
        self.clusters_key = "clusters"
        self.nodes_key = "nodes"
        self.edges_key = "edges"
        self.label_attr = "label"
        self.rank_attr = "rank"
        self.text_attr = "text"
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

    def get_node_attr(self, node_id, attr_key):
        # Returns the value of the attribute(attr_key) for the node with ID(node_id)
        return self.get_nodes()[node_id][attr_key]

    def get_node_label(self, node_id):
        # Returns the label of the node with ID(node_id)
        return self.get_node_attr(node_id, self.label_attr)

    def get_node_rank(self, node_id):
        # Returns the rank of the node with ID(node_id)
        return self.get_node_attr(node_id, self.rank_attr)

    def get_node_text(self, node_id):
        # Returns the text of the node with ID(node_id)
        return self.get_node_attr(node_id, self.text_attr)

    def get_cluster_labels(self):
        # Returns list of cluster labels
        return list(self.get_clusters().keys())

    def get_label_ranks(self, label):
        # Returns list of ranks for a given cluster label
        return list(self.graph[self.clusters_key][label].keys())

    def get_label_rank_node_ids(self, label, rank):
        # Returns list of node IDs for given cluster label and rank
        return list(self.graph[self.clusters_key][label][rank])

    def get_node_ids(self):
        # Returns list of node IDs
        return list(self.get_nodes().keys())

    def add_node(self, node_id, node_attr):
        # Adds a node with ID(node_id) and attributes(node_attr) to the graph
        self.graph[self.nodes_key][node_id] = node_attr

        label = self.get_node_label(node_id)
        rank = self.get_node_rank(node_id)

        # Add node to the corresponding cluster and rank
        if label not in self.get_cluster_labels():
            self.graph[self.clusters_key][label] = {}
        if rank not in self.get_label_ranks(label):
            self.graph[self.clusters_key][label][rank] = []

        if node_id not in self.get_label_rank_node_ids(label, rank):
            self.graph[self.clusters_key][label][rank] += [node_id]

    def remove_node(self, node_id):
        # Removes a node with ID(node_id) from the graph
        label = self.get_node_label(node_id)
        rank = self.get_node_rank(node_id)

        if node_id in self.get_node_ids():
            del self.graph[self.nodes_key][node_id]

            # Remove edges connected to the node
            self.graph[self.edges_key] = [
                edge for edge in self.get_edges() if edge[self.from_key] != node_id and edge[self.to_key] != node_id
            ]

            # Remove node from its corresponding cluster and rank
            if label in self.get_cluster_labels():
                if rank in self.get_label_ranks(label):
                    self.graph[self.clusters_key][label][rank] = [node for node in self.get_label_rank_node_ids(label, rank) if node != node_id]

    def add_edge(self, from_id, to_id):
        # Adds an edge between nodes with IDs(from_id) and IDs(to_id)
        self.graph[self.edges_key].append({self.from_key: from_id, self.to_key: to_id})

    def remove_edge(self, from_id, to_id):
        # Removes an edge between nodes with IDs(from_id) and IDs(to_id)
        self.graph[self.edges_key] = [edge for edge in self.get_edges() if not (edge[self.from_key] == from_id and edge[self.to_key] == to_id)]

    def get_labels_subgraph(self, subgraph_labels):
        # Returns a subgraph containing only the specified subgraph_labels
        subgraph = {self.clusters_key: {}, self.nodes_key: {}, self.edges_key: []}

        subgraph_node_ids = []

        for label in subgraph_labels:
            label_ranks = self.graph[self.clusters_key][label]
            subgraph[self.clusters_key][label] = label_ranks
            for rank in list(label_ranks.keys()):
                rank_node_ids = label_ranks[rank]
                for node_id in rank_node_ids:
                    subgraph[self.nodes_key][node_id] = self.graph[self.nodes_key][node_id]
                subgraph_node_ids += rank_node_ids

        subgraph_edges = []

        if len(self.get_edges()) > 0:
            for edge in self.graph[self.edges_key]:
                from_id = edge[self.from_key]
                to_id = edge[self.to_key]
                if (to_id in subgraph_node_ids) and (from_id in subgraph_node_ids):
                    subgraph_edges += [{self.from_key: from_id, self.to_key: to_id}]
            subgraph[self.edges_key] = subgraph_edges

        return subgraph

    def prep_text(self, text, n=3, x=5):
        # Reformats a text string into chunks of n words, up to x words total
        words = text.split()
        total_words = min(len(words), x)
        formatted_words = []

        for i in range(0, total_words, n):
            chunk = words[i:i + n]
            formatted_words.append(' '.join(chunk))

            if i + n >= x:
                formatted_words.append('...')
                break

        return '\n'.join(formatted_words)

    def build_digraph(self, digraph=None, rankdir_lr=True):
        # Builds a Digraph object from the graph
        dot = Digraph()
        if digraph == None:
            digraph = self.graph

        # Set graph rank direction to left-to-right if rankdir_lr is True
        if rankdir_lr:
            dot.graph_attr['rankdir'] = 'LR'

        # Create cluster and rank subgraphs
        for label, label_ranks in digraph[self.clusters_key].items():
            label_name = f"cluster_{label}"
            with dot.subgraph(name=label_name) as sub:
                sub.attr(label=label, labeljust='l', labelloc='t', style='rounded,filled', fillcolor='lightgrey', margin='10', group=label_name)
                for rank, rank_node_ids in label_ranks.items():
                    label_rank_name = f"cluster_{label}_{rank}"
                    with sub.subgraph(name=label_rank_name) as rank_sub:
                        rank_sub.attr(label=rank, labeljust='l', labelloc='t', style='rounded,filled', fillcolor='white', margin='10', group=label_rank_name)
                        for node_id in rank_node_ids:
                            rank_sub.node(node_id, f"{self.prep_text(digraph[self.nodes_key][node_id][self.text_attr])}\n(ID: {node_id})", style='filled', shape='box', fillcolor='black', fontcolor='white', group=label_rank_name)
                        rank_sub.graph_attr[self.rank_attr] = 'same'

        # Create edges
        for edge in digraph[self.edges_key]:
            dot.edge(edge[self.from_key], edge[self.to_key])

        return dot