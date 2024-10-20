# Dashboard App

## Setup Environment - Anaconda
```
conda create --name main-ds python=3.9.19
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```
mkdir analisis-data
cd analisis-data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run steamlit app
```
streamlit run dashboard/app.py
```
