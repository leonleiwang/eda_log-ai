from setuptools import find_packages, setup


setup(
    name="eda-log-ai",
    version="0.1.0",
    description="Offline EDA log triage assistant for local engineering workflows.",
    package_dir={"": "src"},
    packages=find_packages("src"),
    entry_points={"console_scripts": ["eda-log-ai=eda_log_ai.cli:main"]},
    python_requires=">=3.10",
)
