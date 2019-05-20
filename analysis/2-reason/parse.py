import json
import csv


def score2label(score):
    if score == -1:
        return 'Nonsensical'
    elif score == -0.5 or score == -0.25:
        return 'Unnatural'
    elif score == 0:
        return 'Natural'


def get_reason1(before, reason1):
    if before != reason1:
        return reason1
    else:
        return ''


if __name__ == '__main__':
    with open('shorten_reasons_REV2.json') as f:
        data = json.load(f)

        REASON1 = 'Reason 1'
        REASON2 = 'Reason 2'
        LABEL = 'Label'

        for attribute_name, v1 in data.items():
            for attribute_value, v2 in v1.items():
                csv_path = './{}.{}.csv'.format(attribute_name.replace('/', ''), attribute_value.replace('/', ''))
                with open(csv_path, 'w', newline='') as csvfile:
                    fieldnames = [REASON1, REASON2, LABEL]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()

                    before = ''
                    for reason1, reason2s in v2.items():
                        for i in range(0, len(reason2s), 2):
                            reason2 = reason2s[i]
                            score = reason2s[i + 1]

                            writer.writerow({REASON1: get_reason1(before, reason1), REASON2: reason2, LABEL: score2label(score)})
                            before = reason1
