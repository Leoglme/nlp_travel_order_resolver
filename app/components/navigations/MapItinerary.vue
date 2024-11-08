<template>
  <div v-if="isClient" ref="mapContainer" class="map"></div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { defineProps } from 'vue'

// Définir les types pour les props
export type RoutePoint = {
  id: string
  name: string
  latitude: number
  longitude: number
  travel_time: number
  stop_name: string
}

export type FindRouteResponse = {
  departure: string
  destination: string
  route: RoutePoint[]
  total_travel_time: number
}

// Définir les props
const props = defineProps<{ data: FindRouteResponse }>()

// Assurez-vous que le composant est rendu uniquement côté client
const isClient = computed(() => process.client)
const mapContainer = ref<HTMLDivElement | null>(null)

onMounted(async () => {
  if (isClient.value && mapContainer.value) {
    // Import Leaflet uniquement côté client
    const L = await import('leaflet')
    await import('leaflet/dist/leaflet.css')

    // Initialiser la carte centrée sur le premier point de l'itinéraire
    const startPoint = props.data.route[0]
    const map = L.map(mapContainer.value).setView([startPoint.latitude, startPoint.longitude], 10)

    // Ajouter la couche de tuiles OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map)

    // Initialiser un tableau pour les coordonnées de chaque point de la route
    const routeCoordinates = props.data.route.map(point => [point.latitude, point.longitude])

    // Ajouter un marqueur pour chaque point de la route
    props.data.route.forEach(point => {
      const marker = L.marker([point.latitude, point.longitude]).addTo(map)
      marker.bindPopup(`<b>${point.stop_name}</b><br>${point.name}<br>Temps de voyage: ${point.travel_time} minutes`)
    })

    // Tracer une ligne entre les points pour représenter l'itinéraire
    L.polyline(routeCoordinates, { color: 'blue' }).addTo(map)

    // Adapter la vue de la carte pour inclure l'ensemble de l'itinéraire
    map.fitBounds(routeCoordinates)
  }
})
</script>

<style scoped>
.map {
  width: 100%;
  height: 100%;
}
</style>
