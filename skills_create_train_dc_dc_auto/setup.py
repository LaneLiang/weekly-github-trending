from setuptools import setup, find_packages

setup(
    name="dc_auto_tune",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0.0",
        "numpy>=1.24.0",
        "gymnasium>=0.29.0",
        "pyyaml>=6.0",
        "openai>=1.0.0",
        "matplotlib>=3.7.0",
        "tensorboard>=2.13.0",
    ],
    python_requires=">=3.10",
)
