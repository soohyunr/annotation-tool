import json
import csv


def generate_csv():
    REASON1 = 'Reason 1'
    REASON2 = 'Reason 2'
    LABEL = 'Label'

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

    with open('shorten_reasons_REV2.json') as f:
        data = json.load(f)

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


def generate_tex():
    def score2label(score):
        if score == -1:
            return r'\textbf{Nonsensical}'
        elif score == -0.5 or score == -0.25:
            return r'\textbf{Unnatural}'
        elif score == 0:
            return 'Natural'

        print('who are you ?', score)
        exit(0)

    tex_template = r"""
\begin{table*}[]
\centering
\resizebox{\textwidth}{!}{%
\begin{tabular}{|p{4.6cm}|p{8cm}|l|}
\hline
\textbf{Reason 1} & \textbf{Reason 2} & \textbf{Label} \\ \hline
<%BODY%>
\end{tabular}%
}
\caption{ <%CAPTION%> }
\end{table*}
    """

    with open('shorten_reasons_REV2.json') as f:
        data = json.load(f)
        tex_all = ''
        for attribute_name, v1 in data.items():
            for attribute_value, v2 in v1.items():
                body = ''
                rows = []
                for reason1, reason2s in v2.items():
                    for i in range(0, len(reason2s), 2):
                        if i == 0:
                            reason1 = r'\multirow{' + str(len(reason2s)//2) + r'}{*}{\longcell{' + reason1 + r'}}'
                        else:
                            reason1 = ''
                        reason2 = reason2s[i]
                        score = reason2s[i + 1]

                        if i != len(reason2s) - 2:
                            label = score2label(score) + r' \\ \cline{2-3} ' + '\n'
                        else:
                            label = score2label(score) + r' \\ \hline ' + '\n'

                        rows.append([reason1, reason2, label])

                for i, row in enumerate(rows):
                    body += row[0] + r' & ' + row[1] + r' & ' + row[2]


                tex = tex_template.replace(r'<%BODY%>', body).replace(r'<%CAPTION%>', '{} - {}'.format(attribute_name, attribute_value.replace('_', ' ')))
                tex_all += tex + '\n\n'

        f = open('tex_all.tex', 'w+')
        f.write(tex_all)
        f.close()


if __name__ == '__main__':
    generate_tex()
