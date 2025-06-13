###  Building the Pysa lab docker
```
docker compose build && docker compose up
```

### Analysing the exerice
enter into the exercise directory
```
pyre --typeshed=../../../stubs/typeshed --search-path=../../../stubs/typeshed/typeshed/stdlib/ analyze
```
