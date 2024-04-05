from setuptools import setup, find_packages

setup(
    name="onlexnet_market",
    version="0.1.3",
    packages=find_packages(),
    # include non-code files like schema.avsc
    # it is required by code generated for AVRO classes
    package_data={
        '': ['*.avsc'],
    },
    include_package_data=True    
)