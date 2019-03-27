class Predictor:
    def __init__(self):
        from allennlp.predictors.predictor import Predictor
        self.predictor = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/decomposable-attention-elmo-2018.02.19.tar.gz")

    def predict(self, premise='', hypothesis='', ):
        result = self.predictor.predict(
            premise=premise,
            hypothesis=hypothesis,
        )
        # [entailment, contradiction, neutral]
        return result['label_probs']


if __name__ == '__main__':
    predictor = Predictor()
    print(predictor.predict(hypothesis='The information is straight-forward, and probably easy to verify.', premise='The sentence provides coherent, verifiable information.'))
