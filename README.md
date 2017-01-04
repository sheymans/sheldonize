
Running the local server:

```
./manage.py runserver --settings=sheldonize.settings.dev
```

Get the amount of git commits:

```
git rev-list HEAD --count
```


Deploy to AWS:

```
fab deploy
```