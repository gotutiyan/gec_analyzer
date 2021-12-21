from flask import Flask, render_template, request
from dataset import Dataset
import argparse
from collections import defaultdict

app = Flask(__name__)
dataset = Dataset() # will be loaded at beggining of the program

# 最初はこっちが呼ばれるはず
@app.route('/')
def index():
    global dataset
    # type3, type25 = load_types(id='errant')
    types1 = dataset.type_set[0]
    types2 = dataset.type_set[1]
    visible_types1 = types1
    visible_types2 = types2
    chunks_list = dataset.generate_chunks_list(visible_types1, visible_types2)
    visible_types1_dict = defaultdict(int)
    visible_types2_dict = defaultdict(int)
    for type in visible_types1:
        visible_types1_dict[type] = 1
    for type in visible_types2:
        visible_types2_dict[type] = 1
    return render_template(
        'content.html',
        title='gec analyzer',
        chunks_list=chunks_list,
        visible_types1_dict=visible_types1_dict,
        visible_types2_dict=visible_types2_dict,
        type1=types1,
        type2=types2
    )

# チェックボックス適用したらこっちが呼ばれるはず
@app.route('/', methods=['POST'])
def post():
    global dataset
    # type3, type25 = load_types(id='errant')
    types1 = dataset.type_set[0]
    types2 = dataset.type_set[1]
    visible_types1 = request.form.getlist('type1')
    if types2 == {''}:
        visible_types2 = types2
    else:
        visible_types2 = request.form.getlist('type2')
    chunks_list = dataset.generate_chunks_list(visible_types1, visible_types2)
    visible_types1_dict = defaultdict(int)
    visible_types2_dict = defaultdict(int)
    for type in visible_types1:
        visible_types1_dict[type] = 1
    for type in visible_types2:
        visible_types2_dict[type] = 1
    return render_template(
        'content.html',
        title='gec analyzer',
        chunks_list=chunks_list,
        visible_types1_dict=visible_types1_dict,
        visible_types2_dict=visible_types2_dict,
        type1=types1,
        type2=types2
    )

@app.route('/stat')
def stat():
    _, type2freq, type2ratio = dataset.calc_stat()
    return render_template(
        'stat.html',
        title='gec stat',
        type2freq=type2freq,
        type2ratio=type2ratio,
    )

def load_dataset(args):
    global dataset
    if args.m2:
        dataset.from_m2(
            open(args.m2).read(),
            args.ref_id
        )
    else:
        dataset.from_raw_text(
            open(args.orig).read().split('\n'),
            open(args.cor).read().split('\n')
        )
    return

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--orig')
    parser.add_argument('--cor')
    parser.add_argument('--m2')
    parser.add_argument('--ref_id', type=int, default=0)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_parser()
    load_dataset(args)
    app.run(debug=True)