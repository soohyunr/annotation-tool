# annotation-tool


## prerequisites
```python
import nltk
nltk.download('punkt')
```

```bash
pip3 install -r requirements.txt
export PYTHONPATH=.
python app.py

# background
export PYTHONPATH=.
nohup python3 app.py &
echo $! > save_pid.txt

# kill background
kill -9 `cat save_pid.txt`
```