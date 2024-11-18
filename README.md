# Quote Streaming service proxy

This FastAPI-based service provides random quotes through a high-performance API endpoint. It asynchronously fetches data from multiple providers and offers responses in JSON, XML, HTML, and plain text formats. The service employs a background worker system that maintains a preloaded queue of quotes for optimal performance, falling back to predefined quotes if needed.
The application was designed with edge computing in mind, prioritizing response times by minimizing connection and memory overhead. Built using FastAPI and Python's async, with a extensible architecture that allows for new quote providers.

### To to run
Running the code it's under the scripts directory.
the goal was for commit hooks, but it became handy tool to allow formatter, linter, tests to run.
Like local github actions.

To run any of actions run `start app`, `linters`, `formatting`, `tests`
```bash
bash script/start.sh
bash script/linters.sh
bash script/fomatter.sh
bash script/tests.sh
```

### Run the app with docker
Takes a while.
```bash
docker run --rm -it -p 8000:8000 $(docker build -q .)
```

### Run app locally
```bash
bash script/start.sh
```

### Run
Run the below, or right click url for the browser.
```bash
curl http://127.0.0.1:8000
```
### Swagger
```bash
http://127.0.0.1:8000/docs
```


### Extending the app
Adding new DataProvide quote service.
The idea that extending the application should be simple and without impacting the result of the application.

Within the following file add a new data provider.
[config.py](src/quote/config.py)
```python
DATA_PROVIDERS = {
    "quotable": DataProvider(
        name="quotable",
        url="https://api.quotable.io/quotes/random",
        verify=False
    ),
    "zenquotes":
        DataProvider(
            name="zenquotes",
            url="https://zenquotes.io/api/random"
    ),
    "new_data_provider":
        DataProvider(
            name="new_data_provider",
            url="https://new_data_provider/api/random"
    ),
}
```
Now create a parser.

[parsing.py](src/quote/parsing.py)
```python
def provider_new_data_provider_parsing(data: dict[str, Any]) -> Quote:
    """
    Parse data from new_data_provider service into a Quote object.

    Args:
        data (dict): Raw data from new_data_provider data provider service.

    Returns:
        Quote: Parsed Quote object.

    Example:
        {
            "content": "Her it.",
            "author": "Napoleon Hill",
            "tags": ["Success"],
        }
    """
    return Quote(
        author=data["author"],
        text=data["content"],
        tags=tuple(data["tags"]),
        source="new_data_provider"
    )
```
[parsing.py](src/quote/parsing.py)
Register the parser
```python
PARSERS = {
    "quotable": provider_quotable_parsing,
    "zenquotes": provider_zenquotes_parsing,
    "new_data_provider": provider_new_data_provider_parsing,
}
```


