from distutils.core import setup, Extension

streamreader = Extension('streamreader',
					language = 'c++',
                    sources = ['streamreader.cpp'],
                    include_dirs = ['/home/jordan/Desktop/6.S062-car-swarm/streamreader/libs/ViconDataStreamSDK_CPP',
                    				'DebugServices'],
                    library_dirs = ['/home/jordan/Desktop/6.S062-car-swarm/streamreader/libs'],
                    libraries = ['boost_python', 'ViconDataStreamSDK_CPP'])

setup (name = 'Stream Reader',
       version = '1.0',
       description = 'Package for reading from Vicon Tracker Data Streams',
       ext_modules = [streamreader])