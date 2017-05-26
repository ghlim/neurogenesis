"""
Test for topographic map formation using STDP and synaptic rewiring.

http://hdl.handle.net/1842/3997
"""
# Imports
import numpy as np
import pylab

try:
    import pyNN.spiNNaker as sim
except Exception as e:
    import spynnaker.pyNN as sim

# SpiNNaker setup
sim.setup(timestep=1.0, min_delay=1.0, max_delay=15.0)
sim.set_number_of_neurons_per_core("IF_curr_exp", 50)


# +-------------------------------------------------------------------+
# | Function definitions                                              |
# +-------------------------------------------------------------------+

# Periodic boundaries
# https://github.com/pabogdan/neurogenesis/blob/master/notebooks/neurogenesis-in-numbers/Periodic%20boundaries.ipynb
def distance(x0, x1, grid, type='euclidian'):
    x0 = np.asarray(x0)
    x1 = np.asarray(x1)
    delta = np.abs(x0 - x1)
    delta = np.where(delta > grid * .5, delta - grid, delta)

    if type == 'manhattan':
        return np.abs(delta).sum(axis=-1)
    return np.sqrt((delta ** 2).sum(axis=-1))


# Poisson spike source as from list spike source
# https://github.com/project-rig/pynn_spinnaker_bcpnn/blob/master/examples/modular_attractor/network.py#L115-L148
def poisson_generator(rate, t_start, t_stop):
    n = int((t_stop - t_start) / 1000.0 * rate)
    number = np.ceil(n + 3 * np.sqrt(n))
    if number < 100:
        number = min(5 + np.ceil(2 * n), 100)

    if number > 0:
        isi = np.random.exponential(1.0 / rate, int(number)) * 1000.0
        if number > 1:
            spikes = np.add.accumulate(isi)
        else:
            spikes = isi
    else:
        spikes = np.array([])

    spikes += t_start
    i = np.searchsorted(spikes, t_stop)

    extra_spikes = []
    if len(spikes) == i:
        # ISI buf overrun

        t_last = spikes[-1] + np.random.exponential(1.0 / rate, 1)[0] * 1000.0

        while (t_last < t_stop):
            extra_spikes.append(t_last)
            t_last += np.random.exponential(1.0 / rate, 1)[0] * 1000.0

            spikes = np.concatenate((spikes, extra_spikes))
    else:
        spikes = np.resize(spikes, (i,))

    # Return spike times, rounded to millisecond boundaries
    return [round(x) for x in spikes]


def generate_rates(s, grid):
    '''
    Function that generates an array the same shape as the input layer so that
    each cell has a value corresponding to the firing rate for the neuron
    at that position.
    '''
    _rates = np.zeros(grid)
    for x in range(grid[0]):
        for y in range(grid[1]):
            _d = distance(s, (x, y), grid)
            _rates[x, y] = f_base + f_peak * np.e ** (-_d / ((2 * sigma_stim) ** 2))
    return _rates


def generate_spikes(rates):
    spikes = np.zeros((16, 16, 21))
    for x in range(16):
        for y in range(16):
            spikes_times_xy = poisson_generator(rates[x, y], 0, 20)
            for time in spikes_times_xy:
                spikes[x, y, int(time)] = 1
    return spikes


# +-------------------------------------------------------------------+
# | General Parameters                                                |
# +-------------------------------------------------------------------+

# Population parameters
model = sim.IF_curr_exp

# Membrane
v_rest = -70  # mV
e_ext = 0  # V
v_thr = -54  # mV
g_max = 0.2
tau_m = 20  # ms
tau_ex = 5  # ms

cell_params = {'cm': 0.20,
               'i_offset': 0.0,
               'tau_m': 20.0,
               'tau_refrac': 0.0,
               'tau_syn_E': 5.0,
               'tau_syn_I': 5.0,
               'v_reset': -70.0,
               'v_rest': -65.0,
               'v_thresh': -50.0
               }

# +-------------------------------------------------------------------+
# | Rewiring Parameters                                               |
# +-------------------------------------------------------------------+
no_iterations = 5000
simtime = no_iterations
# Wiring
n = 16
N_layer = n ** 2
S = (n, n)
grid = np.asarray(S)

s = (n // 2, n // 2)
s_max = 32
sigma_form_forward = 2.5
sigma_form_lateral = 1
p_form_lateral = 1
p_form_forward = 0.16
p_elim_dep = 0.0245
p_elim_pot = 1.36 * np.e ** -4
f_rew = 10 ** 4  # Hz

# Inputs
f_mean = 20  # Hz
f_base = 5  # Hz
f_peak = 152.8  # Hz
sigma_stim = 2
t_stim = 20  # ms

# STDP
a_plus = 0.1
b = 1.2
tau_plus = 20  # ms
tau_minus = 64  # ms

# +-------------------------------------------------------------------+
# | Initial network setup                                             |
# +-------------------------------------------------------------------+

# Neuron populations
source_pop = sim.Population(N_layer, model, cell_params, label="SOURCE_POP")
target_pop = sim.Population(N_layer, model, cell_params, label="TARGET_POP")

# Connections
# Plastic Connections between pre_pop and post_pop
stdp_model = sim.STDPMechanism(
    timing_dependence=sim.SpikePairRule(tau_plus=20., tau_minus=64.0,
                                        nearest=True),
    weight_dependence=sim.AdditiveWeightDependence(w_min=0, w_max=0.9,
                                                   A_plus=0.02, A_minus=0.02)
)

structure_model_w_stdp = sim.StructuralMechanism(stdp_model=stdp_model, weight=0.0, s_max=32)

plastic_projection = sim.Projection(
    source_pop, target_pop, sim.FixedNumberPostConnector(32),  # TODO change to a FromListConnector
    synapse_dynamics=sim.SynapseDynamics(slow=structure_model_w_stdp),
    label="plastic_projection"
)

# Need to setup the moving input

# generate all rates

rates = np.zeros((16, 16, simtime // t_stim))
for rate_id in range(simtime // t_stim):
    rates[:, :, rate_id] = generate_rates(np.random.randint(0, n, size=2), grid)
rates = rates.reshape(N_layer, simtime // t_stim)
spike_times = [[], ] * N_layer

for n_id in range(N_layer):
    for time in range(rates.shape[1]):
        spike_times[n_id] += poisson_generator(rates[n_id, time], time * t_stim, time * (t_stim + 1) - 1)

spikeArray = {'spike_times': spike_times}
spike_source = sim.Population(N_layer, sim.SpikeSourceArray, spikeArray)

sim.Projection(spike_source, source_pop, sim.OneToOneConnector(weights=0.1), target="excitatory",
               label="External Stimulus")

# +-------------------------------------------------------------------+
# | Simulation and results                                            |
# +-------------------------------------------------------------------+

# Record neurons' potentials
target_pop.record_v()
source_pop.record_v()

# Record spikes
target_pop.record()
source_pop.record()

# Run simulation
sim.run(simtime)

print("Weights:", plastic_projection.getWeights())


def plot_spikes(spikes, title):
    if spikes is not None:
        pylab.figure()
        pylab.xlim((0, simtime))
        pylab.plot([i[1] for i in spikes], [i[0] for i in spikes], ".")
        pylab.xlabel('Time/ms')
        pylab.ylabel('spikes')
        pylab.title(title)

    else:
        print "No spikes received"


pre_spikes = source_pop.getSpikes(compatible_output=True)
post_spikes = target_pop.getSpikes(compatible_output=True)

np.savez("structural_results_stdp", pre_spike=pre_spikes, post_spikes=post_spikes)

plot_spikes(pre_spikes, "pre-synaptic")
plot_spikes(post_spikes, "post-synaptic")
pylab.show()

# End simulation on SpiNNaker
sim.end()
