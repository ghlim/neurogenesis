import argparse

# Current defaults for [App: Motion detection]
# as of 02.10.2018

# Default values
DEFAULT_CHUNK_SIZE = 200  # ms
DEFAULT_W_MIN = 0
DEFAULT_W_MAX = .1
DEFAULT_CLASSES = [0, 90]
DEFAULT_NO_ITERATIONS = DEFAULT_CHUNK_SIZE * (100 * len(DEFAULT_CLASSES))
DEFAULT_T_RECORD = 200000
DEFAULT_P_CONNECT = .1  # 10%

DEFAULT_B = 1.2
DEFAULT_TAU_MINUS = 60  # ms
DEFAULT_TAU_PLUS = 60  # ms
DEFAULT_TAU_REFRAC = 1.0  # ms
DEFAULT_A_PLUS = 0.1
DEFAULT_A_MINUS = (DEFAULT_A_PLUS * DEFAULT_TAU_PLUS * DEFAULT_B) \
                  / float(DEFAULT_TAU_MINUS)

# Default flags
DEFAULT_REWIRING_FLAG = False
DEFAULT_MNIST_FLAG = False
DEFAULT_LATERAL_INHIBITION = False

# Argument parser
parser = argparse.ArgumentParser(
    description='Readout module for topographic maps generated by SpiNNaker '
                'in order to perform classification. '
                '[WARNING] This module assumes a specific architecture (1 '
                'exc and 1 inh target layers each with 3 input projections)')
flags = parser.add_argument_group('flag arguments')
mutex_required_args = parser.add_mutually_exclusive_group(
    required=True)
mutex_required_args.add_argument('--min_supervised',
                                 help="label is communicated to readout "
                                      "neurons "
                                      "connection weights set to w_min "
                                      "-- [default {}]".format(DEFAULT_W_MIN),
                                 action="store_true")

mutex_required_args.add_argument('--max_supervised',
                                 help="label is communicated to readout "
                                      "neurons. initial "
                                      "connection weights set to w_max"
                                      "-- [default {}]".format(DEFAULT_W_MAX),
                                 action="store_true")

mutex_required_args.add_argument('--unsupervised',
                                 help="label is NOT communicated to "
                                      "readout neurons. "
                                      "initial connection "
                                      "weights set to w_max",
                                 action="store_true")

parser.add_argument('path', help='path of input .npz archive defining '
                                 'connectivity', nargs='*')

parser.add_argument('-o', '--output', type=str,
                    help="name of the numpy archive storing simulation results",
                    dest='filename')

parser.add_argument('--b', type=float,
                    default=DEFAULT_B,
                    help='ration between area under depression curve and '
                         'area under potentiation curve'
                         ' -- [default {}]'.format(DEFAULT_B))

parser.add_argument('--tau_minus', type=float,
                    default=DEFAULT_TAU_MINUS,
                    help='time constant for depression'
                         ' -- [default {}]'.format(DEFAULT_TAU_MINUS))

parser.add_argument('--tau_plus', type=float,
                    default=DEFAULT_TAU_PLUS,
                    help='time constant for potentiation'
                         ' -- [default {}]'.format(DEFAULT_TAU_PLUS))

parser.add_argument('--a_plus', type=float,
                    default=DEFAULT_A_PLUS,
                    help='potentiation learning rate'
                         ' -- [default {}]'.format(DEFAULT_A_PLUS))

parser.add_argument('--w_max', type=float,
                    default=DEFAULT_W_MAX,
                    help='maximum weight'
                         ' -- [default {}]'.format(DEFAULT_W_MAX))

parser.add_argument('--w_min', type=float,
                    default=DEFAULT_W_MIN,
                    help='minimum weight'
                         ' -- [default {}]'.format(DEFAULT_W_MIN))

parser.add_argument('--p_connect', type=float,
                    default=DEFAULT_P_CONNECT,
                    help='readout neurons have, on average, p_connect '
                         'connectivity (0<=p_connect<=1)'
                         ' -- [default {}]'.format(DEFAULT_P_CONNECT))

parser.add_argument('--plot', help="display plots",
                    action="store_true")

flags.add_argument('--snapshots',
                   help="store snapshot information "
                        "(connectivity + weights + delays)",
                   action="store_true")

parser.add_argument('--label_time_offset',
                    help="time offset of label presentation within a time bin "
                         "-- [default {}]".format([DEFAULT_CHUNK_SIZE - 1]),
                    type=int, nargs="+", default=[DEFAULT_CHUNK_SIZE - 1],
                    dest='label_time_offset'
                    )

flags.add_argument('--rewiring',
                   help="flag to allow readout neurons to rewire "
                        "-- [default {}]".format(DEFAULT_REWIRING_FLAG),
                   action="store_true")

flags.add_argument('--wta_readout',
                   help="flag to enable WTA / strong lateral connectivity in "
                        "readout layer "
                        "-- [default {}]".format(DEFAULT_LATERAL_INHIBITION),
                   action="store_true")

flags.add_argument('--mnist',
                   help="flag used to enable inputting MNIST digits "
                        "(as opposed to moving bars) "
                        "-- [default {}]".format(DEFAULT_MNIST_FLAG),
                   action="store_true")

parser.add_argument('--no_iterations', type=int,
                    default=DEFAULT_NO_ITERATIONS, dest='no_iterations',
                    help='total number of iterations (or time steps) for '
                         'the simulation (technically, ms)'
                         ' -- [default {}]'.format(DEFAULT_NO_ITERATIONS))

parser.add_argument('--classes',
                    help="[App: Motion detection] Network will be trained "
                         "using a random succession of these classes"
                         " -- [default {}]".format(DEFAULT_CLASSES),
                    type=int, nargs="+", default=DEFAULT_CLASSES,
                    dest='classes'
                    )

parser.add_argument('--t_record', type=int,
                    default=DEFAULT_T_RECORD, dest='t_record',
                    help='time between retrieval of recordings (ms)'
                         ' -- [default {}]'.format(DEFAULT_T_RECORD))

args = parser.parse_args()
