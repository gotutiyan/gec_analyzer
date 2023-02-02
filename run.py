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
    types1, types2 = dataset.load_types(id='errant')
    visible_types = []
    for t1 in types1:
        for t2 in types2:
            visible_types.append(t1 + ':' + t2)
    return render_template(
        'content.html',
        title='gec analyzer',
        dataset=dataset,
        visible_types1=types1,
        visible_types2=types2,
        visible_types=visible_types,
        type1=types1,
        type2=types2
    )

# チェックボックス適用したらこっちが呼ばれるはず
@app.route('/', methods=['POST'])
def post():
    global dataset
    types1, types2 = dataset.load_types(id='errant')
    visible_types1 = request.form.getlist('type1')
    if types2 == {''}:
        visible_types2 = types2
    else:
        visible_types2 = request.form.getlist('type2')
    visible_types = []
    for t1 in visible_types1:
        for t2 in visible_types2:
            visible_types.append(t1 + ':' + t2)
    return render_template(
        'content.html',
        title='gec analyzer',
        dataset=dataset,
        visible_types1=visible_types1,
        visible_types2=visible_types2,
        visible_types=visible_types,
        type1=types1,
        type2=types2
    )

def load_dataset(args):
    global dataset
    dataset.load(
        original_file=args.orig,
        referece_files=args.refs,
        hypothesis_files=args.hyps
    )

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--orig')
    parser.add_argument('--hyps', nargs='+')
    parser.add_argument('--refs', nargs='+')
    parser.add_argument('--m2')
    parser.add_argument('--ref_id', type=int, default=0)
    parser.add_argument('--port', type=int, default=5000)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_parser()
    load_dataset(args)
    app.run(debug=False, port=args.port)