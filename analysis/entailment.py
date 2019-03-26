if __name__ == '__main__':
    from allennlp.predictors.predictor import Predictor
    predictor = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/decomposable-attention-elmo-2018.02.19.tar.gz")
    predictor.predict(
        hypothesis="Two women are sitting on a blanket near some rocks talking about politics.",
        premise="Two women are wandering along the shore drinking iced tea."
    )
