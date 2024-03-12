Run and keep working local pypi server

- run local pypi server (the first run)
  ```
  python -m venv .venv
  . .venv/bin/activate
  pip install -r requirements.txt
  . start-devpi.sh
  ```

- run local pypi server (second run)
  ```
  python -m venv .venv
  . .venv/bin/activate
  . start-devpi.sh
  ```

Build and push python libs
```
. build-libs-python.sh
```

## Useful links
- [devpi by practice](https://stefan.sofa-rockers.org/2017/11/09/getting-started-with-devpi/)
- [devpi demo](https://www.youtube.com/watch?v=-fz6k44ZHMzQ)
- [devpi client configuration](https://opensource.com/article/18/7/setting-devpi)
