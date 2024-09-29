from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='lightweight_charts',
    version='2.1',
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[
        'pandas',
        'pywebview>=5.0.5',
    ],
    package_data={
        'lightweight_charts': ['js/*'],
    },
    author='louisnw',
    license='MIT',
    description="Python framework for TradingView's Lightweight Charts JavaScript library.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/louisnw01/lightweight-charts-python',
)
