import argparse
from argparse import ArgumentDefaultsHelpFormatter
from lib.calculator.parallelRunVideoCalculator import ParallelRunVideoCalculator


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

    input_data = {'input_video_fp': args.input_video_fp, 'output_img_dp': args.output_img_dp,
                  'input_sample_dp': args.sample_img_dp}

    run_obj = ParallelRunVideoCalculator(**input_data)
    run_obj.run()

if __name__ == '__main__':
    main()
