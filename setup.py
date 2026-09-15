import setuptools

setuptools.setup(
    name="apify-data-scrapers",
    version="1.1.2",
    author="Joseph McRell",
    description="MCP server exposing 30 Apify public-data scrapers as tools (Google Maps, news, SEO, jobs, SEC, procurement, registries, and more)",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jlucasmcrell/apify-scrapers",
    project_urls={
        "Documentation": "https://apify.revenuesystemslabs.com/",
        "Source": "https://github.com/jlucasmcrell/apify-scrapers",
        "Apify Store": "https://apify.com/captainhandsome",
    },
    keywords=[
        "apify",
        "mcp",
        "model-context-protocol",
        "public-data",
        "government-data",
        "lead-generation",
        "workflow-automation",
        "n8n",
        "make",
    ],
    packages=setuptools.find_packages(),
    py_modules=["mcp_server"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[],
    extras_require={"examples": ["apify-client>=1.8.0", "pandas>=2.0", "python-dotenv>=1.0"]},
    entry_points={
        "console_scripts": [
            "apify-data-scrapers=mcp_server:main",
        ],
    },
)
