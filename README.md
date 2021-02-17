# Lux 
With Program Analysis -- Development version. 

See below for install instructions

## Easy install
`pip install git+https://github.com/willeppy/lux.git`

Then you can run `import lux` in jupyter environments. Note this wont work outside of ipython envs.

## Set up locally for dev purposes


```bash
git clone https://github.com/willeppy/lux.git
```

You can install Lux by building from the source code in your fork directly:

```bash
cd lux/
pip install -r requirements.txt
pip install -r requirements-dev.txt
python setup.py install
```

When you make a change to the source code in the `lux/` folder, you can rebuild by doing this: 

```bash
python setup.py install
```

## Debugging and Testing with Jupyter

It is often useful to test your code changes via Jupyter notebook. To debug your code changes, you can import a "local" copy of Lux without having to rebuild the changes everytime.

For example, you can have a test notebook `test.ipynb` that imports. Note that when you do `import lux` at this path, it imports the local lux/ module instead of your global installation (either system-wide or in your virtual environment).

__*NOTE*__: if you run a notebook in another directory and import lux it will import the lux version from pip and NOT your local dev version. Run `lux.__path__` to see where your package is being imported from.

```
lux/
    - test.ipynb
    - lux/
```

## Jupyter widget

May have to re-build jupyter after widget is installed, to do so use
```bash
jupyter lab build
```
