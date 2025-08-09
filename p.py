import streamlit as st
from gecommon import CachedERRANT
from annotated_text import annotated_text
import argparse

ETYPE = [
    'ADJ',
    'ADV',
    'CONJ',
    'CONTR',
    'DET',
    'NOUN',
    'NOUN:POSS',
    'OTHER',
    'PART',
    'PREP',
    'PRON',
    'PUNCT',
    'VERB',
    'VERB:FORM',
    'VERB:TENSE',
    'ADJ:FORM',
    'MORPH',
    'NOUN:INFL',
    'NOUN:NUM',
    'ORTH',
    'SPELL',
    'VERB:INFL',
    'VERB:SVA',
    'WO'
]

def gen_annotate_tokens(tokens, edits, etype2visible):
    annotated_tokens = []
    idx = 0
    for e in edits:
        no_edited_tokens = tokens[idx:e.o_start]
        if no_edited_tokens != '':
            annotated_tokens.append(' '.join(no_edited_tokens) + ' ')
        mru_type = e.type[0]
        other_type = ':'.join(e.type.split(':')[1:])
        if etype2visible[mru_type] and etype2visible[other_type]:
            annotated_tokens.append((
                f'{e.o_str} -> {e.c_str}',
                e.type
            ))
        else:
            annotated_tokens.append(
                f'[{e.o_str} -> {e.c_str}] ',
            )
        idx = e.o_end
    if idx < len(tokens):
        no_edited_tokens = tokens[idx:]
        annotated_tokens.append(' '.join(no_edited_tokens))
    return annotated_tokens

def main(args):
    ss = st.session_state
    if 'cache_parse' not in ss:
        ss['cache_parse'] = dict()
    if 'cache_annotate' not in ss:
        ss['cache_annotate'] = dict()
    errant = CachedERRANT('en')

    st.write('Input sources, hypotheses and references, then click the "Run" button at the bottom of the page.')
    srcs = st.text_area(
        'Input Sources',
        value='This are gramamtical sentence .\nThis are gramamtical sentence .'
    ).rstrip().split('\n')
    hyps = st.text_area(
        'Input Hypotheses',
        value='This is grammatical sentence .\nThis is grammatical sentence .'
    ).rstrip().split('\n')
    refs = st.text_area(
        'Input References',
        value='This is a grammatical sentence .\nThis is a grammatical sentence .'
    ).rstrip().split('\n')
    etype2visible = dict()
    st.header('Select visible error types')
    for etype in ['M', 'R', 'U']:
        etype2visible[etype] = st.checkbox(etype, value=True)
    st.divider()
    for etype in ETYPE:
        etype2visible[etype] = st.checkbox(etype, value=True)

    if st.button("Run"):
        hyp_edits = [errant.extract_edits(s, h) for s, h in zip(srcs, hyps)]
        ref_edits = [errant.extract_edits(s, t) for s, t in zip(srcs, refs)]

        n_sents = len(srcs)
        for i in range(n_sents):
            st.header(f'Line {i+1}')
            st.write(f'<strong>Source:</strong> {srcs[i]}', unsafe_allow_html=True)
            st.markdown('#### References')
            tokens = srcs[i].split(' ')
            annotated_tokens = gen_annotate_tokens(
                tokens,
                ref_edits[i],
                etype2visible
            )
            annotated_text(annotated_tokens)
            st.markdown('#### Hypotheses')
            tokens = srcs[i].split(' ')
            annotated_tokens = gen_annotate_tokens(
                tokens,
                hyp_edits[i],
                etype2visible
            )
            annotated_text(annotated_tokens)
            st.divider()


def get_parser():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_parser()
    main(args)

