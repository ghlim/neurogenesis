import subprocess
import os
import numpy as np
import sys
import hashlib
import pylab as plt

currrent_time = plt.datetime.datetime.now()
string_time = currrent_time.strftime("%H%M%S_%d%m%Y")

suffix = hashlib.md5(string_time).hexdigest()

count = 0

input_filename = "../simulation_statistics/2009_09_04.17_48_33 32Syn300s/InitialConnectivity.mat"
iterations = 300000
# t_record = iterations
t_record = 30000

cases = [1, 3]
input_types = [1, 2, 3, 4]
lesion_types = [0, 1, 2]
no_runs = 10

parameters_of_interest = {
    'cases': cases,
    'input_types': input_types,
    'lesion_types': lesion_types,
    'no_runs':no_runs
}

log_calls = []

for case in cases:
    for input_type in input_types:
        for lesion_type in lesion_types:
            for run in range(no_runs):
                filename = "case{}_inputtype{}_lesiontype{}_run{}" \
                           "_@{}".format(case,
                                         input_type,
                                         lesion_type,
                                         run + 1,
                                         suffix)
                count += 1
                null = open(os.devnull, 'w')
                print "Run ", count, "..."

                call = [sys.executable,
                        'topographic_map_formation.py',
                        '--case', str(case),
                        '-i', input_filename,
                        '-o', filename,
                        '--no_iterations',
                        str(iterations),
                        '--t_record',
                        str(t_record),
                        '--input_type', str(input_type),
                        '--lesion_type', str(lesion_type)
                        ]
                log_calls.append(call)
                subprocess.call(call,
                                stdout=sys.stdout, stderr=null)
                print "Run", count, "complete."
print "All done!"

end_time = plt.datetime.datetime.now()
total_time = end_time - currrent_time
np.savez("batch_{}".format(suffix),
         parameters_of_interest=parameters_of_interest,
         total_time=total_time,
         log_calls=log_calls)
