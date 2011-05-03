from distutils.core import setup, Extension

setup(name="example", version="0.0",
  ext_modules = [Extension("example", ["examplemodule.cpp"])])
