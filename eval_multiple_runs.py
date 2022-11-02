import glob
import os
import sys
import subprocess
import numpy as np
import pandas as pd
from argparse import ArgumentParser


def main():

    parser = ArgumentParser()
    parser.add_argument("-f", help="Directory containing runs (e.g. ../run_dir)", required=True)
    parser.add_argument("-t", help="Target recall (e.g. 0.8)", required=True)
    parser.add_argument("-q", help="qrel file (e.g. ../qrels)", required=True)
    parser.add_argument('-v', help='Verbose output (detailed results for all runs)', action='store_true')

    args = parser.parse_args()

    target_recall = float(args.t)
    run_dir = args.f
    qrel_fname = args.q


    # Create list of runs (remove Windows hidden file) 
    run_dir += "/*"
    stopping_results_list = glob.glob(run_dir)
    stopping_results_list = [x for x in stopping_results_list if 'desktop.ini' not in x]
    # print(stopping_results_list)

    # loop through all runs, run tar_eval and capture results
    # Store results in list of dictionaries (more efficient to convert
    # to df all at once) 
    run_counter = 0
    results_list = [] 
    for run_file in stopping_results_list:
        print(".", end='')
        sys.stdout.flush()
        # recall, cost, loss = run_tar_eval(qrel_fname, run_file, target_recall) 
        results_list.extend(run_tar_eval(qrel_fname, run_file, run_counter, target_recall))
        
        # df.loc[run_counter] = [recall, cost, loss]

        run_counter += 1
    print()

    # Convert results to dataframe 
    df = pd.DataFrame(results_list, columns=['tid', 'run', 'recall', 'cost', 'loss'])
    # print(df.to_string())

    # Group by runs and compute the mean and standard deviation for each topic
    df2 = df.groupby('tid').agg({'recall' : ['mean', 'std'], 'cost' : ['mean', 'std'], 'loss' : ['mean', 'std'] })
    df2.columns = ['recall_mean', 'recall_std', 'cost_mean', 'cost_std', 'loss_mean', 'loss_std']
    df2 = df2.reset_index()
    if args.v: 
        print(df2.to_string())

    # Average over all topics
    df3 = df2.mean(axis=0)

    # Print out mean and 95% CI
    print("*** Summary ***")
    recall_mean = df3['recall_mean']
    recall_std = df3['recall_std']
    recall_ci_bottom = recall_mean - (1.96 * recall_std)
    if recall_ci_bottom < 0:
        recall_ci_bottom = 0
    recall_ci_top = recall_mean + (1.96 * recall_std)
    if recall_ci_top > 1:
        recall_ci_top = 1.000
    print("Recall\t{:.3f} ({:.3f}, {:.3f})".format(recall_mean, recall_ci_bottom, recall_ci_top))

    cost_mean = df3['cost_mean']
    cost_std = df3['cost_std']
    cost_ci_bottom = cost_mean - (1.96 * cost_std)
    if cost_ci_bottom < 0:
        cost_ci_bottom = 0
    cost_ci_top = cost_mean + (1.96 * cost_std)
    if cost_ci_top > 1:
        cost_ci_top = 1.000
    print("Cost\t{:.3f} ({:.3f}, {:.3f})".format(cost_mean, cost_ci_bottom, cost_ci_top))
    
    loss_mean = df3['loss_mean']
    loss_std = df3['loss_std']
    loss_ci_bottom = loss_mean - (1.96 * loss_std)
    if loss_ci_bottom < 0:
        loss_ci_bottom = 0
    loss_ci_top = loss_mean + (1.96 * loss_std)
    if loss_ci_top > 1:
        loss_ci_top = 1.000
    print("Loss\t{:.3f} ({:.3f}, {:.3f})".format(loss_mean, loss_ci_bottom, loss_ci_top))
    
    
 


# Function to evaluate output file and return scores for range of metrics
# Runs tar_eval script and parses output
# Computes four metrics: 
# 1) recall
# 2) cost (== percentage effort)
# 3) loss ( absolute difference between target and achieved recalls) 
def run_tar_eval(qrel_fname, out_fname, run_counter, des_recall): 
     
      # Location of script
      script = './scripts/tar_eval.py'
      
      # Run tar_eval script (supressing stderr) 
      ret = subprocess.check_output(['python', script, qrel_fname, out_fname], stderr=subprocess.DEVNULL)
      ret = ret.decode(encoding='utf-8')

      # Parse eval script output
      teval_dict = {}   # Summary results (computed across all topics)
      recalls = []      # Recall for each topic 
      for line in ret.split('\n'):
          if line.startswith('Usage: '):
            print("Error:\nProblem with arguments passed to {}".format(script))
            # print(line)
            sys.exit()
          if line != '':
            # print(line)
            tid, key, val = line.split()
            #print(f"tid: {tid}, key: {key}, val: {val}")
            if tid != 'ALL':
                if key == 'topic_id':
                    teval_dict[tid] = {}
                teval_dict[tid][key] = val

      
      results_list = [] # List of rows to be added to data frame later
      for tid in teval_dict:
          # Compute recall (rels_found / num_rel)
          recall = float(teval_dict[tid]['rels_found']) / float(teval_dict[tid]['num_rels'])
          
          # cost (num_shown / num_docs)
          cost = float(teval_dict[tid]['num_shown']) / float(teval_dict[tid]['num_docs'])

          # loss (amount by which achieved recall is below target recall)
          if recall >= des_recall: 
            loss = 0
          else:
            loss = (des_recall - recall)

          res_dict = { 'tid': tid, 'run': run_counter, 'recall': recall, 'cost': cost, 'loss': loss } 
          results_list.append(res_dict)

      return results_list

# Run the main function
main()
