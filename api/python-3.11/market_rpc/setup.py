from setuptools import setup, find_packages

setup(
    name="onlexnet_market",
    version="0.0.7",
    packages=find_packages(),
    # include non-code files like schema.avsc
    package_data={
        '': ['*.avsc'],
    },
    include_package_data=True
)