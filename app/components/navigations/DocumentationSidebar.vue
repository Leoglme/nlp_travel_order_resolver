<template>
  <aside
      class="block h-screen max-h-screen pt-5 pb-3 px-3 overflow-scroll bg-white z-20">
    <div
      v-for="(items, menuName) in menuItems"
      :key="menuName"
    >
      <h4 class="relative px-2 py-1 mb-2 text-sm font-semibold rounded-md">
        {{ menuName }}
      </h4>
      <div class="relative grid grid-flow-row text-sm mb-7 auto-rows-max">

        <NuxtLink
          v-for="item in items"
          :key="item.name"
          :to="item.url"
          :class="{ 'bg-gray-100 border-gray-200/60' : activeMenuItem.url == item.url, 'hover:underline border-transparent' : activeMenuItem.url != item.url }"
          class="group flex w-full items-center rounded-md border px-2 py-1.5 hover:underline border-transparent"
        >
          {{ item.name }}
        </NuxtLink>
      </div>
    </div>
  </aside>
</template>


<script lang="ts" setup>
import type {Ref} from "vue";

type MenuItem = {
  name: string
  url: string
}

type MenuItems = {
  [key: string]: MenuItem[]
}

/* HOOKS */
const route = useRoute()

/* REFS */
const menuItems: MenuItems = {
  'Presentation': [
    { name: 'Introduction', url: '/documentation' },
  ],
  'Guide Utilisateur': [
    { name: 'Guide d\'utilisation', url: '/documentation/user-guide/how-to-use' },
  ],
  'Documentation': [
    { name: 'Schema Architecture', url: '/documentation/architecture-schema' },
    { name: 'Analyse de décision', url: '/documentation/decision-analysis' },
    { name: 'Exemple de traitement', url: '/documentation/example-processing' },
    { name: 'Entrainement des modèles', url: '/documentation/model-training' },
  ],
  'Notebooks': [
    { name: 'LanguageIdentification', url: '/documentation/notebooks/language_identification_evaluation' },
    { name: 'TravelIntentClassifier', url: '/documentation/notebooks/travel-intent-classifier' },
    { name: 'CamembertNERModel', url: '/documentation/notebooks/camembert_ner_evaluation' },
    { name: 'SNCF Dijkstra', url: '/documentation/notebooks/sncf-route-finder' },
  ],
}

const activeMenuItem: Ref<MenuItem> = ref(Object.values(menuItems).flat().find((item) => item.url === route.path) || menuItems['Presentation'][0])

// Watch the route to update the active menu item
watch(() => route.path, (path: string) => {
  const menuItem: MenuItem | undefined = Object.values(menuItems).flat().find((item) => item.url === path)
  if (menuItem) {
    activeMenuItem.value = menuItem
  }
})
</script>
