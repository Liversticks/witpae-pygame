# Map creation

## Data sources
- [Natural Earth](https://www.naturalearthdata.com/downloads/). Contains 1:10m, 1:50m, and 1:110m data sets
- [Copernicus GLO-30 DEM](https://portal.opentopography.org/raster?opentopoID=OTSDEM.032021.4326.3)

## Generating azimuthal equidistant projection

Example centered on 15 N, 165 W
```
+proj=aeqd +lat_0=15 +lon_0=165 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs
```

## Clipping raster
1. Download and import subsection raster
2. Generate the vector polygon used to clip:
  1. Select the desired area to clip
  2. If the polygon is multipart, convert it to singlepart (**Vector > Geometry Tools > Multipart to Singleparts**)
3. Clip raster by mask layer
  1. Use the polygon generated in step 2 to clip
  2. Assign NoData to -9999 so the water becomes transparent
  3. Disk size error occurs if the layer was not selected properly
4. For the new layer:
  1. Symbology > Change render type to **Hillshade**
  2. Altitude 45 degrees, azimuth 315 degrees, z factor 1
  3. Change blending mode to **Multiply**
  4. Change brightness to 150