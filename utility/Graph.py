
class Graph:
    def __init__(self, train_graph_file_name=None, train_dictionary=None, graph=None):
        if train_graph_file_name is None and train_dictionary is None and graph is None:
            self.out_links = dict()
            self.node_count = 0
            self.dictionary = {}
        elif train_graph_file_name is not None and train_dictionary is not None and graph is None:
            self.out_links = dict()
            self.node_count = 0
            self.dictionary = dict()
            nodes = set()
            key_set = train_dictionary.keys()

            with open(file=train_graph_file_name, mode='r') as fp:
                for line in fp.readlines():
                    pair = line.strip('\n').split('#')
                    start_node = int(pair[0])
                    end_node = int(pair[1])

                    if start_node in key_set and end_node in key_set:
                        nodes.add(start_node)
                        nodes.add(end_node)

                        if start_node in self.out_links.keys():
                            outlink = self.out_links[start_node]
                        else:
                            outlink = set()
                        outlink.add(end_node)
                        self.out_links[start_node] = outlink
            self.node_count = len(nodes)

        elif train_graph_file_name is None and train_dictionary is None and graph is not None:
            self.out_links = dict()
            self.dictionary = dict()
            self.node_count = 0

            out_links = graph.getoutlinks()
            key_set = out_links.keys()

            for end_node in key_set:
                this_in_links = set()
                in_links = out_links[end_node]
                for start_node in in_links:
                    this_in_links.add(start_node)
                self.out_links[end_node] = this_in_links

            dictionary = graph.get_dictionary()
            dict_key_set = dictionary.keys()

            for key in dict_key_set:
                val = dictionary[key]
                self.dictionary[key] = val

            self.set_num_nodes(graph.get_num_nodes())

    def combine(self, graph, dictionary):
        tmp_out_links = graph.getoutlinks()
        key = tmp_out_links.keys()

        for start_node in key:
            out_links = tmp_out_links[start_node]
            artifact = dictionary[start_node]
            id_start_node = self.extract_key(artifact)

            for end_node in out_links:
                artifact = dictionary[end_node]

                id_end_node = self.extract_key(artifact)

                if id_start_node in self.out_links.keys():
                    main_out_links = self.out_links[id_start_node]
                else:
                    main_out_links = set()
                main_out_links.add(id_end_node)
                self.out_links[id_start_node] = main_out_links

        nodes = set()
        key_set = self.out_links.keys()

        for start_node in key_set:
            nodes.add(start_node)
            main_out_links = self.out_links[start_node]
            for end_node in main_out_links:
                nodes.add(end_node)

        self.node_count = len(nodes)

    def get_dictionary(self):
        return self.dictionary

    def getoutlinks(self):
        return self.out_links

    def set_num_nodes(self, num_node):
        self.node_count = num_node

    def get_num_nodes(self):
        return self.node_count

    def extract_key(self, s):
        if s in self.dictionary.keys():
            return self.dictionary[s]
        else:
            size = len(self.dictionary)
            self.dictionary[s] = size
            return size
