import glob
import argparse
import docx

def get_text(filename):
    doc = docx.Document(filename)
    return '\n'.join([para.text for para in doc.paragraphs])

def is_valid_doc(filename):
    return True
    
if __name__=="__main__":
    for item_path in glob.iglob(target_dir):
        if is_valid_doc(item_path):
            pass # TODO:
            
        
    