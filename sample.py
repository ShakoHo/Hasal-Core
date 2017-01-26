import pp
import os
import time
import sys
import subprocess
import shutil
import cv2
import numpy



def convert_to_dct(image_fp, skip_status_bar_fraction=1.0):
    dct_obj = None
    try:
        img_obj = cv2.imread(image_fp)
        height, width, channel = img_obj.shape
        height = int(height * skip_status_bar_fraction) - int(height * skip_status_bar_fraction) % 2
        img_obj = img_obj[:height][:][:]
        img_gray = numpy.zeros((height, width))
        for channel in range(channel):
            img_gray += img_obj[:, :, channel]
        img_gray /= channel
        img_dct = img_gray / 255.0
        dct_obj = cv2.dct(img_dct)
    except Exception as e:
        print e
    return dct_obj

def isprime(image_list, dct_list):
    TMP_DIR = os.path.join(os.getcwd(), "tmp2")
    #print image_list
    #print dct_list
    for image_fn in image_list:
        image_fp = os.path.join(TMP_DIR, image_fn)
        dct_obj = convert_to_dct(image_fp)
        for sample_dct in dct_list:
            if compare_two_images(dct_obj, sample_dct):
                return image_fn
    return "WTF"


def sum_primes(n):
    """Calculates sum of all primes below given integer n"""


    return sum([x for x in xrange(2,n) if isprime(x)])

def compare_two_images( dct_obj_1, dct_obj_2):
    match = False
    try:
        row1, cols1 = dct_obj_1.shape
        row2, cols2 = dct_obj_2.shape
        if (row1 == row2) and (cols1 == cols2):
            threshold = 0.0003
            mismatch_rate = numpy.sum(numpy.absolute(numpy.subtract(dct_obj_1, dct_obj_2))) / (row1 * cols1)
            if mismatch_rate <= threshold:
                match = True
    except Exception as e:
        print e
    return match

print """Usage: python sum_primes.py [ncpus]
    [ncpus] - the number of workers to run in parallel,
    if omitted it will be set to the number of processors in the system
"""




TMP_DIR = os.path.join(os.getcwd(), "tmp2")
fn_list = os.listdir(TMP_DIR)

sample_1_fn = fn_list[385]

sample_2_fn = fn_list[1201]

sample_1_dct = convert_to_dct(os.path.join(TMP_DIR, sample_1_fn))
sample_2_dct = convert_to_dct(os.path.join(TMP_DIR, sample_2_fn))

sample_dct_list = [sample_1_dct, sample_2_dct]

def gogo_compare(image_list, dct_list):
    print "run!!!!"
    print len(image_list)
    for image_fn in image_list:
        image_fp = os.path.join(TMP_DIR, image_fn)
        image_dct = convert_to_dct(image_fp)
        for sample_dct in dct_list:
            if compare_two_images(image_dct, sample_dct):
                print "Found image matched"
                with open("tmp.txt", "w") as fh:
                    fh.write(image_fn)

                return image_fn
    return True





# tuple of all parallel python servers to connect with
ppservers = ()
#ppservers = ("10.0.0.1",)

ncpus = 8

if len(sys.argv) > 1:
    ncpus = int(sys.argv[1])
    # Creates jobserver with ncpus workers
    job_server = pp.Server(ncpus, ppservers=ppservers)
else:
    # Creates jobserver with automatically detected number of workers
    job_server = pp.Server(ppservers=ppservers)

print "Starting pp with", job_server.get_ncpus(), "workers"

# Submit a job of calulating sum_primes(100) for execution.
# sum_primes - the function
# (100,) - tuple with arguments for sum_primes
# (isprime,) - tuple with functions on which function sum_primes depends
# ("math",) - tuple with module names which must be imported before sum_primes execution
# Execution starts as soon as one of the workers will become available
job1 = job_server.submit(sum_primes, (100,), (isprime,), ("math",))

# Retrieves the result calculated by job1
# The value of job1() is the same as sum_primes(100)
# If the job has not been finished yet, execution will wait here until result is available
#result = job1()

#print "Sum of primes below 100 is", result

start_time = time.time()

# The following submits 8 jobs and then retrieves the results
inputs = (100000, 100100, 100200, 100300, 100400, 100500, 100600, 100700)

i_list = []

if len(fn_list) % ncpus == 0:
    r = ncpus
else:
    r = ncpus + 2
for i in range(r):
    i_index = i * (len(fn_list) / ncpus)
    if i_index < len(fn_list):
        i_list.append(i_index)
    else:
        i_list.append(len(fn_list)-1)

print i_list

jobs = []

#job_server.submit(gogo_compare, (fn_list[:199], sample_dct_list), (convert_to_dct,), ("cv2", "numpy", ))

for index in range(len(i_list)-1):
    jobs.append(job_server.submit(isprime, (fn_list[i_list[index]:i_list[index+1]], sample_dct_list), (convert_to_dct,compare_two_images,), ("cv2", "numpy", )))
    #import pdb
    #pdb.set_trace()


#job_server.wait()

for job in jobs:
    #print job.sresult
    print job()

#jobs = [(input, job_server.submit(sum_primes,(input,), (isprime,), ("math",))) for input in inputs]
#for input, job in jobs:
#    print "Sum of primes below", input, "is", job()#

#print "Time elapsed: ", time.time() - start_time, "s"
job_server.print_stats()

# Parallel Python Software: http://www.parallelpython.com


