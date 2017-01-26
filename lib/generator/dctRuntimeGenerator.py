import cv2
import numpy
import runtimeGenerator


class DctRuntimeGenerator(runtimeGenerator.RuntimeGenerator):
    def __init__(self, input_sample_dp, output_img_dp):
        self.raw_data = {}
        self.input_sample_dp = input_sample_dp
        self.output_img_dp = output_img_dp

    def gen_raw_data(self, image_fp, skip_status_bar_fraction=1.0):
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

    def gen_result(self):
        pass

