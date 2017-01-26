import pp
import os
import time
import subprocess
import shutil
import cv2
import numpy as np

input_image_list = [{'image_fp':'xxxxxx', 'time_seq':0.0, 'matched_sample': [], 'matched_rate': []}]


def compare_images(input_image_list, input_sample_image_list):
    pass


def convert_to_dct(image_fp, skip_status_bar_fraction=1.0):
    dct_obj = None
    try:
        img_obj = cv2.imread(image_fp)
        height, width, channel = img_obj.shape
        height = int(height * skip_status_bar_fraction) - int(height * skip_status_bar_fraction) % 2
        img_obj = img_obj[:height][:][:]
        img_gray = np.zeros((height, width))
        for channel in range(channel):
            img_gray += img_obj[:, :, channel]
        img_gray /= channel
        img_dct = img_gray / 255.0
        dct_obj = cv2.dct(img_dct)
    except Exception as e:
        print e
    return dct_obj

def compare_two_images( dct_obj_1, dct_obj_2):
    match = False
    try:
        row1, cols1 = dct_obj_1.shape
        row2, cols2 = dct_obj_2.shape
        if (row1 == row2) and (cols1 == cols2):
            threshold = 0.0003
            mismatch_rate = np.sum(np.absolute(np.subtract(dct_obj_1, dct_obj_2))) / (row1 * cols1)
            if mismatch_rate <= threshold:
                match = True
    except Exception as e:
        logger.error(e)
    return match

def compare_with_sampe(input_image_list, output_result_dict):
    for image_fn in input_image_list:
        dct_obj = convert_to_dct(image_fn)
        for sample_fn in output_result_dict.keys():
            if compare_two_images(output_result_dict[sample_fn]['dct_value'], dct_obj):
                output_result_dict[sample_fn]['result'].append(image_fn)
    return output_result_dict


def parallel_compare(input_image_list, input_sample_image_fp):
    # tuple of all parallel python servers to connect with
    ppservers = ()
    # ppservers = ("10.0.0.1",)

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
    result = job1()

    print "Sum of primes below 100 is", result

    start_time = time.time()

    # The following submits 8 jobs and then retrieves the results
    inputs = (100000, 100100, 100200, 100300, 100400, 100500, 100600, 100700)
    jobs = [(input, job_server.submit(sum_primes, (input,), (isprime,), ("math",))) for input in inputs]
    for input, job in jobs:
        print "Sum of primes below", input, "is", job()

    print "Time elapsed: ", time.time() - start_time, "s"
    job_server.print_stats()


def main():
    output_dir = os.path.join(os.getcwd(), 'tmp')
    sleep_time = 10
    image_list = []
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.mkdir(output_dir)
    ffmpeg_process = subprocess.Popen(['ffmpeg', '-i', 'test.mkv', 'tmp/img%05d.jpg'])

    start_counter = 0
    time.sleep(sleep_time)
    while True:
        f_list = os.listdir(output_dir)
        if start_counter == len(f_list):
            break
        else:
            start_counter = len(f_list)
            tmp_list = list(set(f_list) - set(image_list))
            image_list.extend(tmp_list)
            image_list.sort()

        time.sleep(sleep_time)




if __name__ == '__main__':
    main()