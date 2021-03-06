import torch

class DatapointsRepComparer(object):
    def __init__(self, representation_extractor, comparison):
        self.representation_extractor = representation_extractor
        self.comparison = comparison

    def compare_datapoints(self, point1_key, point2_key, point1: torch.Tensor = None, point2: torch.Tensor = None):
        point1_rep = self.representation_extractor.get_layers_representation(point1, point1_key)
        point2_rep = self.representation_extractor.get_layers_representation(point2, point2_key)

        comparisons = {}

        for key in point1_rep:
            comparisons[key] = self.comparison.compare(point1_rep[key], point2_rep[key])

        return comparisons