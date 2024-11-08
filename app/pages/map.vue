<template>
  <div class="relative grid md:grid-cols-[500px_minmax(0,1fr)] h-full md:h-[calc(100vh-72px)] overflow-y-auto py-4 gap-4 px-4 bg-[#FEF2E5]">
    <div
        v-if="mapIsLoading"
        class="absolute inset-0 z-20 flex items-center justify-center"
    >
      <i class="animate-spin text-4xl text-secondary-700 fas fa-spinner"></i>
    </div>

    <TimelineItinerary
        v-if="routeResponse"
        :routeResponse="routeResponse"
    />

    <!-- Map Div -->
    <div
        v-show="!mapIsLoading"
        class="inset-0 relative w-full h-full"
    >
      <MapItinerary
          v-if="routeResponse"
          :data="routeResponse"
      />
    </div>
  </div>
</template>

<script lang="ts" setup>
import type { Ref } from 'vue'
import TravelOrderResolverService from "~/core/services/TravelOrderResolverService";
import type { FindRouteResponse, RoutePoint } from "~/core/services/TravelOrderResolverService";
import type { ErrorResponse } from "~/core/types/response";
import NotyfService from "~/lib/services/NotyfService";
import MapItinerary from "~/components/navigations/MapItinerary.vue";
import TimelineItinerary from "~/components/navigations/TimelineItinerary.vue";

function formatTime(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return `${hours}h ${remainingMinutes}m`;
}

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
const routeResponse: Ref<FindRouteResponse | null> = ref(null)


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
  routeResponse.value = findRouteResponse

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
