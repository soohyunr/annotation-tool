# annotation-tool


## prerequisites
Step1. 
```python
import nltk
nltk.download('punkt')
```

Step2.
```bash
pip3 install -r requirements.txt
```

Step3.
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