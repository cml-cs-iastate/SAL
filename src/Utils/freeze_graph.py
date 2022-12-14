"""
Imports a model meta-graph and checkpoint file, converts the variables to constants and exports the model as a graphdef protobuf
"""

import os
import sys
import argparse
import tensorflow as tf
from tensorflow.python.framework import graph_util

import src.SAL.Utils.facenet_sim_v2 as facenet


def main(args):
    with tf.Graph().as_default():
        with tf.compat.v1.Session() as sess:
            # Load the model meta-graph and checkpoint
            print('Model directory: %s' % args.model_dir)
            meta_file, ckpt_file = facenet.get_model_filenames(os.path.expanduser(args.model_dir))
            print('Metagraph file: %s' % meta_file)
            print('Checkpoint file: %s' % ckpt_file)
            facenet.load_model(args.model_dir, meta_file)
            output_node_names = 'embeddings'
            whitelist_names = []
            for node in sess.graph.as_graph_def().node:
                if node.name.startswith('InceptionResnetV1') or node.name.startswith('embeddings') or node.name.startswith('phase_train'):
                    print(node.name)
                    whitelist_names.append(node.name)

            output_graph_def = graph_util.convert_variables_to_constants(sess,
                                                                         sess.graph.as_graph_def(),
                                                                         output_node_names.split(","),
                                                                         variable_names_whitelist=whitelist_names)
        
        with tf.compat.v1.gfile.GFile(args.output_file, 'wb') as f:
            f.write(output_graph_def.SerializeToString())
        print("%d ops in the final graph." % len(output_graph_def.node))


def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('model_dir', type=str, help='Directory containing the metagraph (.meta) file and the checkpoint (ckpt) file containing model parameters')
    parser.add_argument('output_file', type=str, help='Filename for the exported graphdef protobuf (.pb)')
    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
