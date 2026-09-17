import { useCallback, useEffect, useRef, useState } from 'react'
import Globe from 'react-globe.gl'
import { feature } from 'topojson-client'
import { geoCentroid } from 'd3-geo'
import countries110 from 'world-atlas/countries-110m.json'
import './App.css'

const COUNTRIES = feature(countries110, countries110.objects.countries).features

const WIKI_ALIAS = {
  'United States of America': 'United States',
  'Russian Federation': 'Russia',
  'Czechia': 'Czech Republic',
  'Republic of Korea': 'South Korea',
  "Democratic People's Republic of Korea": 'North Korea',
  'Bosnia and Herz.': 'Bosnia and Herzegovina',
  'Central African Rep.': 'Central African Republic',
  'S. Sudan': 'South Sudan',
  'Eq. Guinea': 'Equatorial Guinea',
  'Dem. Rep. Congo': 'Democratic Republic of the Congo',
  'Congo': 'Republic of the Congo',
  'Dominican Rep.': 'Dominican Republic',
  'Falkland Is.': 'Falkland Islands',
  'Solomon Is.': 'Solomon Islands',
  'W. Sahara': 'Western Sahara',
}

function wikiTitle(name) {
  return WIKI_ALIAS[name] || name
}

export default function App() {
  const globeRef = useRef(null)
  const [spinning, setSpinning] = useState(true)
  const [size, setSize] = useState(() => ({
    w: window.innerWidth,
    h: window.innerHeight,
  }))
  const [picked, setPicked] = useState(null)
  const [wiki, setWiki] = useState({ status: 'idle', extract: '', url: '' })
  const [hover, setHover] = useState(null)

  const setRotate = useCallback((on) => {
    const controls = globeRef.current?.controls?.()
    if (controls) {
      controls.autoRotate = on
      controls.autoRotateSpeed = 0.45
    }
    setSpinning(on)
  }, [])

  useEffect(() => {
    const onResize = () => setSize({ w: window.innerWidth, h: window.innerHeight })
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  }, [])

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

  const onReady = useCallback(() => {
    const g = globeRef.current
    if (!g) return
    const controls = g.controls()
    controls.autoRotate = true
    controls.autoRotateSpeed = 0.45
    controls.enableZoom = true
    controls.enableRotate = true
    controls.enablePan = false
    controls.minDistance = 90
    controls.maxDistance = 800
    controls.addEventListener('start', () => {
      controls.autoRotate = false
      setSpinning(false)
    })
    g.pointOfView({ lat: 18, lng: 10, altitude: 2.4 }, 0)
  }, [])

  const flyTo = useCallback(
    (feat) => {
      const name = feat?.properties?.name
      if (!name) return
      const [lng, lat] = geoCentroid(feat)
      setRotate(false)
      setPicked(name)
      globeRef.current?.pointOfView({ lat, lng, altitude: 1.25 }, 1100)
    },
    [setRotate],
  )

  return (
    <div className="shell">
      <Globe
        ref={globeRef}
        width={size.w}
        height={size.h}
        backgroundColor="#05070c"
        globeImageUrl="/earth-blue-marble.jpg"
        bumpImageUrl="/earth-topology.png"
        backgroundImageUrl="/night-sky.png"
        polygonsData={COUNTRIES}
        polygonCapColor={(d) =>
          d === hover || d?.properties?.name === picked
            ? 'rgba(120, 210, 255, 0.45)'
            : 'rgba(20, 90, 160, 0.18)'
        }
        polygonSideColor={() => 'rgba(8, 30, 60, 0.4)'}
        polygonStrokeColor={() => 'rgba(180, 220, 255, 0.35)'}
        polygonLabel={(d) => `<div class="tip">${d.properties.name}</div>`}
        polygonsTransitionDuration={180}
        onPolygonHover={setHover}
        onPolygonClick={flyTo}
        onGlobeReady={onReady}
        animateIn={false}
      />

      <div className="hud">
        <div className="brand">
          <strong>Live Globe</strong>
          <span>toy · tap a country · scroll to zoom</span>
        </div>
        <div className="row">
          <button type="button" onClick={() => setRotate(!spinning)}>
            {spinning ? 'Stop spin' : 'Spin'}
          </button>
          {picked ? (
            <button
              type="button"
              onClick={() => {
                setPicked(null)
                globeRef.current?.pointOfView({ lat: 18, lng: 10, altitude: 2.4 }, 1000)
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
        <p className="hint">Tap a country. Drag to look. Pinch/scroll to zoom in 3D. Spin stops when you touch it.</p>
      )}
    </div>
  )
}
