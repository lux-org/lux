from setuptools import setup, find_packages
from os import path

HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(HERE, 'requirements.txt')) as fp:
    install_requires = fp.read()

setup(
    name='lux-api',  # PyPI Name (pip install [name])
    version='0.2.0',  # Required
    description='A Python API for Intelligent Data Discovery', 
    long_description=long_description,  
    long_description_content_type='text/markdown',  
    url='https://github.com/lux-org/lux',  
    author='Doris Jung-Lin Lee',  
    author_email='dorisjunglinlee@gmail.com', 
    license         = 'Apache-2.0 License',
    classifiers=[  
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Other Audience',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Visualization',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3'
    ],
    keywords='visualization analytics data-science insight discovery', 
    include_data_package=True,
    packages=find_packages(),  # Required
    python_requires='>=3.5',
    install_requires=install_requires,
    extras_require={  
        'test': ['pytest']
    }
)