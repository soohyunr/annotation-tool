import json

if __name__ == '__main__':
    with open('shorten_reasons_REV2.json') as f:
        data = json.load(f)
        print(data)
