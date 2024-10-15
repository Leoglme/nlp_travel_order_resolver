<template>
  <div class="relative md:grid md:grid-cols-[500px,1fr] h-[calc(100vh-72px)]">
    <div
        v-if="mapIsLoading"
        class="absolute inset-0 z-20 flex items-center justify-center"
    >
      <i class="animate-spin text-4xl text-secondary-700 fas fa-spinner"></i>
    </div>

    <!-- Map Div -->
    <div
        v-show="!mapIsLoading"
        class="absolute inset-0 md:relative"
    >
      departure: {{ departure }}
      <br>
      destination: {{ destination }}
      <br>
      routePoints: {{ routePoints }}
    </div>
  </div>
</template>

<script lang="ts" setup>
import type { Ref } from 'vue'
import TravelOrderResolverService from "~/core/services/TravelOrderResolverService";
import type { FindRouteResponse, RoutePoint } from "~/core/services/TravelOrderResolverService";
import type {ErrorResponse} from "~/core/types/response";
import NotyfService from "~/lib/services/NotyfService";

/* METAS */
useHead({
  title: 'Carte de votre trajet',
})

/* HOOKS */
const route = useRoute()

/* REFS */
const mapIsLoading: Ref<boolean> = ref(true)
const travelSentence: Ref<string> = ref(route.query.q?.toString() || '')
const departure: Ref<string> = ref('')
const destination: Ref<string> = ref('')
const routePoints: Ref<RoutePoint[]> = ref([])


/* WATCHERS */
watch(
    () => route.query,
    async (query: Record<string, any>) => {
      travelSentence.value = query.q ? query.q.toString() : ''
      await findRoute()
    }
)

/* METHODS */
const findRoute = async () => {
  mapIsLoading.value = true
  const findRouteResponse: FindRouteResponse | ErrorResponse = await TravelOrderResolverService.findRoute(travelSentence.value)

  if ('detail' in findRouteResponse) {
    const notyfService = new NotyfService()
    return notyfService.error(findRouteResponse.detail)
  }

  departure.value = findRouteResponse.departure
  destination.value = findRouteResponse.destination
  routePoints.value = findRouteResponse.route


  mapIsLoading.value = false
}

/* LIFECYCLE */
onMounted(async () => {
  await findRoute()
})
</script>
