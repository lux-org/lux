from setuptools import setup, find_packages
from os import path

HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='lux-api',  # PyPI Name (pip install [name])
    version='0.1.1',  # Required
    description='A Python API for Intelligent Data Discovery',  # Project description (Optional)
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://github.com/lux-org/lux',  # Optional
    maintainer='Doris Jung-Lin Lee',  # Optional
    maintainer_email='dorisjunglinlee@gmail.com',  # Optional
    classifiers=[  # Optional
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Other Audience',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Visualization',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3'
    ],
    keywords='visualization analytics data-science insight discovery',  # Optional
    include_data_package=True,
    packages=find_packages(),  # Required
    python_requires='>=3.5',
    install_requires=['pandas','altair'],  # Optional
    extras_require={  # Optional
        'test': ['pytest']
    }
)