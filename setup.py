from setuptools import setup, find_packages

setup(
    name="data_science_project",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "torch", "torchvision", "pandas", "numpy", "scikit-learn", "xgboost", "matplotlib", "seaborn"
    ],
    include_package_data=True,
    zip_safe=False
)