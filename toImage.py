import argparse
import json
import os
import sys

from pdf2image import convert_from_path


def convert_batch_pdfs_to_images(ip_dir, op_dir):
    '''
    params
        ip_dir : The input directory which contains the pdfs.
        op_dir : The output directory to store the images.

    returns
        infodict : The status of pdfs converted.
    '''
    if not os.path.exists(ip_dir):
        os.makedirs(ip_dir)
    if not os.path.exists(op_dir):
        os.makedirs(op_dir)
        
    files = os.listdir(os.path.dirname(os.path.abspath(__file__)))
    infodict = {"filesdone": [], "counter": 0}

    if "info.json" in files:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "info.json"), "r") as infofile:
            infodict = json.load(infofile)

    files = os.listdir(ip_dir)
    for singlefile in files:
        if singlefile not in infodict["filesdone"] and singlefile.endswith('.pdf'):
            filecnt = infodict["counter"] + 1
            infodict["filesdone"].append(singlefile)
            pdf = convert_from_path(os.path.join(ip_dir, singlefile))
            cnt = 1
            for page in pdf:
                page.save(os.path.join(op_dir, str(
                    filecnt)+"_"+str(cnt)+".jpg"), "JPEG")
                cnt += 1
            infodict["counter"] = filecnt
            print("Converted "+singlefile+" to images")
    
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "info.json"), "w") as infofile:
        json.dump(infodict, infofile)

    return infodict

def convert_single_pdf_to_images(pdf_path, op_dir):
    '''
    params
        pdf_path: The pdf path.
        op_dir : The output directory to store the images.
    '''

    if not os.path.exists(op_dir):
        os.makedirs(op_dir)

    pdf = convert_from_path(pdf_path)
    cnt = 1
    for page in pdf:
        page.save(os.path.join(op_dir,str(cnt)+".jpg"), "JPEG")
        cnt+=1

    print('converted '+pdf_path+' to images')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Convert a directory of pdfs into images.")
    parser.add_argument('input_dir', type=str,
                        help="Relative path to the input directory which contains the pdfs.")
    parser.add_argument('output_dir', type=str,
                        help="Relative path to the output directory to store the images.")

    args = parser.parse_args()
    ip_dir = args.input_dir
    op_dir = args.output_dir
    status = convert_pdfs_to_images(ip_dir, op_dir)
    print("completed : ")
    print(json.dumps(status, indent=2))