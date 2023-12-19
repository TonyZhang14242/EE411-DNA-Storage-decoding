class Droplet:
    def __init__(self, data, seed, num_chunks = None, rs = 0):
        self.data = data
        self.seed = seed
        self.num_chunks = set(num_chunks)
        self.rs = rs