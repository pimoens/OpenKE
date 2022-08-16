import argparse
import json
import os

import config
from models import *


def main(args):
    input_dir = args.input_dir
    output_dir = args.output_dir

    model = args.model

    os.environ['CUDA_VISIBLE_DEVICES'] = '0'

    con = config.Config()

    con.set_use_gpu(True)
    con.set_in_path(input_dir)
    con.set_work_threads(8)
    con.set_train_times(1000)
    con.set_nbatches(100)
    con.set_alpha(0.001)
    con.set_bern(0)
    con.set_dimension(50)
    con.set_margin(1.0)
    con.set_ent_neg_rate(1)
    con.set_rel_neg_rate(0)
    con.set_opt_method("SGD")
    con.set_save_steps(100)
    con.set_valid_steps(100)
    con.set_early_stopping_patience(10)
    con.set_checkpoint_dir('./checkpoint')
    con.set_result_dir(output_dir)
    con.set_test_link(True)
    con.set_test_triple(True)
    con.init()
    con.set_train_model(TransH)
    con.train()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--model', help='The model to train')
    parser.add_argument('--input-dir', help='Directory containing the Turtle files')
    parser.add_argument('--output-dir', help='Directory for output files')
    parser.add_argument('-v', '--verbose', help='Verbosity', action='store_true')
    args_ = parser.parse_args()

    main(args_)
