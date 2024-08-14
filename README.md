# pyedgarai

A package for retrieving SEC filings and parse them using LLMs

## Installation

```bash
$ pip install pyedgarai
```

## Usage

- Retrieve Apple's 10-K filings from the SEC

```python
from pyedgarai import get_company_facts

cik = 320193

get_company_facts(cik)
```



## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`pyedgarai` was created by Juan F. Imbet. It is licensed under the terms of the MIT license.

## Credits

`pyedgarai` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
