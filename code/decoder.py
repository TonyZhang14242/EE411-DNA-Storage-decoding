from reedsolo import RSCodec
import numpy as np
from glass import Glass
from collections import defaultdict
import os, sys, logging
class Decoder():
    def __init__(self, input_file, output_file, chunk_num, header_size, rs_size, chunk_data_size):
        self.in_file = input_file
        self.out_file = output_file
        self.chunk_num = chunk_num
        self.header_size = header_size
        self.rs_size = rs_size
        self.chunk_data_size = chunk_data_size
        self.glass = Glass(self.chunk_num)
    
    def read_input_file(self):
        try: 
            f = open(self.in_file, 'r')
        except:
            print("{self.file_in} file not found")
            sys.exit(0)
        return f

    def decoding(self):
        line = 0
        errors = 0
        f = self.read_input_file()
        seen_seeds = defaultdict(int)
        while True:
            dna = f.readline().rstrip('\n')
            #print(dna)
            line += 1
            seed, data = self.glass.add_dna(dna)
            if line > 2500:
                print("Error occurred when decoding!!!")
                exit(1)
            if seed == -1: #Exclude the sequence with error, which is founded by RS code
                errors += 1
            else:
                seen_seeds[seed] += 1 
            
            if line % 100 == 0:
                print("Already read {} lines, {} chunks are done. Number of errors: {} ({}%)"
                      .format(line, len(self.glass.done_segments), errors, errors/float(line)*100))
            if self.glass.num_chunks == len(self.glass.done_segments):
                print("Already read {} lines, {} chunks are done. Number of errors: {} ({}%)"
                      .format(line, len(self.glass.done_segments), errors, errors/float(line)*100))
                print("Done!")
                break
        f.close()
        
        res = ''
        for x in self.glass.chunks:
            res += ''.join(map(chr, x))
        with open(self.out_file, 'wb') as f:
            f.write(res)

if __name__ == '__main__':
    in_file = './src/50-SF.txt'
    out_file = './output/50-SF.jpg'
    Decoder(input_file=in_file, output_file=out_file, chunk_num=1494, header_size=4, rs_size=5, chunk_data_size=16).decoding()