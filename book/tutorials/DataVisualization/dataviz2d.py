# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.5
#   kernelspec:
#     display_name: hackweek
#     language: python
#     name: hackweek
# ---

# %% [markdown]
# # **Making nice maps for posters with Python** 🗺️+🐍
#
# To communicate your results effectively to people 🧑‍🤝‍🧑,
# you may come to a point where making maps are needed.
#
# These maps could be created for a conference poster,
# a presentation, or even for a social media 🐦 post!
#
# In this tutorial 🧑‍🏫, we'll focus on making basic 2D maps,
# and by the end of this lesson, you should be able to:
#   - Set up basic map elements - basemap, overview map, title and axis annotations 🌐
#   - Plot raster data (images/grids) and choose a Scientific Colour Map 🌈
#   - Plot vector data (points/lines/polygons) with different styles 🗠
#   - Save and export your map into a suitable format for your audience 😎

# %% [markdown]
# ## 🎉 **Getting started**
#
# Once you have an idea for what to map, you will need a way to draw it 🖌️.
#
# There are plenty of ways to make maps 🗾, from pen and paper to Photoshop.
#
# We'll start by loading some of these tools, that help us to process and visualize our data 📊.

# %%
# Install development versions
# # !pip install https://github.com/icesat2py/icepyx/archive/refs/heads/development.zip
# Note, need to restart jupyter kernel after installation for new version to show up

# %%
import icepyx as ipx  # for downloading and loading ICESat-2 data
import xarray as xr  # for working with n-dimensional data

# %% [markdown]
# Just to make sure we're on the same page,
# let's check that we've got the same versions.

# %%
print(f"icepyx version: {ipx.__version__}")

# %% [markdown]
# ### A note about layers 🍰
#
# What do you do when you want to plot several
# datasets overlaping the same geographical area? 🤔
#
# A general rule of thumb is to have the raster images on the
# 'bottom' 👎🏽, and the vector data plotted on 'top' 👍🏽.
#
# Think of it like making a fancy birthday cake 🎂, starting
# with the dense cake flour (raster), and decorating the
# colourful icing on top!

# %% [markdown]
# # 0️⃣ The data
#
# ## Download ATL14 Gridded Land Ice Height 🏔️
#
# This is a 125m ATLAS/ICESat-2 L3B raster
# grid product over the cryosphere (ice) regions.
#
# Specifically, this includes places like:
#
# - Antarctica (AA) 🇦🇶
# - Alaska (AK) 🏴󠁵󠁳󠁡󠁫󠁿
# - Arctic Canada North (CN) 🇨🇦
# - Arctic Canada South (CS) 🇨🇦
# - Greenland and peripheral ice caps (GL) 🇬🇱
# - Iceland (IS) 🇮🇸
# - Svalbard (SV) 🇸🇯
# - Russian Arctic (RA) 🇷🇺
#
# 🔖 References:
#
# - Smith, B., B. P. Jelley, S. Dickinson, T. Sutterley, T. A. Neumann, and K. Harbeck. 2021.
#   ATLAS/ICESat-2 L3B Gridded Antarctic and Arctic Land Ice Height, Version 1. Boulder, Colorado USA.
#   NASA National Snow and Ice Data Center Distributed Active Archive Center.
#   doi: https://doi.org/10.5067/ATLAS/ATL14.001.
# - Official NSIDC download source - https://nsidc.org/data/ATL14
# - Source code for generating ATL14/15 - https://github.com/SmithB/ATL1415

# %%
# Set up an instance of an icepyx Query object
# for a Region of Interest located over Iceland
region_iceland = ipx.Query(
    product="ATL14",  # ICESat-2 Gridded Annual Ice Product
    spatial_extent=[-28.0, 62.0, -10.0, 68.0],  # minlon, minlat, maxlon, maxlat
)

# %% [markdown]
# Inside of the `region_iceland` class instance are attributes
# that can be accessed using dot '.' something.
#
# ⏩ Type out `region_iceland.` and press `Tab` to see some of them!

# %%
# Check that we've selected the right region
region_iceland.visualize_spatial_extent()

# %%
# See the version of the ATL14 product we're using
print(region_iceland.product)
print(region_iceland.product_version)

# %% [markdown]
# 🔖 For a more complete tutorial on using `icepyx`, see:
#
# - https://icepyx.readthedocs.io/en/latest/example_notebooks/IS2_data_access.html
# - https://icepyx.readthedocs.io/en/latest/example_notebooks/IS2_data_read-in.html

# %% [markdown]
# ## 🧊 Load the grid data into an xarray.Dataset
#
# An [`xarray.Dataset`](https://docs.xarray.dev/en/v2022.03.0/generated/xarray.Dataset.html)
# is a data structure that puts labels on top of the dimensions.
#
# So, for a raster grid, there would be X and Y geographical dimensions.
#
# At each X and Y coodinate, there is a Z value.
# This Z value can be something like elevation or temperature.
#
# ```
#         Z-values in /z/
#         
#              --------------------
#             / 1 / 2 / 3 / 4 / 5 /
#            / 2 / 4 / 2 / 7 / 0 /
#           / 3 / 6 / 9 / 2 / 5 /  Y-dimension
#          / 4 / 5 / 1 / 8 / 1 /
#         / 5 / 0 / 2 / 4 / 3 /
#         --------------------
#             X-dimension
# ```

# %%
region_iceland.earthdata_login(
    uid="penguin123",  # EarthData username, e.g. penguin123
    email="penguin123@southpole.net",  # Email address, e.g. penguin123@southpole.net
)

# %%
region_iceland.download_granules(path=".")

# %%
# https://n5eil01u.ecs.nsidc.org/ATLAS/ATL14.001/2019.03.31/ATL14_IS_0311_100m_001_01.nc
ds_iceland: xr.Dataset = xr.open_dataset(
    "book/tutorials/DataVisualization/ATL14_IS_0311_100m_001_01.nc"
)
# ds_iceland.sel()
print(ds_iceland)


# %% [markdown]
# # 1️⃣ The raster basemap 🌈

# %%

# %% [markdown]
# # 2️⃣ The vector features 🚏


# %%

# %% [markdown]
# # 3️⃣ Saving the map 💾

# %%
