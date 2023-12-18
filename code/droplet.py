import random
import struct


class Droplet:
    def __init__(self, data, seed, num_chunks = None, rs = 0, rs_obj = None, degree = None):

        self.data = data
        self.seed = seed

        self.num_chunks = set(num_chunks)

        self.rs = rs
        self.rs_obj = rs_obj
        self.degree = degree
        self.DNA = None