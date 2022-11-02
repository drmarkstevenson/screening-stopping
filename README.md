# screening-stopping
Code to evaluate evaluate screening stopping algorithms applied to multiple rankings by calling tar_eval multiple times and averaging results.

Metrics used: 
1. Recall 
2. Cost (== percentage of documents examined)
3. Loss (== amount by which achieved recall is below target recall)

Results are averaged across runs (with standard deviation reported in brackets).  

## Prerequisite

Script assumes that tar_eval.py (and associated scripts) are available via ./scripts/tar_eval.py

These can be downloaded from https://github.com/CLEF-TAR/tar

## Running script 

### Syntax: 
~~~
  % python eval_multiple_runs.py  -f DIR -t TARGET_RECALL -q QRELS_FILE [-v]
~~~

where
~~~
  DIR is directory containing a list of runs
  TARGET_RECALL is the target recall provided to the stopping algorithm (required for loss metric)
  QRELS_FILE is the location of the qrels file
  -v flag produces verbose output (results printed for each topic) 
~~~

~~~
  % python eval_multiple_runs.py  -h
~~~
Prints command line help

### Example:
~~~
% python eval_multiple_runs.py  -f ./run_outputs/ -t 0.8 -q ./qrels.txt 
~~~

### Example output: 

~~~
  Runs: 4
  Recall: 0.974	(0.002)
  Cost:   0.579	(0.005)
  Loss:   0.003	(0.001)
~~~

