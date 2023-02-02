# GEC Analyzer

GEC Analyzer is a visualizer for Grammtical Error Correction efficiently.

- You can see the error correction easily.
- You can narrow down your search by error type (ERRANT definition).
- Because GEC Analyzer visualizes multiple references and hypotheses, you can analyze which error corrections are true, and what corrections that are different from other GEC systems.

![](./images/demo.gif)

### Install
python >=3.7

```sh
pip install -r requirements.txt
python -m spacy download en
```

### Usage

```sh
python run.py --orig <orig file> --hypos <output files> --refs <reference files>
```
Then, please go to [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

- `<output files>` and `<reference files>` can be multiple.
- The format of each input file can be either M2 format or raw text. Note that you must use the `.m2` extension for a M2 format file.
- M2 format can contain multiple references, but GEC Analyzer will display all of them.
- You can specify a mixture of raw text and M2 format files.
- If you specify raw text for `--hypo` or `--refs`, please also specify `--orig`. If you specify only M2 format, `--orig` is not needed.

### Demo

1. Use raw text files.

   ```sh
   python run.py --orig demo/orig.txt --refs demo/ref.txt --hyps demo/hyp.txt
   ```

1. Use a M2 file format files.

   ```sh
   python  run.py --refs demo/sample.m2 --hyps demo/sample.m2
   ```

1. Use multiple raw text files for each option.

   ```sh
   python run.py --orig demo/orig.txt --refs demo/ref.txt demo/ref.txt --hyps demo/hyp.txt demo/hyp.txt
   ```

3. Use mixture of M2 and raw text files for each option (This may be a rare case...).

   ```sh
   python run.py --m2 demo/other_type.m2
   ```

   