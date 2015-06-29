import random
from knowledgegenerator import KnowledgeGenerator


class RandomSampleKnowledgeGenerator(KnowledgeGenerator):
    def __init__(self, population=100, sample_size=1):
        KnowledgeGenerator.__init__(self)
        assert population > 0
        assert sample_size > 0
        self.numbers = set(range(population))
        self.sample_size = sample_size

    def generate_knowledge(self):
        return random.sample(self.numbers, self.sample_size)
