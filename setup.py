from setuptools import setup, find_packages
from setuptools_rust import RustExtension, Binding


setup(
    name="paradox-savedata",
    version="0.1.0",
    description="Parser for Paradox game save data",
    author="",
    packages=find_packages(),
    rust_extensions=[
        RustExtension(
            "paradox_savedata.parser.rust_parser",
            "Cargo.toml",
            binding=Binding.PyO3,
        )
    ],
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=[],
    setup_requires=["setuptools-rust>=0.11.4"],
)