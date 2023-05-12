from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='lightweight_charts',
    version='1.0.1',
    packages=find_packages(),
    python_requires='>=3.9',
    install_requires=[
        'pandas',
        'pywebview',
    ],
    author='louisnw',
    license='MIT',
    description="Python framework for TradingView's Lightweight Charts JavaScript library.",
    long_description=long_description,
    url='https://github.com/louisnw01/lightweight-charts-python',
)
