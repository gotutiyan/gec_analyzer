import errant
import configparser
import argparse

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

class Dataset:
    def __init__(self):
        self.orig_list = []
        self.cor_list = []
        self.edits_list = []
        self.chunks_list = []
        self.type2freq = dict()
        self.type2ratio = dict()
        self.wer = 0 # word error ratio
        self.annotator = errant.load('en')
        self.n_orig_tokens = 0
        self.type_set = []
    
    def from_raw_text(self, orig_list, cor_list):
        self.orig_list = orig_list
        self.cor_list = cor_list
        self.edits_list = self.extract_edits(self.orig_list, self.cor_list, self.annotator)
        self.type_set = self.make_type_set(self.edits_list)
        return

    def from_m2(self, m2, ref_id):
        orig_list, edits_list = self.read_m2(m2, ref_id=ref_id)
        self.orig_list = orig_list
        self.edits_list = edits_list
        self.type_set = self.make_type_set(self.edits_list)
        return
        
    @staticmethod
    def read_m2(m2, ref_id=0):
        m2_contetns = m2.split('\n\n')
        orig_list = []
        edits_list = []
        for m2_sent in m2_contetns:
            orig, *edits_m2 = m2_sent.split('\n')
            orig = orig[2:] # remove 'S '
            orig_list.append(orig)
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
            edits_list.append(edits)
        return orig_list, edits_list
            

    def generate_chunks_list(self, visible_type3, visible_type25):
        chunks_list = []
        for orig, edits in zip(self.orig_list, self.edits_list):
            chunks = self.make_chunks(orig, edits, visible_type3, visible_type25)
            if chunks != -1:
                chunks_list.append(chunks)
        return chunks_list
    
    def calc_stat(self):
        self.n_orig_tokens = self.calc_orig_tokens(self.orig_list)
        self.wer = self.calc_wer(self.edits_list, self.n_orig_tokens)
        self.type2freq = self.calc_type2freq(self.edits_list)
        self.type2ratio = self.calc_type2ratio(self.type2freq)
        return self.wer, self.type2freq, self.type2ratio
    
    def extract_edits(self, orig_list, cor_list, annotator):
        edits_list = []
        for orig, cor in zip(orig_list, cor_list):
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
    def calc_orig_tokens(orig_list):
        sum = 0
        for orig in orig_list:
            sum += len(orig.split(' '))
        return sum

    @staticmethod
    def calc_type2freq(edits_list):
        type2freq = [dict(), dict()]
        for edits in edits_list:
            for e in edits:
                type0 = e.type.split(':')[0] # R:VERB:SVA => R
                type1 = ':'.join(e.type.split(':')[1:]) # R:VERB:SVA => VERB:SVA
                type2freq[0][type0] = type2freq[0].get(type0, 0) + 1
                type2freq[1][type1] = type2freq[1].get(type1, 0) + 1
        return type2freq

    @staticmethod    
    def calc_type2ratio(type2freq):
        type2ratio = [dict(), dict()]
        sum_corrections = sum(type2freq[0].values())
        for i in range(len(type2freq)):
            for type, freq in type2freq[i].items():
                type2ratio[i][type] = round(freq / sum_corrections, 4) 
        return type2ratio
    
    @staticmethod
    def calc_wer(edits_list, n_orig_token):
        error_token = 0
        for edits in edits_list:
            error_token += sum([len(e.o_str.split()) for e in edits])
        return error_token / n_orig_token
        
    @staticmethod
    def make_edits(orig, cor, annotator):
        orig = annotator.parse(orig)
        cor = annotator.parse(cor)
        edits = annotator.annotate(orig, cor)
        return edits

    @staticmethod
    def make_chunks(orig, edits, visible_type1, visible_type2):
        orig_tokens = orig.split()
        chunks = []
        token_idx = 0
        edit_idx = 0
        len_orig_tokens = len(orig_tokens)
        len_edits = len(edits)
        found_error = False
        while token_idx < len_orig_tokens:
            if edit_idx < len_edits and token_idx == edits[edit_idx].o_start:
                edit = edits[edit_idx]
                type1, *type2 = edit.type.split(':')
                type2 = ':'.join(type2)
                if type1 in visible_type1 and\
                    type2 in visible_type2:
                    found_error = True
                    chunks.append({
                        'o_str': "φ" if edit.o_str == "" else edit.o_str,
                        'c_str': "φ" if edit.c_str == "" else edit.c_str,
                        'type': edit.type,
                        'is_modified': True
                    })
                    token_idx = edit.o_end
                else:
                    chunks.append({
                        'o_str': orig_tokens[token_idx],
                        'c_str': None,
                        'type': None,
                        'is_modified': False
                    })
                    token_idx += 1
                edit_idx += 1
            else:
                chunks.append({
                    'o_str': orig_tokens[token_idx],
                    'c_str': None,
                    'type': None,
                    'is_modified': False
                })
                token_idx += 1
        if found_error:
            return chunks
        else:
            return -1
    
    def load_types(id='errant'):
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