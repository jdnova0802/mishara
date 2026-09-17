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

function addFill(map, id, source, minzoom, maxzoom) {
  map.addLayer({
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
        0.45,
        0.22,
      ],
    },
  })
  map.addLayer({
    id: `${id}-line`,
    type: 'line',
    source,
    minzoom,
    maxzoom,
    paint: {
      'line-color': 'rgba(180, 220, 255, 0.55)',
      'line-width': 0.8,
    },
  })
}

export default function App() {
  const hostRef = useRef(null)
  const mapRef = useRef(null)
  const spinningRef = useRef(false)
  const selectedRef = useRef(null)
  const [spinning, setSpinning] = useState(false)
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
      zoom: 1.6,
      clickTolerance: 16,
      canvasContextAttributes: { antialias: true },
    })
    mapRef.current = map
    map.addControl(new NavigationControl({ visualizePitch: true }), 'bottom-right')

    const stopOnTouch = () => stopSpin()
    map.on('mousedown', stopOnTouch)
    map.on('touchstart', stopOnTouch)
    map.on('wheel', stopOnTouch)
    map.on('dragstart', stopOnTouch)

    let raf = 0
    const spin = () => {
      if (spinningRef.current && mapRef.current) {
        const c = map.getCenter()
        map.setCenter([c.lng + 0.08, c.lat])
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
    Promise.all([
      fetch(COUNTRIES).then((r) => r.json()),
      fetch(STATES).then((r) => r.json()),
      fetch(CITIES).then((r) => r.json()),
    ]).then(([countries, states, cities]) => {
      collections.countries = countries
      collections.states = states
      collections.cities = cities
    })

    const pick = (feature, maxZoom, sourceId) => {
      const name = placeName(feature.properties)
      if (!name) return
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
      map.addSource('countries', { type: 'geojson', data: COUNTRIES, generateId: true })
      map.addSource('states', { type: 'geojson', data: STATES, generateId: true })
      map.addSource('cities', { type: 'geojson', data: CITIES, generateId: true })
      addFill(map, 'countries-fill', 'countries', 0, 4.5)
      addFill(map, 'states-fill', 'states', 3.2, 8.5)
      map.addLayer({
        id: 'cities-circle',
        type: 'circle',
        source: 'cities',
        minzoom: 4.2,
        paint: {
          'circle-radius': ['interpolate', ['linear'], ['zoom'], 4, 3, 8, 7],
          'circle-color': '#7cd2ff',
          'circle-stroke-color': '#041018',
          'circle-stroke-width': 1,
        },
      })
      map.addLayer({
        id: 'cities-label',
        type: 'symbol',
        source: 'cities',
        minzoom: 5,
        layout: {
          'text-field': ['coalesce', ['get', 'NAME'], ['get', 'name']],
          'text-size': 12,
          'text-offset': [0, 1],
        },
        paint: {
          'text-color': '#e8eef7',
          'text-halo-color': '#041018',
          'text-halo-width': 1.2,
        },
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
          pick(best, 9, 'cities')
          return
        }
      }
      if (z >= 3.2 && collections.states?.features) {
        const st = collections.states.features.find((f) => pointInPolygonFeature(lng, lat, f))
        if (st) {
          pick(st, 6.2, 'states')
          return
        }
      }
      const country = collections.countries?.features.find((f) =>
        pointInPolygonFeature(lng, lat, f),
      )
      if (country) pick(country, 4.2, 'countries')
    })

    return () => {
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
          <span>MapLibre globe · tap country / state / city</span>
        </div>
        <div className="row">
          <button type="button" onClick={() => (spinning ? stopSpin() : startSpin())}>
            {spinning ? 'Stop spin' : 'Spin'}
          </button>
          {picked ? (
            <button
              type="button"
              onClick={() => {
                setPicked(null)
                selectedRef.current = null
                mapRef.current?.flyTo({ center: [10, 18], zoom: 1.6, duration: 1000 })
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
          Tap a country. Keep zooming — US states then cities show up. Spin is a button. Globe morphs to a map as you go in.
        </p>
      )}
    </div>
  )
}
