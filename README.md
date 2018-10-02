# annotation-tool


## prerequisites
```python
import nltk
nltk.download('punkt')
```

```bash
pip3 install -r requirements.txt
python app.py

# background
nohup python3 app.py &
echo $! > save_pid.txt

# kill background
kill -9 `cat save_pid.txt`
```