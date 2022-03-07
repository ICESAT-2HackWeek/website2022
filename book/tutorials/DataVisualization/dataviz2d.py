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
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
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
# We'll start by loading some of these tools,
# that help us to process and visualize our data 📊.

# %%
# Install development versions
# # !pip install https://github.com/icesat2py/icepyx/archive/refs/heads/development.zip
# Note, need to restart jupyter kernel after installation for new version to show up

# %%
import icepyx as ipx  # for downloading and loading ICESat-2 data
import pygmt  # for making geographical maps and figures
import rioxarray  # for performing geospatial operations like reprojection
import xarray as xr  # for working with n-dimensional data

# %% [markdown]
# Just to make sure we're on the same page,
# let's check that we've got the same versions.

# %%
print(f"icepyx version: {ipx.__version__}")
pygmt.show_versions()

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

# %% [raw]
# region_iceland.avail_granules(ids=True, s3urls=True)
# region_iceland.earthdata_login(
#     uid="penguin123",  # EarthData username, e.g. penguin123
#     email="penguin123@southpole.net",  # e.g. penguin123@southpole.net
#     s3token=True,
# )

# %% [raw]
# region_iceland.download_granules(path=".")

# %%
# Load the NetCDF using xarray.open_dataset
# https://n5eil01u.ecs.nsidc.org/ATLAS/ATL14.001/2019.03.31/ATL14_IS_0311_100m_001_01.nc
ds: xr.Dataset = xr.open_dataset(filename_or_obj="ATL14_IS_0311_100m_001_01.nc")


# %% [markdown]
# The original ATL14 NetCDF data comes in a projected coordinate system called
# NSIDC Sea Ice Polar Stereographic North (EPSG:3413) 🧭.
#
# We'll reproject it to a geographic coordinate system (EPSG:4326) first,
# and that will give nice looking longitude and latitude 🌐 coordinates.

# %%
ds_3413 = ds.rio.write_crs(input_crs="EPSG:3413")  # set initial projection
ds_4326 = ds_3413.rio.reproject(dst_crs="EPSG:4326")  # reproject to WGS84
ds_iceland = ds_4326.sel(x=slice(-28.0, -10.0), y=slice(68.0, 62.0))  # spatial subset
ds_iceland

# %% [markdown]
# The 'ds_iceland' `xarray.Dataset` includes many data variables (Z-values)
# and attributes (metadata).
#
# Feel free to click on the dropdown icons 🔻📄🍔 to explore what's inside!

# %% [markdown]
# # 1️⃣ The raster basemap 🌈

# %% [markdown]
# ## Making the first figure! 🎬
#
# Colours are easier to visualize than numbers.
# Let's begin with just three lines of code 🤹
#
# We'll use PyGMT's [pygmt.Figure.grdimage](https://www.pygmt.org/v0.4.1/api/generated/pygmt.Figure.grdimage.html)
# to make this plot.

# %%
fig = pygmt.Figure()  # start a new instance of a blank Figure canvas
fig.grdimage(grid=ds_iceland["h"], frame=True)  # plot the height variable
fig.show()  # display the map as a jupyter notebook cell output

# %% [markdown]
# Already we're seeing 👀 some rainbow colors and a lot of gray.
#
# Let's add some axis labels and a title so people know what we're looking at 😉
#
# Previously we used `frame=True` to do this automatically,
# but let's customize it a bit more!

# %%
fig.grdimage(
    grid=ds_iceland["h"],
    frame=[
        'xaf+l"Longitude"',  # x-axis, (a)nnotate, (f)ine ticks, +(l)abel
        'yaf+l"Latitude"',  # y-axis, (a)nnotate, (f)ine ticks, +(l)abel
        '+t"ATL14 ice surface height over Iceland"',  # map title
    ],
)
fig.show()

# %% [markdown]
# Now we've got some x and y axis labels, and a plot title 🥳
#
# Still, it's hard to know what the map colors represent,
# so let's add ➕ some extra context.

# %% [markdown]
# ## Adding a colorbar 🍫
#
# A color scalebar helps us to link the colors on a map with some actual numbers 🔢
#
# Let's use [`pygmt.Figure.colorbar`](https://www.pygmt.org/v0.5.0/api/generated/pygmt.Figure.colorbar.html#pygmt.Figure.colorbar)
# to add this to our existing map 🔲

# %%
fig.colorbar()  # just plot the default color scalebar on the bottom
fig.show()

# %% [markdown]
# Now this isn't too bad, but we can definitely improve it more!
#
# Here are some ways to further customize the colorbar 📊:
# - **J**ustify the colorbar position to the **M**iddle **R**ight ➡️
# - Add a box representing NaN values using **+n** ◾
# - Add labels to the colorbar frame to say that this represents Elevation in metres 🇲
#
# 🔖 References:
# - https://www.pygmt.org/v0.5.0/gallery/embellishments/colorbar.html
# - https://www.pygmt.org/v0.5.0/tutorials/earth_relief.html

# %%
fig.colorbar(position="JMR+n", frame=["x+lElevation", "y+lm"])
fig.show()

# %% [markdown]
# Now we've got a map that makes more sense 😁
#
# Notice however, that there are two colorbars - our original horizontal 🚥 one
# and the new vertical 🚦 one.
#
# Recall back to what was said about 'layers' 🍰.
# Everytime you call `fig.something`,
# you will be 'drawing' on top of the existing canvas.
#
# ‼️ To start from a blank canvas 📄 again,
# make a new figure by calling `fig = pygmt.Figure()`‼️

# %% [markdown]
# ## Choosing a different colormap 🏳️‍🌈
#
# Do you have a favourite colourmap❓
#
# When making maps, we need to be mindful 😶‍🌫️ of how we represent data.
#
# Take some time ⏱️ to consider
# what is the most suitable type of colormap for this case.
#
# ![What type of colourmap to choose?](https://media.springernature.com/lw685/springer-static/image/art%3A10.1038%2Fs41467-020-19160-7/MediaObjects/41467_2020_19160_Fig6_HTML.png?as=webp)
#
# Done? Now let's use [`pygmt.makecpt`](https://www.pygmt.org/v0.5.0/api/generated/pygmt.makecpt.html)
# to change our map's color!!
#
# 🔖 References:
#
# - Crameri, F., Shephard, G.E. & Heron, P.J.
#   The misuse of colour in science communication. Nat Commun 11, 5444 (2020).
#   https://doi.org/10.1038/s41467-020-19160-7
# - List of built-in GMT color palette tables:
#   https://docs.generic-mapping-tools.org/6.3/cookbook/cpts.html#id3

# %%
fig = pygmt.Figure()  # start a new blank figure!

pygmt.makecpt(
    cmap="",  # insert your colormap's name here
    series=[-200, 2500],  # min an max values to stretch the colormap
)

fig.grdimage(
    grid=ds_iceland["h"],  # plot the xarray.Dataset's height variable
    cmap=True,  # setting this as True tells pygmt to use the colormap from makecpt
    frame=True,  # have automatic map frames
)

fig.show()

# %% [markdown]
# Once again, we'll add a colorbar on the right for completeness 🎓

# %%
fig.colorbar(position="JMR+n", frame=["x+lElevation", "y+lm"])
fig.show()

# %% [markdown]
# ## (Optional) Advanced basemap customization 😎
#
# If you have time, try playing 🛝 with the [`pygmt.Figure.basemap`](https://www.pygmt.org/v0.5.0/api/generated/pygmt.Figure.basemap.html)
# method to customize your map even more.
#
# Do so by calling `fig.basemap()`, which has options to do things like:
# - Adding graticules/gridlines using `frame="g"` 🌐
# - Adding a North arrow (compass rose) using `rose="jTR+w2c"` 🔝
# - Adding a kilometer scalebar using something like `map_scale="jBR+w5k+o1"` 📏
#
# 🔖 References:
# - https://www.pygmt.org/v0.5.0/tutorials/frames.html
# - https://www.pygmt.org/v0.5.0/api/generated/pygmt.Figure.basemap.html#examples-using-pygmt-figure-basemap

# %%
# Code block to play with
fig = pygmt.Figure()  # start a new figure

fig.grdimage(grid=ds_iceland["h"], cmap="oleron")  # plot grid as a background

# Customize your basemap here!!
fig.basemap(
    frame="afg",
    # Add more options here!!
)

fig.show()  # show the map

# %% [markdown]
# # 2️⃣ The vector features 🚏


# %%

# %% [markdown]
# # 3️⃣ Saving the map 💾

# %%
