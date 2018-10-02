# annotation-tool


## Prerequisites

Step1.
```bash
pip3 install -r requirements.txt
```

Step2. 
```python
import nltk
nltk.download('punkt')
```

Step3.
```bash
# Modify the settings in config.sample.py
vi config.sample.py
mv config.smaple.py config.py
```

## Run
```bash
python app.py
```

```bash
# background
nohup python3 app.py &
```