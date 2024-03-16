from setuptools import setup, find_packages

setup(
    name="onlexnet_scheduler",
    version="0.0.1",
    packages=find_packages(),
    # include non-code files like schema.avsc
    package_data={
        '': ['*.avsc'],
    },
    include_package_data=True
)