from setuptools import setup, find_packages

with open("requirements.txt") as requirements_file:
    requirements = requirements_file.readlines()

setup(
    name='s3calc',
    version='0.1.0',
    description='S3 tool used to calculate transitions to other S3 storage types',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},

    install_requires=requirements,

    entry_points={
        'console_scripts': [
            's3calc = s3calc.s3_costs:main',
        ]
    },
)
