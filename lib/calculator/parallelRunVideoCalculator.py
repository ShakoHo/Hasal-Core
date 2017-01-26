import pp
import os
import time
import copy
import importlib
from videoCalculator import VideoCalculator


class ParallelRunVideoCalculator(VideoCalculator):

    def __init__(self, **kwargs):
        super(ParallelRunVideoCalculator, self).__init__(**kwargs)

        # init converter object
        converter_class = getattr(importlib.import_module(self.calculator_module['converter']['path']),
                                  self.calculator_module['converter']['name'])
        self.converter_obj = converter_class(self.input_video_fp, self.output_img_dp)

        # init generator object
        self.generator_obj_list = []
        self.generator_gen_data_fp_list = []
        self.generator_gen_result_fp_list = []
        self.generator_deplib_list = []
        for generator_data in self.calculator_module['generator']:
            generator_class = getattr(importlib.import_module(generator_data['path']), generator_data['name'])
            generator_obj = generator_class(self.input_sample_dp, self.output_img_dp)
            self.generator_obj_list.append(generator_obj)
            self.generator_gen_data_fp_list.append(generator_obj.gen_raw_data)
            self.generator_gen_result_fp_list.append(generator_obj.gen_result)
            for deplib in generator_data['deplib']:
                if deplib not in self.generator_deplib_list:
                    self.generator_deplib_list.append(deplib)
        self.default_thread_no = 4
        self.default_max_thread_no = 8
        self.default_sleep_time = 3

    def run(self):
        # converting videos to images (default converter should be ffmpegconverter)
        # self.converter_obj.start_converting()

        start_counter = 0
        processed_img_fn_list = []
        time.sleep(self.default_sleep_time)
        while True:
            print "start_counter = [%s]" % str(start_counter)
            current_img_fn_list = os.listdir(self.output_img_dp)
            if start_counter == len(current_img_fn_list):
                break
            else:
                start_counter = len(current_img_fn_list)
                processing_img_fn_list = copy.deepcopy(list(set(current_img_fn_list) - set(processed_img_fn_list)))
                processing_img_fn_list.sort()
                print "processing_img_fn_list [%s] - [%s]" % (processing_img_fn_list[0], processing_img_fn_list[-1])
                self.generate_raw_data(processing_img_fn_list)
                processed_img_fn_list.extend(copy.deepcopy(processing_img_fn_list))
                time.sleep(self.default_sleep_time)

        #return self.generate_result()

    def generator_gen_data(self, input_fn_list):
        for image_fn in input_fn_list:
            image_fp = os.path.join(self.output_img_dp, image_fn)
            #for generator_obj in input_generator_obj_list:
            #self.generator_obj_list[0].gen_raw_data(image_fp)
            print image_fp

    def generator_gen_result(self, input_fn_list, input_generator_obj_list):
        for image_fn in input_fn_list:
            image_fp = os.path.join(self.output_img_dp, image_fn)
            for generator_obj in input_generator_obj_list:
                generator_obj.gen_result(image_fp)

    def generate_chunks(self, input_list, input_chunk_no):
        return_list = []
        for i in xrange(0, len(input_list), input_chunk_no):
            return_list.append(input_list[i:i + input_chunk_no])
        return return_list

    def generate_raw_data(self, current_fn_list):
        jobs = []

        # init ppservers
        ppservers = ()
        self.job_server = pp.Server(self.default_thread_no, ppservers=ppservers)

        # divide fn_list to thread_no portion
        chunk_list = self.generate_chunks(current_fn_list, self.default_thread_no)
        print "chunk_list [%s] - [%s]" % (chunk_list[0], [chunk_list][-1])
        # parallel execute all generator's gen_raw_data function
        o = ooo()
        for index in range(len(chunk_list)):
            jobs.append(self.job_server.submit(o.test, (chunk_list[index], ),
                                               (), ()))

        for job in jobs:
            print job()

    def generate_result(self):
        jobs = []
        full_fn_list = os.listdir(self.output_img_dp)
        chunk_list = self.generate_chunks(full_fn_list, self.default_max_thread_no)

        # parallel execute all generator's gen_result function
        for index in range(len(chunk_list)):
            jobs.append(self.job_server.submit(self.generator_gen_result, (chunk_list[index], self.generator_obj_list),
                                               tuple(self.generator_gen_result_fp_list), tuple(self.generator_deplib_list)))


import threading

class ooo(threading.Thread):
    def test(self, list):
        print 'haha'