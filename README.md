# annotation-tool


## prerequisites
step1. 
```python
import nltk
nltk.download('punkt')
```

step2.
```bash
pip3 install -r requirements.txt
```

step3.
```bash
# Modify the settings in config.sample.py
vi config.sample.py
mv config.smaple.py config.py
```

## run
```bash
python app.py
```

```bash
# background
nohup python3 app.py &
```