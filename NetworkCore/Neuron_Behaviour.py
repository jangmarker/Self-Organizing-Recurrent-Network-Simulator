import numpy as np
from NetworkCore.Base import *
from numpy.random import *

class Neuron_Behaviour(NetworkObjectBase):
    #modificaton_reset_vars = []
    run_on_neuron_init_var = False

    def __init__(self, **kwargs):
        #if 'tag' in self.init_kwargs:
        #    self.add_tag(self.get_init_attr['tag'])
        self.init_kwargs = kwargs
        self.behaviour_enabled = self.get_init_attr('behaviour_enabled', True, None)
        super().__init__(tag=self.get_init_attr('tag', None, None))

    #def add_tag(self, tag):
    #    self.tags.append(tag)

    def run_on_neuron_init(self):
        self.run_on_neuron_init_var=True
        return self

    def diversity_string_to_vec(self, ds, neurons):

        if 'same(' in ds and ds[-1] is ')':
            params=ds[5:-1].replace(' ','').split(',')
            if len(params) == 2:
                #print('same', params)
                return getattr(neurons[params[0], 0], params[1])

        command = ds.split(';')
        if (not '(' in ds and not ')' in ds) and not command[0].replace('.', '').replace('+', '').replace('-', '').isdigit():
            return ds


        if len(command) == 1:
            if command[0].replace('.', '').replace('+', '').replace('-', '').isdigit():
                result = float(command[0])

            #else:
            #    result = self.get_random_nparray((neurons.size), rnd_code=command[0])
                #print(result, type(result))
                return result

        dist_cmd='uniform(low, high)'
        if len(command) > 2 and not 'plot' in command[2]:# problem: , also in command
            dist_cmd=command[2]

            if 'smooth' in command[2]:
                smoothing = float(command[2].replace('smooth', ''))
                dist_cmd = 'np.sum([uniform(low, high, size=dim) for _ in range(smoothing)], axis=0)/smoothing'.replace('smoothing', str(smoothing))


        if command[0].replace('.', '').replace('+', '').replace('-', '').isdigit():
            min_v = float(command[0])
            if '%' in command[1]:
                max_v = min_v
                if '-' in command[1]:
                    min_v -= min_v / 100 * float(command[1].replace('+', '').replace('-', '').replace('%', ''))
                if '+' in command[1]:
                    max_v += max_v / 100 * float(command[1].replace('+', '').replace('-', '').replace('%', ''))
            else:
                max_v = float(command[1])

            dist_cmd=dist_cmd.replace('low',str(min_v)).replace('high',str(max_v)).replace('min_v',str(min_v)).replace('max_v',str(max_v)).replace('min',str(min_v)).replace('max',str(max_v))
        else:
            dist_cmd=command[0]

        if 'lognormal_real_mean' in command[0]:
            parts = command[0].replace(')', '').replace(' ', '').split('(')
            arguments = parts[1].split(',')
            mean = float(arguments[0])
            sigma = float(arguments[1])
            mu = -np.power(sigma, 2) + np.log(mean)
            dist_cmd = 'lognormal({}, {})'.format(mu, sigma)

        result=self.get_random_nparray((neurons.size), rnd_code=dist_cmd)


        if 'plot' in command[-1]:
            import matplotlib.pyplot as plt
            #print(result)
            plt.hist(result, bins=30)
            plt.show()


        return result


    def get_init_attr(self, key, default, neurons, do_not_diversify=False):
        result = self.init_kwargs.get(key, default)

        if not do_not_diversify and type(result) is str and neurons is not None:
            result = self.diversity_string_to_vec(result, neurons)

        return result

    def set_variables(self, neurons):
        return

    def reset(self):
        return

    def new_iteration(self, neurons):
        return

    def get_shared_variable(self, name):
        return None

    def normalize_synapse_attr(self, src_attr, target_attr, target_value, neurons, synapse_type):

        neurons.temp_weight_sum = neurons.get_neuron_vec()

        for s in neurons.afferent_synapses[synapse_type]:
            if 'sparse' in s.tags:
                s.dst.temp_weight_sum += np.array(getattr(s, src_attr).sum(1)).flatten()
            else:
                s.dst.temp_weight_sum += np.sum(getattr(s, src_attr),axis=1)

        neurons.temp_weight_sum /= target_value

        for s in neurons.afferent_synapses[synapse_type]:
            if 'sparse' in s.tags:
                W = getattr(s, target_attr)
                W.data /= np.array(neurons.temp_weight_sum[W.indices]).reshape(W.data.shape)
            else:
                setattr(s, target_attr, getattr(s, target_attr) / (s.dst.temp_weight_sum[:, None]+(s.dst.temp_weight_sum[:, None]==0)))

    def initialize_synapse_attr(self, target_attr, density, equal_range, random_range, neurons, synapse_type, all_neurons_same=False):
        for s in neurons.afferent_synapses[synapse_type]:
            s.enabled *= s.get_random_synapse_mat(density, all_neurons_same) > 0.0
            setattr(s, target_attr, s.enabled*(s.get_synapse_mat()+equal_range+s.get_random_synapse_mat(1.0, all_neurons_same)*random_range))#s.shape_mat*#neurons.GABA_strength+neurons.min_GABA_strength





