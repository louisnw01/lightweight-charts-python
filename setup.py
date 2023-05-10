from setuptools import setup, find_packages

setup(
    name='lightweight_charts',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'pywebview',
    ],
    # Additional package metadata
    author='louisnw01',
    description="Python framework for TradingView's Lightweight Charts JavaScript library.",
    url='https://github.com/SORT-THIS-OUT',
)