import { useEffect, useRef, useState } from 'react'
import { Map, NavigationControl } from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import './App.css'

const STYLE = 'https://tiles.openfreemap.org/styles/liberty'
const COUNTRIES = '/geo/countries.geojson'
const STATES = '/geo/states.geojson'
const CITIES = '/geo/cities.geojson'

const WIKI_ALIAS = {
  'United States of America': 'United States',
  'Russian Federation': 'Russia',
  Czechia: 'Czech Republic',
  'Republic of Korea': 'South Korea',
  "Democratic People's Republic of Korea": 'North Korea',
  'Bosnia and Herz.': 'Bosnia and Herzegovina',
  'Central African Rep.': 'Central African Republic',
  'S. Sudan': 'South Sudan',
  'Eq. Guinea': 'Equatorial Guinea',
  'Dem. Rep. Congo': 'Democratic Republic of the Congo',
  'Dominican Rep.': 'Dominican Republic',
}

function wikiTitle(name) {
  return WIKI_ALIAS[name] || name
}

function placeName(props = {}) {
  return (
    props.NAME ||
    props.name ||
    props.NAME_EN ||
    props.ADMIN ||
    props.admin ||
    props.NAMEASCII ||
    props.nameascii ||
    ''
  )
}

function featureBbox(feature) {
  const coords = []
  const walk = (c) => {
    if (typeof c[0] === 'number') coords.push(c)
    else c.forEach(walk)
  }
  walk(feature.geometry.coordinates)
  let minX = 180
  let minY = 90
  let maxX = -180
  let maxY = -90
  for (const [x, y] of coords) {
    minX = Math.min(minX, x)
    maxX = Math.max(maxX, x)
    minY = Math.min(minY, y)
    maxY = Math.max(maxY, y)
  }
  return [
    [minX, minY],
    [maxX, maxY],
  ]
}

function pointInRing(lng, lat, ring) {
  let inside = false
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const xi = ring[i][0]
    const yi = ring[i][1]
    const xj = ring[j][0]
    const yj = ring[j][1]
    const intersect = yi > lat !== yj > lat && lng < ((xj - xi) * (lat - yi)) / (yj - yi || 1e-12) + xi
    if (intersect) inside = !inside
  }
  return inside
}

function pointInPolygonFeature(lng, lat, feature) {
  const g = feature.geometry
  const polys = g?.type === 'Polygon' ? [g.coordinates] : g?.type === 'MultiPolygon' ? g.coordinates : []
  return polys.some(
    (poly) => pointInRing(lng, lat, poly[0]) && !poly.slice(1).some((hole) => pointInRing(lng, lat, hole)),
  )
}

function withIds(collection) {
  collection.features.forEach((f, i) => {
    f.id = i
  })
  return collection
}

function overlayBeforeId(map) {
  const layers = map.getStyle().layers || []
  const road = layers.find((l) => /^(tunnel_|road_|bridge_)/.test(l.id))
  if (road) return road.id
  return layers.find((l) => l.type === 'symbol')?.id
}

function applyAtmosphere(map) {
  try {
    map.setSky({
      'sky-color': '#02040a',
      'horizon-color': '#3a6cb0',
      'fog-color': '#07101c',
      'fog-ground-blend': 0.55,
      'horizon-fog-blend': 0.8,
      'sky-horizon-blend': 0.85,
      'atmosphere-blend': ['interpolate', ['linear'], ['zoom'], 0, 0.9, 3, 0.75, 5, 0.25, 7, 0],
    })
  } catch {
    /* sky optional */
  }
}

function restyleBase(map) {
  try {
    map.setPaintProperty('background', 'background-color', '#0b1220')
  } catch {
    /* ignore */
  }
  try {
    map.setPaintProperty('water', 'fill-color', '#071422')
  } catch {
    /* ignore */
  }
  try {
    map.setPaintProperty('natural_earth', 'raster-opacity', [
      'interpolate',
      ['linear'],
      ['zoom'],
      0,
      0.42,
      6,
      0.12,
    ])
  } catch {
    /* ignore */
  }
}

function addFill(map, id, source, minzoom, maxzoom, beforeId) {
  map.addLayer(
    {
      id,
      type: 'fill',
      source,
      minzoom,
      maxzoom,
      paint: {
        'fill-color': [
          'case',
          ['boolean', ['feature-state', 'selected'], false],
          '#7cd2ff',
          '#1a5aa0',
        ],
        'fill-opacity': [
          'case',
          ['boolean', ['feature-state', 'selected'], false],
          0.2,
          0.04,
        ],
      },
    },
    beforeId,
  )
  map.addLayer(
    {
      id: `${id}-line`,
      type: 'line',
      source,
      minzoom,
      maxzoom,
      paint: {
        'line-color': [
          'case',
          ['boolean', ['feature-state', 'selected'], false],
          '#b9f0ff',
          'rgba(180, 220, 255, 0.22)',
        ],
        'line-width': [
          'case',
          ['boolean', ['feature-state', 'selected'], false],
          1.8,
          0.6,
        ],
        'line-blur': [
          'case',
          ['boolean', ['feature-state', 'selected'], false],
          0.4,
          0,
        ],
        'line-opacity': [
          'case',
          ['boolean', ['feature-state', 'selected'], false],
          0.95,
          0.7,
        ],
      },
    },
    beforeId,
  )
  map.addLayer(
    {
      id: `${id}-glow`,
      type: 'line',
      source,
      minzoom,
      maxzoom,
      paint: {
        'line-color': '#7cd2ff',
        'line-width': 6,
        'line-blur': 4.5,
        'line-opacity': ['case', ['boolean', ['feature-state', 'selected'], false], 0.55, 0],
      },
    },
    beforeId,
  )
}

export default function App() {
  const hostRef = useRef(null)
  const mapRef = useRef(null)
  const spinningRef = useRef(true)
  const selectedRef = useRef(null)
  const pickedRef = useRef(null)
  const [spinning, setSpinning] = useState(true)
  const [picked, setPicked] = useState(null)
  const [wiki, setWiki] = useState({ status: 'idle', extract: '', url: '' })

  const stopSpin = () => {
    spinningRef.current = false
    setSpinning(false)
  }

  const startSpin = () => {
    spinningRef.current = true
    setSpinning(true)
  }

  useEffect(() => {
    if (!picked) {
      setWiki({ status: 'idle', extract: '', url: '' })
      return
    }
    const title = wikiTitle(picked)
    let cancelled = false
    setWiki({ status: 'loading', extract: '', url: '' })
    fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(title)}`)
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((j) => {
        if (cancelled) return
        setWiki({
          status: 'ok',
          extract: j.extract || '',
          url: j.content_urls?.desktop?.page || '',
        })
      })
      .catch(() => {
        if (!cancelled) setWiki({ status: 'none', extract: '', url: '' })
      })
    return () => {
      cancelled = true
    }
  }, [picked])

  useEffect(() => {
    const map = new Map({
      container: hostRef.current,
      style: STYLE,
      center: [10, 18],
      zoom: 1.55,
      minZoom: 0.8,
      maxZoom: 18,
      clickTolerance: 16,
      canvasContextAttributes: { antialias: true },
    })
    mapRef.current = map
    map.addControl(new NavigationControl({ visualizePitch: true }), 'bottom-right')

    let idleTimer = 0
    const bumpIdle = () => {
      spinningRef.current = false
      setSpinning(false)
      window.clearTimeout(idleTimer)
      idleTimer = window.setTimeout(() => {
        const z = mapRef.current?.getZoom?.() ?? 0
        if (!pickedRef.current && z < 2.7) {
          spinningRef.current = true
          setSpinning(true)
        }
      }, 7000)
    }
    map.on('mousedown', bumpIdle)
    map.on('touchstart', bumpIdle)
    map.on('wheel', bumpIdle)
    map.on('zoom', () => {
      const z = map.getZoom() ?? 0
      if (z >= 2.8) {
        spinningRef.current = false
        setSpinning(false)
      }
    })

    let raf = 0
    const spin = () => {
      if (spinningRef.current && mapRef.current) {
        const c = map.getCenter()
        map.setCenter([c.lng + 0.025, c.lat])
      }
      raf = requestAnimationFrame(spin)
    }
    raf = requestAnimationFrame(spin)

    const clearSelected = () => {
      const prev = selectedRef.current
      if (prev) {
        try {
          map.setFeatureState(prev, { selected: false })
        } catch {
          /* source may be gone */
        }
      }
      selectedRef.current = null
    }

    const collections = { countries: null, states: null, cities: null }
    const geoReady = Promise.all([
      fetch(COUNTRIES).then((r) => r.json()).then(withIds),
      fetch(STATES).then((r) => r.json()).then(withIds),
      fetch(CITIES).then((r) => r.json()).then(withIds),
    ]).then(([countries, states, cities]) => {
      collections.countries = countries
      collections.states = states
      collections.cities = cities
      return collections
    })

    const pick = (feature, maxZoom, sourceId) => {
      const name = placeName(feature.properties)
      if (!name) return
      pickedRef.current = name
      stopSpin()
      clearSelected()
      if (sourceId != null && feature.id != null) {
        const key = { source: sourceId, id: feature.id }
        selectedRef.current = key
        try {
          map.setFeatureState(key, { selected: true })
        } catch {
          /* ignore */
        }
      }
      setPicked(name)
      if (feature.geometry.type === 'Point') {
        map.flyTo({
          center: feature.geometry.coordinates,
          zoom: maxZoom,
          duration: 1100,
        })
        return
      }
      try {
        map.fitBounds(featureBbox(feature), {
          padding: 56,
          duration: 1100,
          maxZoom,
        })
      } catch {
        map.flyTo({ center: map.getCenter(), zoom: maxZoom, duration: 1100 })
      }
    }

    map.on('style.load', () => {
      map.setProjection({ type: 'globe' })
      applyAtmosphere(map)
      restyleBase(map)
      const beforeId = overlayBeforeId(map)
      geoReady.then(({ countries, states, cities }) => {
        if (!map.getSource('countries')) {
          map.addSource('countries', { type: 'geojson', data: countries })
          map.addSource('states', { type: 'geojson', data: states })
          map.addSource('cities', { type: 'geojson', data: cities })
        }
        if (!map.getLayer('countries-fill')) {
          addFill(map, 'countries-fill', 'countries', 0, 4.2, beforeId)
          addFill(map, 'states-fill', 'states', 3.2, 6.2, beforeId)
          map.addLayer(
            {
              id: 'cities-circle',
              type: 'circle',
              source: 'cities',
              minzoom: 4.2,
              maxzoom: 12,
              paint: {
                'circle-radius': ['interpolate', ['linear'], ['zoom'], 4, 3, 10, 5],
                'circle-color': [
                  'case',
                  ['boolean', ['feature-state', 'selected'], false],
                  '#e8f9ff',
                  '#7cd2ff',
                ],
                'circle-stroke-color': '#041018',
                'circle-stroke-width': 1,
                'circle-opacity': 0.9,
                'circle-blur': ['case', ['boolean', ['feature-state', 'selected'], false], 0.35, 0],
              },
            },
            beforeId,
          )
        }
      })
    })

    map.on('click', (e) => {
      const { lng, lat } = e.lngLat
      const z = map.getZoom()
      if (z >= 4.2 && collections.cities?.features) {
        const pt = e.point
        let best = null
        let bestD = 18
        for (const f of collections.cities.features) {
          if (f.geometry?.type !== 'Point') continue
          const p = map.project(f.geometry.coordinates)
          const d = Math.hypot(p.x - pt.x, p.y - pt.y)
          if (d < bestD) {
            bestD = d
            best = f
          }
        }
        if (best) {
          pick(best, 15, 'cities')
          return
        }
      }
      if (z >= 3.2 && collections.states?.features) {
        const st = collections.states.features.find((f) => pointInPolygonFeature(lng, lat, f))
        if (st) {
          pick(st, 8, 'states')
          return
        }
      }
      const country = collections.countries?.features.find((f) =>
        pointInPolygonFeature(lng, lat, f),
      )
      if (country) pick(country, 5.2, 'countries')
    })

    return () => {
      window.clearTimeout(idleTimer)
      cancelAnimationFrame(raf)
      map.remove()
      mapRef.current = null
    }
  }, [])

  return (
    <div className="shell">
      <div ref={hostRef} className="map" />
      <div className="hud">
        <div className="brand">
          <strong>Live Globe</strong>
          <span>OpenFreeMap streets · tap country / state / city</span>
        </div>
        <div className="row">
          <button type="button" onClick={() => (spinning ? stopSpin() : startSpin())}>
            {spinning ? 'Stop spin' : 'Spin'}
          </button>
          {picked ? (
            <button
              type="button"
              onClick={() => {
                const map = mapRef.current
                const prev = selectedRef.current
                if (map && prev) {
                  try {
                    map.setFeatureState(prev, { selected: false })
                  } catch {
                    /* ignore */
                  }
                }
                setPicked(null)
                pickedRef.current = null
                selectedRef.current = null
                map?.flyTo({ center: [10, 18], zoom: 1.55, duration: 1000 })
                spinningRef.current = true
                setSpinning(true)
              }}
            >
              Back out
            </button>
          ) : null}
        </div>
      </div>
      {picked ? (
        <aside className="panel">
          <h1>{picked}</h1>
          <p className="meta">Latest available (Wikipedia) · not live news</p>
          {wiki.status === 'loading' ? <p>Loading…</p> : null}
          {wiki.status === 'ok' ? <p>{wiki.extract}</p> : null}
          {wiki.status === 'none' ? <p>No summary for this name.</p> : null}
          {wiki.url ? (
            <a href={wiki.url} target="_blank" rel="noreferrer">
              Wikipedia
            </a>
          ) : null}
        </aside>
      ) : (
        <p className="hint">
          Tap a country, then keep zooming — streets and city labels come from OpenFreeMap vector tiles. Idle spin resumes if nothing is picked.
        </p>
      )}
    </div>
  )
}
