try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

setup(
    name='saw',
    version='0.1',
    description='saw - Command line utility for AWS EC2 scaffolding and backup',
    url='https://github.com/checkaayush/SAW',
    author='Aayush Sarva',
    author_email='checkaayush@gmail.com',
    packages=['saw'],
    entry_points={
        'console_scripts' : ['saw = saw.saw:main']
    },
    install_requires=['setuptools>=24.0.3', 'nose>=1.3.4'],
    package_data={'saw': ['config.json']},
    include_package_data=True,
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Infrastructure'
    ]
)
