#coding=UTF-8
from decoder import Decoder
from PIL import Image, ImageChops
def main():
    in_file_dir = './src/50-SF.txt'
    origin_file_dir = './src/神奈川冲浪.jpg'
    out_file_dir = './output/50-SF.jpg'
    d = Decoder(input_file=in_file_dir, output_file=out_file_dir, 
                chunk_num=1494, header_size=4, rs_size=5, chunk_data_size=16)
    d.decoding()
    try:
        print('Checking integrity of output image...')
        check_integrity(origin_file_dir, out_file_dir)
    except:
        print('Error occurred when trying to compare origin picture to output picture.')
        exit(1)

def check_integrity(origin, out):
    image_origin = Image.open(origin)
    image_out = Image.open(out)

    diff = ImageChops.difference(image_origin, image_out)
    print('Checking integrity completed.')
    if diff.getbbox() is None:
        print('No difference found between input image and output image!')
    else:
        print('Oops, there are some differences between two pictures!')

if __name__ == '__main__':
    main()