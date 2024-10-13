<!--<template>-->
<!--  <div-->
<!--      id="mapContainer"-->
<!--      class="mapContainer"-->
<!--  ></div>-->
<!--</template>-->

<!--<script setup lang="ts">-->
<!--import { ref, watch } from 'vue'-->
<!--import mapboxgl, { LngLatBounds, Map } from 'mapbox-gl'-->
<!--import axios from 'axios'-->
<!--import { useRoute } from 'vue-router'-->
<!--import type { Ref, ComputedRef } from 'vue'-->
<!--import type * as GeoJSON from 'geojson'-->
<!--import type { CoordinateTuple } from '~/lib/types/MapboxTypes'-->
<!--import { useGoogleApiStore } from '#imports'-->
<!--import type { GooglePlace } from '~/core/types/google-places'-->
<!--import { useSuggestionStore } from '~/stores/suggestion.store'-->
<!--import { useRoadtripStore } from '~/stores/roadtrip.store'-->

<!--/* PROPS */-->
<!--const props = defineProps({-->
<!--  isLoading: {-->
<!--    type: Boolean,-->
<!--    default: false,-->
<!--  },-->
<!--})-->

<!--/* STORES */-->
<!--const googleApiStore = useGoogleApiStore()-->
<!--const suggestionStore = useSuggestionStore()-->
<!--const roadtripStore = useRoadtripStore()-->

<!--/* HOOKS */-->
<!--const route = useRoute()-->

<!--/* REFS */-->
<!--const map: Ref<Map | null> = ref(null)-->
<!--const start: Ref<CoordinateTuple | null> = ref(null)-->
<!--const end: Ref<CoordinateTuple | null> = ref(null)-->

<!--/* CONSTANTS */-->
<!--const mapboxAccessToken: string =-->
<!--    'pk.eyJ1IjoiZmxvcmlhbnJvdXNzZWF1IiwiYSI6ImNsdHg0bGpjYzAzNnEyaXMxcDlvbnNzZHQifQ.N9vFw7kJyrfJuFgHF3tp0Q'-->

<!--/* COMPUTED */-->
<!--const sortedMarkers: ComputedRef<GeoJSON.Feature[]> = computed(() => {-->
<!--  const categoryOrder: { [key: number]: Array<[keyof typeof googleApiStore, string]> } = {-->
<!--    1: [-->
<!--      ['restaurants', 'restaurant'],-->
<!--      ['bars', 'bar'],-->
<!--      ['hotels', 'lodging'],-->
<!--      ['events', 'theatre'],-->
<!--    ],-->
<!--    2: [-->
<!--      ['bars', 'bar'],-->
<!--      ['restaurants', 'restaurant'],-->
<!--      ['hotels', 'lodging'],-->
<!--      ['events', 'theatre'],-->
<!--    ],-->
<!--    3: [-->
<!--      ['hotels', 'lodging'],-->
<!--      ['restaurants', 'restaurant'],-->
<!--      ['bars', 'bar'],-->
<!--      ['events', 'theatre'],-->
<!--    ],-->
<!--    4: [-->
<!--      ['events', 'theatre'],-->
<!--      ['restaurants', 'restaurant'],-->
<!--      ['bars', 'bar'],-->
<!--      ['hotels', 'lodging'],-->
<!--    ],-->
<!--  }-->

<!--  // Get the current order based on the active tab or default to the first tab order-->
<!--  const currentOrder = categoryOrder[suggestionStore.activeTabId] || categoryOrder[1]-->

<!--  // Flatten and generate place markers based on the current order-->
<!--  return currentOrder.flatMap(([storeKey, icon]) =>-->
<!--      generatePlaceMarkers(googleApiStore[storeKey] as GooglePlace[], icon),-->
<!--  )-->
<!--})-->

<!--/* METHODS */-->
<!--const parseCoordinates = (coordinates: string | undefined): CoordinateTuple | null => {-->
<!--  if (!coordinates) return null-->
<!--  const [latitude, longitude] = coordinates.split(',').map(Number)-->
<!--  return isNaN(latitude) || isNaN(longitude) ? null : [longitude, latitude]-->
<!--}-->

<!--const initializeMap = () => {-->
<!--  if (map.value || !start.value || !end.value) return-->
<!--  mapboxgl.accessToken = mapboxAccessToken-->
<!--  map.value = new Map({-->
<!--    container: 'mapContainer',-->
<!--    style: 'mapbox://styles/mapbox/streets-v12',-->
<!--    center: start.value,-->
<!--    zoom: 10,-->
<!--  })-->

<!--  map.value.on('load', async () => {-->
<!--    try {-->
<!--      await loadRoute()-->
<!--      loadStartEndMarkers()-->
<!--      loadPlacesMarkers()-->
<!--      map.value?.resize()-->
<!--      // Remove POI in the map-->
<!--      map.value?.removeLayer('poi-label')-->
<!--    } catch (error) {-->
<!--      console.error('Error initializing map:', error)-->
<!--    }-->
<!--  })-->
<!--}-->

<!--const loadRoute = async () => {-->
<!--  if (!start.value || !end.value) return-->
<!--  const directionsRequest = `https://api.mapbox.com/directions/v5/mapbox/driving-traffic/${start.value.join(',')};${end.value.join(',')}?geometries=geojson&overview=full&access_token=${mapboxAccessToken}`-->
<!--  const response = await axios.get(directionsRequest)-->
<!--  const routeData = response.data.routes[0].geometry-->

<!--  map.value?.addLayer({-->
<!--    id: 'route',-->
<!--    type: 'line',-->
<!--    source: {-->
<!--      type: 'geojson',-->
<!--      data: routeData,-->
<!--    },-->
<!--    layout: {-->
<!--      'line-join': 'round',-->
<!--      'line-cap': 'round',-->
<!--    },-->
<!--    paint: {-->
<!--      'line-color': '#0077B6',-->
<!--      'line-width': 5,-->
<!--      'line-opacity': 0.75,-->
<!--    },-->
<!--  })-->

<!--  const bounds = new LngLatBounds()-->
<!--  bounds.extend(start.value)-->
<!--  bounds.extend(end.value)-->
<!--  map.value?.fitBounds(bounds, {-->
<!--    padding: { top: 50, bottom: 50, left: 50, right: 50 },-->
<!--  })-->
<!--}-->

<!--// https://docs.mapbox.com/ios/search/api/core/1.0.0-beta.1/Enums/Maki.html#/s:12MapboxSearch4MakiO7lodgingyA2CmF-->
<!--const loadPlacesMarkers = () => {-->
<!--  const features: GeoJSON.FeatureCollection<GeoJSON.Geometry> = {-->
<!--    type: 'FeatureCollection',-->
<!--    features: sortedMarkers.value,-->
<!--  }-->

<!--  if (map.value) {-->
<!--    if (map.value.getSource('places')) {-->
<!--      map.value.removeLayer('places')-->
<!--      map.value.removeSource('places')-->
<!--    }-->

<!--    map.value.addSource('places', {-->
<!--      type: 'geojson',-->
<!--      data: features,-->
<!--    })-->

<!--    map.value.addLayer({-->
<!--      id: 'places',-->
<!--      type: 'symbol',-->
<!--      source: 'places',-->
<!--      layout: {-->
<!--        'icon-image': ['get', 'icon'],-->
<!--        'icon-size': 1.5,-->
<!--      },-->
<!--    })-->
<!--  }-->
<!--}-->

<!--const loadRoadtripMarkers = () => {-->
<!--  const features: GeoJSON.Feature<GeoJSON.Geometry, GeoJSON.GeoJsonProperties>[] = roadtripStore.steps.map((step) => ({-->
<!--    type: 'Feature',-->
<!--    geometry: {-->
<!--      type: 'Point',-->
<!--      coordinates: [step.location.longitude, step.location.latitude],-->
<!--    },-->
<!--    properties: {-->
<!--      icon: 'custom-marker',-->
<!--      title: step.name,-->
<!--    },-->
<!--  }))-->

<!--  const featureCollection: GeoJSON.FeatureCollection<GeoJSON.Geometry> = {-->
<!--    type: 'FeatureCollection',-->
<!--    features,-->
<!--  }-->

<!--  if (map.value) {-->
<!--    if (map.value.getSource('roadtrip')) {-->
<!--      // Met à jour les données existantes sans supprimer la source-->
<!--      ;(map.value.getSource('roadtrip') as mapboxgl.GeoJSONSource).setData(featureCollection)-->
<!--    } else {-->
<!--      // Crée la source et la couche si elles n'existent pas-->
<!--      map.value.addSource('roadtrip', {-->
<!--        type: 'geojson',-->
<!--        data: featureCollection,-->
<!--      })-->

<!--      map.value.addLayer({-->
<!--        id: 'roadtrip',-->
<!--        type: 'symbol',-->
<!--        source: 'roadtrip',-->
<!--        layout: {-->
<!--          'icon-image': 'custom-marker',-->
<!--          'icon-size': 0.8,-->
<!--          'text-field': '{title}',-->
<!--          'text-font': ['Open Sans Semibold', 'Arial Unicode MS Bold'],-->
<!--          'text-offset': [0, 1],-->
<!--          'text-size': 12,-->
<!--          'text-anchor': 'top',-->
<!--        },-->
<!--      })-->
<!--    }-->

<!--    // Ajoute ici le centrage sur le dernier step ajouté-->
<!--    if (roadtripStore.steps.length > 0) {-->
<!--      const lastStep = roadtripStore.steps[roadtripStore.steps.length - 1]-->
<!--      map.value.flyTo({-->
<!--        center: [lastStep.location.longitude, lastStep.location.latitude],-->
<!--        essential: true, // this ensures the animation will happen even if the user is interacting with the map-->
<!--        zoom: map.value.getZoom(), // conserve le niveau de zoom actuel-->
<!--      })-->
<!--    }-->
<!--  }-->
<!--}-->

<!--const loadStartEndMarkers = () => {-->
<!--  const features: GeoJSON.FeatureCollection<GeoJSON.Geometry> = {-->
<!--    type: 'FeatureCollection',-->
<!--    features: generateStartEndMarkers(),-->
<!--  }-->

<!--  map.value?.addSource('markers', {-->
<!--    type: 'geojson',-->
<!--    data: features,-->
<!--  })-->

<!--  const hasMarkerStartEndImage: boolean = map.value?.hasImage('custom-marker') || false-->

<!--  if (hasMarkerStartEndImage) {-->
<!--    map.value?.addLayer({-->
<!--      id: 'markers',-->
<!--      type: 'symbol',-->
<!--      source: 'markers',-->
<!--      layout: {-->
<!--        'icon-image': 'custom-marker',-->
<!--        'icon-size': 0.8,-->
<!--      },-->
<!--    })-->
<!--  } else {-->
<!--    map.value?.loadImage(-->
<!--        '/images/custom_marker.png',-->
<!--        function (error: Error | undefined, image: HTMLImageElement | ImageBitmap | undefined) {-->
<!--          if (error) throw error-->
<!--          if (!image) return-->
<!--          map.value?.addImage('custom-marker', image)-->
<!--          map.value?.addLayer({-->
<!--            id: 'markers',-->
<!--            type: 'symbol',-->
<!--            source: 'markers',-->
<!--            layout: {-->
<!--              'icon-image': 'custom-marker',-->
<!--              'icon-size': 0.8,-->
<!--              'text-field': '{title}',-->
<!--              'text-font': ['Open Sans Semibold', 'Arial Unicode MS Bold'],-->
<!--              'text-offset': [0, 0.6],-->
<!--              'text-anchor': 'top',-->
<!--            },-->
<!--          })-->
<!--        },-->
<!--    )-->
<!--  }-->
<!--}-->

<!--const generateStartEndMarkers = (): GeoJSON.Feature[] => {-->
<!--  if (!start.value || !end.value) return []-->
<!--  return [-->
<!--    {-->
<!--      type: 'Feature',-->
<!--      geometry: {-->
<!--        type: 'Point',-->
<!--        coordinates: start.value,-->
<!--      },-->
<!--      properties: {-->
<!--        'marker-symbol': 'harbor',-->
<!--      },-->
<!--    },-->
<!--    {-->
<!--      type: 'Feature',-->
<!--      geometry: {-->
<!--        type: 'Point',-->
<!--        coordinates: end.value,-->
<!--      },-->
<!--      properties: {-->
<!--        'marker-symbol': 'harbor',-->
<!--      },-->
<!--    },-->
<!--  ]-->
<!--}-->

<!--const generatePlaceMarkers = (data: GooglePlace[], icon: string): GeoJSON.Feature[] => {-->
<!--  console.log('generatePlaceMarkers', data, icon)-->
<!--  return data.map((item) => ({-->
<!--    type: 'Feature',-->
<!--    geometry: {-->
<!--      type: 'Point',-->
<!--      coordinates: [item.location.longitude, item.location.latitude],-->
<!--    },-->
<!--    properties: {-->
<!--      icon,-->
<!--      name: item.name,-->
<!--    },-->
<!--  }))-->
<!--}-->

<!--// RUN MAP-->
<!--start.value = parseCoordinates(route.query.start as string)-->
<!--end.value = parseCoordinates(route.query.end as string)-->

<!--const resetMarkers = () => {-->
<!--  // verify has layer and source-->
<!--  if (map.value?.getLayer('markers') && map.value?.getSource('markers')) {-->
<!--    map.value?.removeLayer('markers')-->
<!--  }-->
<!--  loadPlacesMarkers()-->

<!--  map.value?.addLayer({-->
<!--    id: 'markers',-->
<!--    type: 'symbol',-->
<!--    source: 'markers',-->
<!--    layout: {-->
<!--      'icon-image': 'custom-marker',-->
<!--      'icon-size': 0.8,-->
<!--    },-->
<!--  })-->
<!--}-->

<!--const updateRoute = async () => {-->
<!--  if (!start.value || !end.value) return-->

<!--  // Construire les coordonnées pour l'API de directions-->
<!--  const coordinates = [-->
<!--    start.value,-->
<!--    ...roadtripStore.steps.map((step) => [step.location.longitude, step.location.latitude]),-->
<!--    end.value,-->
<!--  ]-->

<!--  const directionsRequest = `https://api.mapbox.com/directions/v5/mapbox/driving/${coordinates.join(';')}?geometries=geojson&steps=true&access_token=${mapboxAccessToken}`-->

<!--  try {-->
<!--    const response = await axios.get(directionsRequest)-->
<!--    const data = response.data.routes[0].geometry-->

<!--    // Mettre à jour ou ajouter la couche de route si elle n'existe pas-->
<!--    if (map.value?.getLayer('route')) {-->
<!--      ;(map.value.getSource('route') as mapboxgl.GeoJSONSource).setData(data)-->
<!--    } else {-->
<!--      map.value?.addLayer({-->
<!--        id: 'route',-->
<!--        type: 'line',-->
<!--        source: {-->
<!--          type: 'geojson',-->
<!--          data,-->
<!--        },-->
<!--        layout: {-->
<!--          'line-join': 'round',-->
<!--          'line-cap': 'round',-->
<!--        },-->
<!--        paint: {-->
<!--          'line-color': '#0077B6',-->
<!--          'line-width': 5,-->
<!--          'line-opacity': 0.75,-->
<!--        },-->
<!--      })-->
<!--    }-->
<!--  } catch (error) {-->
<!--    console.error('Failed to update route:', error)-->
<!--  }-->
<!--}-->

<!--// When a place marker is clicked, add or remove to the roadtrip-->
<!--const setupPlaceMarkerClickEvents = () => {-->
<!--  if (map.value) {-->
<!--    map.value.on(-->
<!--        'click',-->
<!--        'places',-->
<!--        (-->
<!--            e: mapboxgl.MapMouseEvent & {-->
<!--              features?: mapboxgl.MapboxGeoJSONFeature[] | undefined-->
<!--            } & mapboxgl.EventData,-->
<!--        ) => {-->
<!--          // find the clicked place-->
<!--          const clickedPlace = e.features?.find((feature) => feature.layer.id === 'places')-->
<!--          if (clickedPlace) {-->
<!--            console.log('Clicked place:', clickedPlace)-->
<!--            const clickedPlaceName: string | undefined = clickedPlace.properties?.name-->
<!--            if (clickedPlaceName) {-->
<!--              const clickedPlace: GooglePlace | null = googleApiStore.findPlaceByName(clickedPlaceName)-->
<!--              if (clickedPlace) {-->
<!--                if (roadtripStore.isStepAdded(clickedPlace)) {-->
<!--                  roadtripStore.removeStep(clickedPlace)-->
<!--                } else {-->
<!--                  roadtripStore.addStep(clickedPlace)-->
<!--                }-->
<!--              } else {-->
<!--                console.error('Clicked place not found')-->
<!--              }-->
<!--            }-->
<!--          }-->
<!--        },-->
<!--    )-->
<!--  }-->
<!--}-->

<!--const setupRoadtripMarkerEvents = () => {-->
<!--  if (map.value) {-->
<!--    map.value.on(-->
<!--        'click',-->
<!--        'roadtrip',-->
<!--        (-->
<!--            e: mapboxgl.MapMouseEvent & {-->
<!--              features?: mapboxgl.MapboxGeoJSONFeature[] | undefined-->
<!--            } & mapboxgl.EventData,-->
<!--        ) => {-->
<!--          // find the clicked place-->
<!--          const clickedPlace = e.features?.find((feature) => feature.layer.id === 'roadtrip')-->
<!--          if (clickedPlace) {-->
<!--            console.log('Clicked roadtrip place:', clickedPlace)-->
<!--            const clickedPlaceName: string | undefined = clickedPlace.properties?.title-->
<!--            if (clickedPlaceName) {-->
<!--              const clickedPlace: GooglePlace | null = googleApiStore.findPlaceByName(clickedPlaceName)-->
<!--              if (clickedPlace) {-->
<!--                roadtripStore.removeStep(clickedPlace)-->
<!--              } else {-->
<!--                console.error('Clicked place not found')-->
<!--              }-->
<!--            }-->
<!--          }-->
<!--        },-->
<!--    )-->
<!--  }-->
<!--}-->

<!--const setupMarkerEvents = () => {-->
<!--  setupPlaceMarkerClickEvents()-->
<!--  setupRoadtripMarkerEvents()-->
<!--}-->

<!--/* LIFECYCLE */-->
<!--onMounted(() => {-->
<!--  if (!props.isLoading && start.value && end.value) {-->
<!--    initializeMap()-->
<!--    nextTick(() => {-->
<!--      map.value?.resize()-->
<!--      setupMarkerEvents()-->
<!--    })-->
<!--  }-->
<!--})-->

<!--/* WATCHERS */-->
<!--watch(-->
<!--    () => props.isLoading,-->
<!--    (isLoading) => {-->
<!--      if (!isLoading && start.value && end.value) {-->
<!--        initializeMap()-->
<!--        nextTick(() => {-->
<!--          map.value?.resize()-->
<!--          setupMarkerEvents()-->
<!--        })-->
<!--      }-->
<!--    },-->
<!--)-->

<!--watch(-->
<!--    () => suggestionStore.selectedCoordinates,-->
<!--    (newCoordinates) => {-->
<!--      if (newCoordinates && map.value) {-->
<!--        map.value.flyTo({-->
<!--          center: [newCoordinates.longitude, newCoordinates.latitude],-->
<!--          essential: true,-->
<!--          zoom: 17,-->
<!--        })-->
<!--      }-->
<!--    },-->
<!--    { immediate: true },-->
<!--)-->

<!--watch(-->
<!--    () => suggestionStore.activeTabId,-->
<!--    (activeTabId: number) => {-->
<!--      // verify if activeTabId is in [1, 2, 3, 4]-->
<!--      if (activeTabId >= 1 && activeTabId <= 4) {-->
<!--        resetMarkers()-->
<!--      }-->
<!--    },-->
<!--)-->

<!--watch(-->
<!--    () => suggestionStore.isRefreshing,-->
<!--    (isRefreshing) => {-->
<!--      if (!isRefreshing) {-->
<!--        console.log('REFRESH END - LOAD PLACES MARKERS')-->
<!--        resetMarkers()-->
<!--      }-->
<!--    },-->
<!--)-->

<!--watch(-->
<!--    () => roadtripStore.steps,-->
<!--    (newSteps) => {-->
<!--      console.log('ROADTRIP STEPS CHANGED', newSteps)-->
<!--      loadRoadtripMarkers()-->
<!--    },-->
<!--    { deep: true },-->
<!--)-->

<!--watch(-->
<!--    () => [roadtripStore.steps, start.value, end.value],-->
<!--    () => {-->
<!--      updateRoute()-->
<!--    },-->
<!--    { deep: true },-->
<!--)-->
<!--</script>-->

<!--<style>-->
<!--.mapContainer {-->
<!--  width: 100%;-->
<!--  height: 100%;-->
<!--  cursor: grab;-->
<!--}-->

<!--.mapboxgl-ctrl,-->
<!--.mapboxgl-ctrl-attrib {-->
<!--  display: none;-->
<!--}-->
<!--</style>-->
