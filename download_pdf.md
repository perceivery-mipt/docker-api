### Экспорт ноутбука `.ipynb` в `.html` через `python3`

Конвертация Jupyter Notebook в HTML-файл через `python3`.

Гриша, специально тебе :)
  
```
cd /Папка с проектом
python3 -m pip install nbconvert
python3 -m pip install jupyter
python3 -m jupyter trust "Название ноута.ipynb"
python3 -m nbconvert --to html "Название ноута.ipynb"
open "Название ноута.html"
```
Потом просто `Export as PDF` из Safari
