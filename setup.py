from setuptools import setup, find_packages

setup(
    name="generic_simulator",
    version="0.1.0",
    description="A generic device simulator using SimPy with SQLite configuration",
    author="Generic Simulator Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "simpy>=4.0.1",
        "typing-extensions>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "generic-simulator=generic_simulator.cli:main",
        ],
    },
    python_requires=">=3.8",
)
