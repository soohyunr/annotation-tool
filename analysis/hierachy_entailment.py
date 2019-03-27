if __name__ == '__main__':
    from analysis.data_util import Annotation
    from analysis.entailment import Predictor
    from tqdm import tqdm

    anno = Annotation()
    reasons = anno.get_reasons(anno.acceptance, anno.strong_accept)

    predictor = Predictor()

    with open('./data/entailment/{}_{}.txt'.format(anno.acceptance, anno.strong_accept), 'w+') as f:
        hypothesis = reasons[0]
        for reason in tqdm(reasons):
            f.write('Text : {}\n'.format(reason))
            f.write('Hypothesis: {}\n'.format(hypothesis))
            result = predictor.predict(premise=reason, hypothesis=hypothesis)
            f.write('Prediction: {}/{}/{}\n\n'.format(result[0], result[1], result[2]))
