try:
  import google.colab
  get_ipython().system('pip install ipympl')
  import importlib  
  magneticrhr = importlib.import_module("right-hand-rules.magneticrhr")
except:
  import magneticrhr

m = magneticrhr.MagneticRHR()
