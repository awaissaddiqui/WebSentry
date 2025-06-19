<template>
  <nav class="bg-white shadow-sm">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-20"> <!-- Increased height for prominence -->
        <div class="flex">
          <!-- Logo and app name -->
          <div class="flex-shrink-0 flex items-center">
            <router-link to="/" class="flex items-center">
              <img :src="logo" alt="Logo" class="h-14 w-14 rounded-md object-cover shadow-md" /> <!-- Increased size and added shadow -->
              <span class="ml-4 text-2xl font-extrabold text-primary tracking-wide company-name">CySmart.ai</span> <!-- Larger, bolder, spaced -->
            </router-link>
          </div>

          
          <!-- Navigation links -->
          <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
            <router-link 
              v-for="(item, index) in navItems" 
              :key="index" 
              :to="item.path"
              class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors duration-200"
              :class="[$route.path === item.path ? 'border-primary text-gray-900' : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700']"
            >
              {{ item.title }}
            </router-link>
          </div>
        </div>
        
        <!-- Mobile menu button -->
        <div class="flex items-center sm:hidden">
          <button 
            @click="isMobileMenuOpen = !isMobileMenuOpen" 
            type="button"
            class="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary"
            aria-controls="mobile-menu"
            :aria-expanded="isMobileMenuOpen"
          >
            <span class="sr-only">Open main menu</span>
            <svg 
              class="h-6 w-6" 
              xmlns="http://www.w3.org/2000/svg" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor" 
              aria-hidden="true"
            >
              <path 
                stroke-linecap="round" 
                stroke-linejoin="round" 
                stroke-width="2" 
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile menu -->
    <div 
      v-show="isMobileMenuOpen" 
      class="sm:hidden" 
      id="mobile-menu"
    >
      <div class="pt-2 pb-3 space-y-1">
        <router-link 
          v-for="(item, index) in navItems" 
          :key="index" 
          :to="item.path"
          class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium transition-colors duration-200"
          :class="[$route.path === item.path ? 'border-primary text-primary bg-primary-light' : 'border-transparent text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800']"
        >
          {{ item.title }}
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import logo from '../../imgs/logo.jpg'

const route = useRoute()
const isMobileMenuOpen = ref(false)

const navItems = [
  { title: 'Dashboard', path: '/' },
  { title: 'New Scan', path: '/scan' },
  { title: ' Incremental Scan', path: '/demo' },
  { title: 'Reports', path: '/reports' }
]
</script>

<style scoped>
/* Navbar styles */
.router-link-active {
  color: var(--primary-color, #1890ff);
  border-color: var(--primary-color, #1890ff);
}
.company-name {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--primary-color, #1890ff);
  letter-spacing: 0.04em;
  text-shadow: 0 2px 8px rgba(24,144,255,0.08);
}
</style>