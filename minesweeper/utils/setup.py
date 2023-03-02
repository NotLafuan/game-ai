from distutils.core import setup, Extension

module = Extension("utilsModule", sources=["utils.c"])
setup(name="Utils",
      version=1.0,
      description="For utils",
      ext_modules=[module])
