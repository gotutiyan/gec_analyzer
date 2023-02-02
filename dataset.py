import errant
import configparser
import argparse
from dataclasses import dataclass, field

def test():
    origs = ['This are gramamtical sentence .',
        'This are gramamtical sentence . dummy']
    cors = ['This is a grammatical sentence .',
        'This are gramamtical computer .']
    dataset = Dataset()
    dataset.from_raw_text(origs, cors)
    return dataset

def file_test():
    config = configparser.ConfigParser()
    config.read('config.ini')
    orig_list = load_file(config['FILES']['orig'])
    cor_list = load_file(config['FILES']['cor'])
    dataset = Dataset(orig_list, cor_list)
    return dataset

def load_file(file_path):
    sentences = []
    with open(file_path) as fp:
        for line in fp:
            sentences.append(line)
    return sentences
    
def load_annotator(lang):
    return errant.load(lang)

@dataclass
class Chunk:
    o_str: str
    c_str: str
    type: str
    is_highlight: bool

class SentenceDataset:
    '''This class handles original, references and hypotheses for a sentence.'''
    def __init__(self, id):
        self.id = id
        self.orig = ''
        self.refs_chunks = [] # 2d array (# references, # Chunk instances)
        self.hyps_chunks = [] # 2d array (# hypothesis, # Chunk instances)

    def update_n(self):
        self.n_refs = len(self.refs_chunks)
        self.n_hyps = len(self.hyps_chunks)
        
class Dataset:
    '''
    This class handles all sentences data.
    Each data of a sentence is handled by SentenceData instanse.
    '''
    def __init__(self):
        return

    def load(
        self,
        original_file=None,
        referece_files=None,
        hypothesis_files=None
    ):
        annotator = errant.load('en')
        if referece_files is not None:
            originals, ref_edits_lists = self.generate_edits_from_files(
                original_file,
                referece_files,
                annotator
            )
        if hypothesis_files is not None:
            originals, hyp_edits_lists = self.generate_edits_from_files(
                original_file,
                hypothesis_files,
                annotator
            )

        self.data = [SentenceDataset(id=i+1) for i in range(len(originals))]
        self.n_sents = len(originals)
        for i, orig in enumerate(originals):
            self.data[i].orig = orig
        
        if referece_files is not None:
            for ref_edits in ref_edits_lists: # loop for each reference
                for i, edits in enumerate(ref_edits): # loop for each sentence in the reference
                    self.data[i].refs_chunks.append(
                        self.make_chunks(
                            self.data[i].orig,
                            edits
                        )
                    )

        if hypothesis_files is not None:
            for hypo_edits in hyp_edits_lists:
                for i, edits in enumerate(hypo_edits):
                    self.data[i].hyps_chunks.append(
                        self.make_chunks(
                            self.data[i].orig,
                            edits
                        )
                    )
        for seq_dataset in self.data:
            seq_dataset.update_n()

    def generate_edits_from_files(self, orig_file, cor_files, annotator):
        edits_lists = []
        for file in cor_files:
            if file.split('.')[-1] == 'm2':
                ''' If M2 format'''
                ref_id = 0
                while True:
                    originals, edits_list = self.load_from_m2(file, ref_id=ref_id)
                    if edits_list == -1:
                        # There is no edit corresponding ref_id-th reference.
                        break
                    edits_lists.append(edits_list)
                    ref_id += 1
            else:
                '''If raw text'''
                originals = open(orig_file).read().rstrip().split('\n')
                hypothesis = open(file).read().rstrip().split('\n')
                edits_list = self.extract_edits(
                    origs=originals,
                    cors=hypothesis,
                    annotator=annotator
                )
                edits_lists.append(edits_list)
        return originals, edits_lists

    def load_from_m2(self, m2, ref_id):
        originals, edits_list = self.read_m2(m2, ref_id=ref_id)
        # self.type_set = self.make_type_set(self.edits_list)
        return originals, edits_list
        
    def read_m2(self, file, ref_id=0):
        m2_contetns = open(file).read().rstrip().split('\n\n')
        originals = []
        edits_list = []
        are_there_edits = False
        for m2_sent in m2_contetns:
            orig, *edits_m2 = m2_sent.split('\n')
            orig = orig[2:] # remove 'S '
            originals.append(orig)
            edits = []
            for edit_m2 in edits_m2:
                idx, e_type, c_str, _, _, id = edit_m2[2:].split('|||')
                if e_type == 'noop':
                    continue
                if int(id) != ref_id:
                    continue
                o_start, o_end = list(map(int, idx.split(' ')))
                edit = MyEdit()
                edit.o_start = o_start
                edit.o_end = o_end
                edit.o_str = ' '.join(orig.split(' ')[o_start:o_end])
                edit.c_str = c_str
                edit.type = e_type
                edits.append(edit)
            if edits != []:
                are_there_edits = True
            edits_list.append(edits)
        if not are_there_edits:
            edits_list = -1
        return originals, edits_list
    
    def extract_edits(self, origs, cors, annotator):
        edits_list = []
        for orig, cor in zip(origs, cors):
            edits = self.make_edits(orig, cor, annotator)
            edits_list.append(edits)
        return edits_list

    @staticmethod
    def make_type_set(edits_list):
        type_set = [set(), set()]
        for edits in edits_list:
            for edit in edits:
                type1 = edit.type.split(':')[0]
                type2 = ':'.join(edit.type.split(':')[1:])
                type_set[0].add(type1)
                type_set[1].add(type2)
        return type_set
        
    @staticmethod
    def make_edits(orig, cor, annotator):
        orig = annotator.parse(orig)
        cor = annotator.parse(cor)
        edits = annotator.annotate(orig, cor)
        return edits

    def make_chunks(self, orig, edits):
        orig_tokens = orig.split()
        chunks = []
        token_idx = 0
        edit_idx = 0
        len_orig_tokens = len(orig_tokens)
        len_edits = len(edits)
        while token_idx < len_orig_tokens:
            if edit_idx < len_edits and token_idx == edits[edit_idx].o_start:
                edit = edits[edit_idx]
                chunks.append(
                    Chunk(
                        o_str="φ" if edit.o_str == "" else edit.o_str,
                        c_str="φ" if edit.c_str == "" else edit.c_str,
                        type=edit.type,
                        is_highlight=True
                    )
                )
                token_idx = edit.o_end
                edit_idx += 1
            else:
                chunks.append(
                    Chunk(
                        o_str=orig_tokens[token_idx],
                        c_str=None,
                        type=None,
                        is_highlight=False
                    )
                )
                token_idx += 1
        return chunks
    
    def load_types(self, id='errant'):
        if id == 'errant':
            type3 = "R M U".split()
            type25 = "ADJ ADJ:FORM ADV CONJ CONTR DET MORPH NOUN "\
                "NOUN:INFL NOUN:NUM NOUN:POSS ORTH OTHER PART PREP "\
                "PRON PUNCT SPELL UNK VERB VERB:FORM VERB:INFL VERB:SVA VERB:TENSE WO".split()
        return type3, type25

class MyEdit():
    def __init__(self):
        self.o_start = int
        self.o_end = int
        self.o_str = str
        self.c_str = str
        self.type = type
    
    def __repr__(self):
        return 'o_start: {}, o_end: {}, o_str: {}, c_str: {}, type: {}'.format(
            self.o_start,
            self.o_end,
            self.o_str,
            self.c_str,
            self.type
        )

def main(args):
    dataset = test()
    pass

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_parser()
    main(args)