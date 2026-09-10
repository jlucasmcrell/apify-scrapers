import setuptools

setuptools.setup(
    name="apify-data-scrapers",
    version="1.0.0",
    author="Joseph McRell",
    description="MCP tools and SDK for Apify public data scrapers (Google Maps, SEC EDGAR, Glassdoor, Contractor Licenses)",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jlucasmcrell/apify-scrapers",
    packages=setuptools.find_packages(),
    py_modules=["mcp_server"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "apify-client>=1.8.0",
        "mcp>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "apify-data-scrapers=mcp_server:main",
        ],
    },
)
