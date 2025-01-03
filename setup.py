from setuptools import setup, find_packages

setup(
    name='kaeru-webfs-colab',
    version="0.0.1",
    description='kaeru-webfs for Google Colab',
    author='kaeru-shigure',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'kaeru_webfs_colab': [
            'bin/*',
        ],
    },
    license='MIT',
    zip_safe=False,
)