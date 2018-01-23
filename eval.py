import argparse
import functools
import sys
import os
import json

import torch

from tools import evaluation
from datasets import executor
import datasets
import tools

import models
import arguments


def evaluate(args):
    print("Evaluation:")
    print("\tModel type: %s\n\tModel path: %s" % (args.model_type, args.model_dir))
    tools.restore_args(args)
    arguments.backport_default_args(args)
    if args.eval_train:
        eval_dataset, _ = datasets.get_dataset(args)
    else:
        eval_dataset = datasets.get_eval_dataset(args)
    m = models.get_model(args)
    if m.last_step == 0:
        raise ValueError('Attempting to evaluate on untrained model')
    m.model.eval()
    current_executor = executor.get_executor(args)()
    if args.example_id is not None:
        eval_dataset.data = [eval_dataset.task[args.example_id]]

    evaluation.run_eval(
        args.tag, eval_dataset, m.inference,
        current_executor.execute, not args.hide_example_info)


if __name__ == "__main__":
    parser = arguments.get_arg_parser('Evaluating Text2Code', 'eval')

    args, _ = parser.parse_known_args(sys.argv)
    args.cuda = not args.no_cuda and torch.cuda.is_available()
    if not args.model_type or (not args.model_dir and args.model_type != 'search'):
        raise ValueError("Specify model_dir and model_type")
    if not args.tag:
        args.tag = args.model_type
    evaluate(args)
