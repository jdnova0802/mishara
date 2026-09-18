# Live Globe (toy)

Not a company. Not Nisaba. Not a SKU.

MapLibre GL JS with `setProjection({ type: 'globe' })` and OpenFreeMap **liberty** vector tiles (`https://tiles.openfreemap.org/styles/liberty`). Streets, place labels, and finer geography come from those tiles as you zoom. Country/state/city GeoJSON is a click overlay under the road layers, not the base texture.

Dark page, atmosphere ring, idle spin, selected-region glow.

```bash
cd globe
npm install
npm run dev
```
