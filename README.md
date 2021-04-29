# Lux 
With Program Analysis -- Development version. 

See below for install instructions

## Easy install
```
pip install git+https://github.com/willeppy/lux.git
jupyter labextension install @jupyter-widgets/jupyterlab-manager
jupyter labextension install luxwidget
```

Then you can run `import lux` in jupyter environments. Note this wont work outside of ipython envs.

## Set up locally for dev purposes

You can install Lux by building from the source code in your fork (or clone) directly:
```bash
git clone https://github.com/willeppy/lux.git
cd lux/
pip install -r requirements.txt
pip install -r requirements-dev.txt
python setup.py install
```

There are two ways to make sure your local changes show up when running locally. 

To rebuild and re-install the local version of `lux` system wide (or conda profile wide) run the below.
```bash
python setup.py install
```

However since this takes a bit to run it can be cumbersome. To develop faster, run a jupyter notebook __in this repo__ (like `DEMO_NB.ipynb`). Changes will propogate when you kill and re-start jupyter. You do not have to re-run the install script for changes to show up.

__*NOTE*__: if you run a notebook in another directory and import lux it will import the lux version from pip and NOT your local dev version. Run `lux.__path__` to see where your package is being imported from.

## Luxwidget

If you are also making local edits to the [luxwidget](https://github.com/willeppy/lux-widget) repo, then follow the instructions in that repo to install. After making changes to `luxwidget`, re-install by running the below in the `luxwidget` repo

```bash
pip install . 
```

May have to re-build jupyter after widget is installed for the first time, to do so use
```bash
jupyter lab build
```