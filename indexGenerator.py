import pp
import os
import time
import subprocess
import shutil
import cv2
import numpy
import argparse
from argparse import ArgumentDefaultsHelpFormatter


class IndexGenerator(object):

    def __init__(self, input_video_fp, input_sample_dp, output_img_dp='tmp'):
        self.result_data = {}
        self.input_video_fp = input_video_fp
        self.output_img_dp = os.path.join(os.getcwd(), output_img_dp)
        self.generate_result_data(input_sample_dp)
        self.sleep_time = 3

    def generate_result_data(self, input_sample_dp):
        for sample_fn in os.listdir(input_sample_dp):
            sample_fp = os.path.join(input_sample_dp, sample_fn)
            self.result_data[sample_fn] = {'dct': self.convert_to_dct(sample_fp),
                                           'fp': sample_fp,
                                           'result': []}

    def convert_to_image(self,  converting_fmt='bmp'):
        if os.path.exists(self.output_img_dp):
            shutil.rmtree(self.output_img_dp)
        os.mkdir(self.output_img_dp)
        output_img_fmt = self.output_img_dp + os.sep + 'img%05d.' + converting_fmt.lower()
        cmd_list = ['ffmpeg', '-i', self.input_video_fp, output_img_fmt]
        ffmpeg_process = subprocess.Popen(cmd_list)
        return ffmpeg_process

    def run(self):
        image_list = []
        background_process = self.convert_to_image()
        start_counter = 0
        time.sleep(self.sleep_time)
        while True:
            print "start_counter = [%s]" % str(start_counter)
            print "background information!!!!"
            print background_process.pid
            print "background information!!!!"
            f_list = os.listdir(self.output_img_dp)
            if start_counter == len(f_list):
                break
            else:
                start_counter = len(f_list)
                tmp_list = list(set(f_list) - set(image_list))
                self.compare_with_sample_img(tmp_list, self.result_data)

    def convert_to_dct(self, image_fp, skip_status_bar_fraction=1.0):
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

    def compare_dct(self, dct_obj_1, dct_obj_2, threshold=0.0003):
        match = False
        try:
            row1, cols1 = dct_obj_1.shape
            row2, cols2 = dct_obj_2.shape
            if (row1 == row2) and (cols1 == cols2):
                mismatch_rate = numpy.sum(numpy.absolute(numpy.subtract(dct_obj_1, dct_obj_2))) / (row1 * cols1)
                if mismatch_rate <= threshold:
                    match = True
        except Exception as e:
            print e
        return match

    def compare_with_sample_img(self, current_fn_list, result_data, threads=4):
        current_fn_number = len(current_fn_list)
        index_list = []
        jobs = []

        ppservers = ()
        job_server = pp.Server(threads, ppservers=ppservers)

        if current_fn_number % threads == 0:
            r_index = threads
        else:
            r_index = threads + 2
        for i in range(r_index):
            i_index = i * (current_fn_number / threads)
            if i_index < len(current_fn_list):
                index_list.append(i_index)
            else:
                index_list.append(current_fn_number - 1)

        for index in range(len(index_list) - 1):
            jobs.append(job_server.submit(self.paralle_compare_image, (current_fn_list[index_list[index]:index_list[index + 1]], result_data),
                                          (self.convert_to_dct, self.compare_dct,), ("cv2", "numpy",)))

        for job in jobs:
            if job():
                self.result_data[job()[0]]['result'].append(job()[1])
                print "%s = %s" % (job()[0], self.result_data[job()[0]]['result'])

    def paralle_compare_image(self, input_fn_list, input_sample_data):
        for image_fn in input_fn_list:
            image_fp = os.path.join(self.output_img_dp, image_fn)
            dct_obj = self.convert_to_dct(image_fp)
            for sample_fn in input_sample_data.keys():
                if self.compare_dct(dct_obj, input_sample_data[sample_fn]['dct']):
                    return sample_fn, image_fn
        return None



def main():
    arg_parser = argparse.ArgumentParser(description='Image tool',
                                         formatter_class=ArgumentDefaultsHelpFormatter)
    arg_parser.add_argument('-i', '--input', action='store', dest='input_video_fp', default=None,
                            help='Specify the file path.', required=False)
    arg_parser.add_argument('-o', '--outputdir', action='store', dest='output_img_dp', default=None,
                            help='Specify output image dir path.', required=False)
    arg_parser.add_argument('-s', '--sample', action='store', dest='sample_img_dp', default=None,
                            help='Specify sample image dir path.', required=False)
    args = arg_parser.parse_args()

    input_video_fp = args.input_video_fp
    output_img_dp = args.output_img_dp
    sample_img_dp = args.sample_img_dp

    run_obj = IndexGenerator(input_video_fp, sample_img_dp, output_img_dp)
    run_obj.run()

if __name__ == '__main__':
    main()