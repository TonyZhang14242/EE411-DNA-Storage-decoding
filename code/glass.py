from collections import defaultdict
from reedsolo import RSCodec
from droplet import Droplet
import numpy as np
import operator, random, math
class Glass:
    def __init__(self, num_chunks):
        self.entries = []
        self.droplets = set()
        self.num_chunks = num_chunks
        self.chunks = [None] * num_chunks
        self.header_size = 4
        self.rs_size = 5
        self.chunk_to_droplets = defaultdict(set)
        self.done_segments = set()
        self.RSCodec = RSCodec(self.rs_size)
        self.seen_seeds = set()
        self.state = 1
        self.K_int = int(self.num_chunks)
        self.K = float(self.num_chunks)
        self.S = 0.1 * math.log(self.K/0.05) * math.sqrt(self.K)
        self.cdf = self._gen_rsd_cdf(self.num_chunks, self.S, 0.05)
        #self.PRNG = PRNG(K = self.num_chunks, delta = 0.05, c = 0.1, np = False)    

    def dna_to_int_arr(self, dna_str):
        #print(dna_str)
        num = dna_str.replace('A','0').replace('C','1').replace('G','2').replace('T','3')
        #print(num)
        s = ''.join('{0:02b}'.format(int(num[t])) for t in range(0, len(num),1))
        #print(s)
        data = [int(s[t:t+8],2) for t in range(0,len(s), 8)]
        #print(data)
        return data
    
    def get_src_blocks_wrap(self):
        random.seed(self.state)
        p = random.random()
        d = self._sample_d(p)
        nums = random.sample(range(self.K_int), d)
        return d, nums
    
    def _sample_d(self,p):
        for ix, v in enumerate(self.cdf):
            if v > p:
                return ix + 1
        return ix + 1
    
    def _gen_rsd_cdf(self,K, S, delta):
        pivot = int(math.floor(K/S))
        val1 =  [S/K * 1/d for d in range(1, pivot)] 
        val2 =  [S/K * math.log(S/delta)] 
        val3 =  [0 for d in range(pivot, K)] 
        tau = val1 + val2 + val3
        rho = [1.0/K] + [1.0/(d*(d-1)) for d in range(2, K+1)]
        Z = sum(rho) + sum(tau)
        mu = [(rho[d] + tau[d])/Z for d in range(K)]
        cdf = np.cumsum(mu)
        return cdf

    def add_dna(self, dna_str):
        data = self.dna_to_int_arr(dna_str)
        try:
            #evaluate the error correcting code
            data_corrected = list(self.RSCodec.decode(data)[0])
        except:
            #could not correct the code
            return -1, None 
        seed_array = data_corrected[:self.header_size]
        #print(seed_array)
        seed = sum([int(x)*256**i for i, x in enumerate(seed_array[::-1])])
        #print(seed)
        payload = data_corrected[self.header_size:]

        #more error detection (filter seen seeds)
        if seed in self.seen_seeds:
            return -1, None
        else:
            self.seen_seeds.add(seed)

        self.state = seed
        ix_samples = self.get_src_blocks_wrap()[1]
        #print(ix_samples)

        d = Droplet(payload, seed, ix_samples)
        self.addDroplet(d)
        return seed, data

    def addDroplet(self, droplet):
        self.droplets.add(droplet)
        for chunk_num in droplet.num_chunks:
            self.chunk_to_droplets[chunk_num].add(droplet) #we document for each chunk all connected droplets        
        self.message_passing(droplet) #one round of message passing

    def message_passing(self, droplet):
        '''
        If the droplet contains inferred segments, the algorithm will XOR these segments from the droplet
        and remove them from the identity list of droplet
        '''
        
        for chunk_num in (droplet.num_chunks & self.done_segments):        
            droplet.data = list(map(operator.xor, droplet.data, self.chunks[chunk_num]))
            #subtract (ie. xor) the value of the solved segment from the droplet.
            droplet.num_chunks.remove(chunk_num)
            self.chunk_to_droplets[chunk_num].discard(droplet)          

        '''
        solving segments when the droplet have exactly 1 segment
        If the droplet has only one segment left in the list, 
        the algorithm will set the segment to the droplet's data payload
        '''
        
        if len(droplet.num_chunks) == 1: 
            lone_chunk = droplet.num_chunks.pop() 
            self.chunks[lone_chunk] = droplet.data 
            self.done_segments.add(lone_chunk) 
            self.droplets.discard(droplet) 
            self.chunk_to_droplets[lone_chunk].discard(droplet) 
            
            '''
            Recursively propagate the new inferred segment to all previous droplets
            until no more updates are made.
            '''
            for other_droplet in self.chunk_to_droplets[lone_chunk].copy():
                self.message_passing(other_droplet)
    

