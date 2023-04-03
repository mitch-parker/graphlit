from graphviz import Digraph


class Graph():
    def __init__(self, clusters={}, nodes={}, edges=[]):

        self.id_key = "id"

        self.clusters_key = "clusters"
        self.nodes_key = "nodes"
        self.edges_key = "edges"

        self.label_attr = "label"
        self.rank_attr = "rank"
        self.text_attr = "text"

        self.from_key = "from"
        self.to_key = "to"

        self.graph = {self.clusters_key: clusters, self.nodes_key: nodes, self.edges_key: edges}

    def get_clusters(self):

        return self.graph[self.clusters_key]
    

    def get_nodes(self):

        return self.graph[self.nodes_key]
    

    def get_edges(self):

        return self.graph[self.edges_key]
    

    def get_node_attr(self, node_id, attr_key):

        return self.get_nodes()[node_id][attr_key]
    

    def get_node_label(self, node_id):

        return self.get_node_attr(node_id, self.label_attr)
    

    def get_node_rank(self, node_id):

        return self.get_node_attr(node_id, self.rank_attr)
    

    def get_node_text(self, node_id):

        return self.get_node_attr(node_id, self.text_attr)
    

    def get_cluster_labels(self):

        return list(self.get_clusters().keys())
    
    
    def get_label_ranks(self, label):

        return list(self.graph[self.clusters_key][label].keys())
    
    
    def get_label_rank_node_ids(self, label, rank):

        return list(self.graph[self.clusters_key][label][rank])
    

    def get_node_ids(self):

        return list(self.get_nodes().keys())
    

    def add_node(self, node_id, node_attr):

        self.graph[self.nodes_key][node_id] = node_attr
    
        label = self.get_node_label(node_id)
        rank = self.get_node_rank(node_id)

        if label not in self.get_cluster_labels():
            self.graph[self.clusters_key][label] = {}
        if rank not in self.get_label_ranks(label):
            self.graph[self.clusters_key][label][rank] = []

        if node_id not in self.get_label_rank_node_ids(label, rank):
            self.graph[self.clusters_key][label][rank] += [node_id]
     

    def remove_node(self, node_id):

        label = self.get_node_label(node_id)
        rank = self.get_node_rank(node_id)

        if node_id in self.get_node_ids():
            del self.graph[self.nodes_key][node_id]

            self.graph[self.edges_key] = [
                edge for edge in self.get_edges() if edge[self.from_key] != node_id and edge[self.to_key] != node_id
            ]

            if label in self.get_cluster_labels():
                if rank in self.get_label_ranks(label):
                    self.graph[self.clusters_key][label][rank] = [node for node in self.get_label_rank_node_ids(label, rank) if node != node_id]


    def add_edge(self, from_id, to_id):
        self.graph[self.edges_key].append({self.from_key: from_id, self.to_key: to_id})


    def remove_edge(self, from_id, to_id):
        self.graph[self.edges_key] = [edge for edge in self.get_edges() if not (edge[self.from_key] == from_id and edge[self.to_key] == to_id)]


    def get_labels_subgraph(self, subgraph_labels):

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
    
    def prep_digraph_text(self, text, n=3, x=10):
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

    
    def build_digraph(self,digraph=None, rankdir_lr=True):
        dot = Digraph()
        if digraph == None:
            digraph = self.graph
        
        if rankdir_lr:
            dot.graph_attr['rankdir'] = 'LR'

        for label, label_ranks in digraph[self.clusters_key].items():

            with dot.subgraph(name=f"cluster_{label}") as sub:
                sub.attr(label=label, labeljust='l', labelloc='t', style='filled', fillcolor='lightgrey', margin="10")

                for rank, rank_node_ids in label_ranks.items():
                    with sub.subgraph(name=f"cluster_{label}_{rank}") as rank_sub:
                        rank_sub.attr(label=rank, labeljust='l', labelloc='t', style='filled', fillcolor='white', margin="5")

                        for i, node_id in enumerate(rank_node_ids):
                            n_label = f"{self.prep_digraph_text(digraph[self.nodes_key][node_id][self.text_attr])}\n(ID: {node_id})"
                            rank_sub.node(node_id, n_label, shape='ellipse')
                            if i > 0: 
                                rank_sub.edge(rank_node_ids[i - 1], node_id, style='invis') 
                        rank_sub.graph_attr[self.rank_attr] = 'same'

        for edge in digraph[self.edges_key]:
            dot.edge(edge[self.from_key], edge[self.to_key])

        return dot

    