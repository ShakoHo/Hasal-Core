from baseCalculator import BaseCalculator


class VideoCalculator(BaseCalculator):
    def __init__(self, **kwargs):
        super(VideoCalculator, self).__init__(**kwargs)
        self.calculator_module = {'converter': {'path': 'lib.converter.ffmpegConverter', 'name': 'FfmpegConverter'},
                                  'generator': [
                                      {'path': 'lib.generator.dctRuntimeGenerator', 'name': 'DctRuntimeGenerator',
                                       'deplib': ['cv2', 'numpy', 'runtimeGenerator']}]}

