Notas de instalación:

1. crear y activar entorno
conda create -n speccoms python=3.9
conda activate speccoms

2. instalar dependencias
pip install pygame oscpy 
pip install pysimplegui numpy
pip install opencv-python 
pip install sklearn scikit-image pillow
pip install ipython

3. copiar directorio
ce_scope
    |
    |-ce_scope.py
    |-tracker.py
    |-RevMiniPixel.ttf

4. desde la terminal moverse al directorio y ejecutar
ce_scope
python ce_scope.py
