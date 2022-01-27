#!/usr/bin/env bash
# This script will re-generate reproducible lockfiles
# Execution needs to be from inside the `conda` folder

ENV_FILE="environment.yml"
LOCK_ENV='CondaLock'

# Generate CondaLock environment unless present
conda env list | grep ${LOCK_ENV} > /dev/null

if [[ $? -eq 1 ]]; then
  conda create -q -y -n ${LOCK_ENV} -c conda-forge conda-lock=0.13 mamba=0.20
fi

# https://github.com/conda/conda/issues/7980#issuecomment-492784093
eval "$(conda shell.bash hook)"
conda activate ${LOCK_ENV}

if [[ ! -s "${ENV_FILE}" ]]; then
    >&2 printf " Missing ${ENV_FILE} to generate environments with\n"
    >&2 printf " Are you inside the 'conda' folder?\n"
    exit 1
fi

# Local environments
## Generate explicit lock files (optional -p win-64)
conda-lock lock --mamba -f ${ENV_FILE} -p linux-64 -p osx-64

# BinderHub support
## Generate environment.yml for binder compatibility
printf "Generate environment.yml for BinderHub \n"
conda-lock lock --mamba -f ${ENV_FILE} -p linux-64 -k env
mv conda-linux-64.lock.yml ../binder/environment.yml

# Remove CondaLock environment when the last command was successful
if [[ $? -eq 0 ]]; then
  conda deactivate
  conda remove -q -y --name ${LOCK_ENV} --all
fi
