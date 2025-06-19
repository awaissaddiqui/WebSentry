import { defineStore } from 'pinia'
import { configApi } from '../api'

export const useConfigStore = defineStore('config', {
  state: () => ({
    config: null,
    vulnerabilityLibrary: null,
    isLoading: false,
    error: null
  }),

  actions: {
    // Fetch configuration
    async fetchConfig() {
      this.isLoading = true;
      this.error = null;

      try {
        this.config = await configApi.getConfig();
        return this.config;
      } catch (err) {
        this.error = err.message || 'Failed to fetch configuration';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    // Update configuration
    async updateConfig(configData) {
      this.isLoading = true;
      this.error = null;

      try {
        this.config = await configApi.updateConfig(configData);
        return this.config;
      } catch (err) {
        this.error = err.message || 'Failed to update configuration';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch vulnerability library
    async fetchVulnerabilityLibrary() {
      this.isLoading = true;
      this.error = null;

      try {
        this.vulnerabilityLibrary = await configApi.getVulnerabilityLibrary();
        return this.vulnerabilityLibrary;
      } catch (err) {
        this.error = err.message || 'Failed to fetch vulnerability library';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    // Update vulnerability rule
    async updateVulnerabilityRule(vulnType, ruleData) {
      this.isLoading = true;
      this.error = null;

      try {
        const updatedRule = await configApi.updateVulnerabilityRule(vulnType, ruleData);

        // Update local state
        if (this.vulnerabilityLibrary) {
          this.vulnerabilityLibrary[vulnType] = updatedRule;
        }

        return updatedRule;
      } catch (err) {
        this.error = err.message || 'Failed to update vulnerability rule';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    // Reset configuration
    async resetConfig() {
      this.isLoading = true;
      this.error = null;

      try {
        this.config = await configApi.resetConfig();
        return this.config;
      } catch (err) {
        this.error = err.message || 'Failed to reset configuration';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    // Clear error
    clearError() {
      this.error = null;
    }
  }
})
