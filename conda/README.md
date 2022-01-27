# Conda environment management

**The only file you should need to edit in this folder is `conda/environment.yml`. This file defines the set of conda-packages needed to render the full website.**

If you've edited this file to change package versions or add new ones, be sure to re-lock the environment by running `./lock-environment.sh`

lockfiles ensure everyone working on this project has exactly the same development environment. So if every time you re-lock the packages, be sure to create a new environment:

```
conda deactivate
conda remove --name hackweek --all
conda create --name hackweek --file conda-linux-64.lock
```
