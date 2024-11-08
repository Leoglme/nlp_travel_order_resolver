<template>
  <div class="bg-white rounded-lg shadow-lg w-full mx-auto overflow-y-auto">
    <!-- Header Section -->
    <div class="flex justify-between items-center border-b py-4 sticky top-0 px-6 z-10 bg-white">
      <h2 class="text-lg font-semibold">{{ routeResponse.departure }} → {{ routeResponse.destination }}</h2>
      <p class="text-gray-500">
        Durée totale :
        <span
            class="font-semibold text-gray-600"
        >
          {{ minutesToHoursStr(routeResponse.total_travel_time) }}
        </span>
      </p>
    </div>

    <!-- Itinerary Stops -->
    <div class="p-6">
      <div class="relative pl-1.5">
        <!-- Vertical Line for the Timeline -->
        <div class="absolute top-0 bottom-0 left-[11px] w-px bg-gray-300"></div>

        <!-- Each Stop Point-->
        <div
            v-for="(point, index) in routeResponse.route"
            :key="point.id"
            class="relative flex cursor-pointer"
            :class="[index === 0 ? 'mt-0' : 'mt-8', index === routeResponse.route.length - 1 ? 'items-end' : 'items-start']"
        >
          <div class="flex flex-col items-center mr-4">
            <!-- Timeline Point Indicator -->
            <div class="w-3 h-3 rounded-full bg-secondary-600" />
          </div>

          <!-- Stop Details -->
          <div class="grid gap-2">
            <p class="font-medium leading-3">{{ point.name }}</p>
            <p
                v-if="index !== routeResponse.route.length - 1"
                class="text-xs font-medium text-gray-600">
              {{formattedTravelTime(routeResponse.route[index + 1].travel_time)}}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

// Types for RoutePoint and FindRouteResponse
export type RoutePoint = {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  travel_time: number;
  stop_name: string;
};

export type FindRouteResponse = {
  departure: string;
  destination: string;
  route: RoutePoint[];
  total_travel_time: number;
};

export default defineComponent({
  name: 'TimelineItinerary',
  props: {
    routeResponse: {
      type: Object as () => FindRouteResponse,
      required: true,
    },
  },
  methods: {
    // Format the time in minutes to hours and minutes
    minutesToHoursStr(minutes: number): string {
      const hours = Math.floor(minutes / 60);
      const remainingMinutes = minutes % 60;
      return `${hours}h ${remainingMinutes}m`;
    },
    // Format travel time between points
    formattedTravelTime(travelTime: number): string {
      return travelTime >= 60
          ? this.minutesToHoursStr(travelTime)
          : `${travelTime} minutes`;
    },
  },
});
</script>
