import pickle, os


class Predictor:
    cache_path = './data/pkl/entailment_cache.pkl'
    _cache = dict()

    def __init__(self):
        from allennlp.predictors.predictor import Predictor
        self.predictor = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/decomposable-attention-elmo-2018.02.19.tar.gz")
        print('[Predictor] loaded')

        if os.path.exists(self.cache_path):
            self._cache = pickle.load(open(self.cache_path, "rb"))

    def predict(self, premise='', hypothesis='', ):
        cache_key = '{}->{}'.format(premise, hypothesis)
        if cache_key in self._cache:
            return self._cache[cache_key]['label_probs']

        result = self.predictor.predict(
            premise=premise,
            hypothesis=hypothesis,
        )
        # [entailment, contradiction, neutral]
        self._cache[cache_key] = result
        self.save()
        return result['label_probs']

    def save(self):
        pickle.dump(self._cache, open(self.cache_path, "wb"))


if __name__ == '__main__':
    predictor = Predictor()
    print(predictor.predict(hypothesis='The information is straight-forward, and probably easy to verify.', premise='The sentence provides coherent, verifiable information.'))
