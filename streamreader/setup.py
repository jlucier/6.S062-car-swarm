from distutils.core import setup, Extension

streamreader = Extension('streamreader',
					language = 'c++',
                    sources = ['streamreader.cpp'],
                    libraries = ['boost_python', 'ViconDataStreamSDK_CPP'])

setup (name = 'Stream Reader',
       version = '1.0',
       description = 'Package for reading from Vicon Tracker Data Streams',
       ext_modules = [streamreader])