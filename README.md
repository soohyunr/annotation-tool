# annotation-tool

This program is an annotation tool, which distributes texts that may arise copyright issue when distributing original text type, to several annotators without copyright issues. 

## Prerequisites

```bash
pip3 install -r requirements.txt

# Modify the settings in config.sample.py
vi config.sample.py

mv config.smaple.py config.py
```

## Run
```bash
sudo python3 app.py
```

To run background
```bash
sudo nohup python3 app.py &
```
