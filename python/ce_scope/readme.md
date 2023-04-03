##Instrucciones de instalación del analizador ce_scope.py 
(estas instrucciones se ejecutan solo la primera vez. para cualquier sistema operativo.)

0.    Abrir terminal

1.    Descargar e instalar Anaconda desde 
 	https://www.anaconda.com/products/distribution#Downloads 

2.A  Para macOS/Linux: abrir terminal
2.B  Para windows: abrir anaconda powershell

3.     Crear entorno speccoms copiando y pegando en terminal/powershell y pulsando Enter:
	conda create -n speccoms python=3.9

4.     Activar el entorno:
	conda activate speccoms	

5.     Instalar dependencias, ejecutando una instrucción a la vez:
	pip install pygame oscpy
pip install numpy
pip install opencv-python
pip install scikit-learn scikit-image pillow
pip install ipython

6.     Descargar y descomprimir los archivos del repositorio 
	https://github.com/interspecifics/bio-exploraciones 

7.     Desde la terminal desplazarse a la carpeta descomprimida:
(depende de la estructura del directorio donde se halla descargado) 
por ejemplo, si la carpeta fue descomprimida en Downloads:	
cd Downloads/bio-exploraciones/python/ce_scope

8.     Ejecutar usando el comando en la terminal:
	python ce_scope.py


##Instrucciones de ejecución ce_scope.py 
(una vez que ha sido instalado, ver arriba. para cualquier sistema operativo.)

0.    Abrir terminal
1.    Desde terminal/powershell activar el entorno:
	conda activate speccoms
2.     Ejecutar usando el comando en la terminal:
	python ce_scope.py
3.     Have fun!





Guía de sonificación puredata/automatonism
0.     Instalación:
	https://puredata.info/downloads
https://www.automatonism.com/the-software
1.     Patching automatonism
https://github.com/Lessnullvoid/automatonism_workshop
