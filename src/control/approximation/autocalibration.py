import src.benchmark.approximation_experiment.collect_data_for_approximation as collect_data_for_approximation


class Autocalibration:
    def __init__(self, raw_controller, position_detector):
        self.raw_controller = raw_controller
        self.position_detector = position_detector

    def run(self):
        print("welcome in  auto-calibration mode. Please, enjoy your arm!")
        print("""Put camera in front of arm's glyphs and make sure that all four glyphs in max/
        min arm position are visible""")

        # ask about custom duration of experiment
        try:
            duration = int(input("""Put experiment duration in hours. Default is 2"""))
            print('Started data_for_approximation experiment with duration: %'.format(duration))
            collect_data_for_approximation.start(self.raw_controller, self.position_detector, running_time=duration)
        except ValueError:
            print('Started data_for_approximation experiment with default duration')
            collect_data_for_approximation.start(self.raw_controller, self.position_detector)
            pass

        print("Experiment finished. Results in data dir")

