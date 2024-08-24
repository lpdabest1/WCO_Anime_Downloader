<template>
  <div>
    <h1>Anime Downloader</h1>
    <form @submit.prevent="startScraping">
      <div>
        <label for="sign_in_url">Sign-In URL:</label>
        <input v-model="form.sign_in_url" id="sign_in_url" type="text" required />
      </div>
      <div>
        <label for="username">Username:</label>
        <input v-model="form.username" id="username" type="text" required />
      </div>
      <div>
        <label for="password">Password:</label>
        <input v-model="form.password" id="password" type="password" required />
      </div>
      <div>
        <label for="anime_url">Anime URL:</label>
        <input v-model="form.anime_url" id="anime_url" type="text" required />
      </div>
      <div>
        <label for="download_folder">Download Folder:</label>
        <input v-model="form.download_folder" id="download_folder" type="text" required />
      </div>
      <button type="submit">Start Scraping</button>
    </form>

    <div v-if="results">
      <h2>Results</h2>
      <!--<p>{{ results.message }}</p>-->
      <h3>{{ results.anime_title }}</h3>
      <img v-if="results.image_data_url" :src="results.image_data_url" alt="Anime Image" />
      <ul>
        <li v-for="(result, index) in results.downloads" :key="index">{{ result }}</li>
      </ul>
      <!-- Optionally, display the image path -->
      <p v-if="results.image_path">Image saved at: {{ results.image_path }}</p>
      <p>{{ results.message }}</p>
    </div>

    <!-- Bonus Section to Display Form Data -->
    <div v-if="formDataDisplayed">
      <h2>Entered Data</h2>
      <pre>{{ form }}</pre>
    </div>
    <!-- End of bonus section -->

  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AnimeScraper',
  data() {
    return {
      form: {
        sign_in_url: '',
        username: '',
        password: '',
        anime_url: '',
        download_folder: ''
      },
      results: null,
      formDataDisplayed: false // Track whether to display form data
    };
  },
  methods: {
    async startScraping() {
      try {
        const response = await axios.post('http://localhost:5000/scrape', this.form);
        this.results = response.data;

        // Display form data in Vue.js UI
        this.formDataDisplayed = true;

        // Log form data to console (Bonus)
        console.log('Form data:', this.form);


      } catch (error) {
        console.error('Error during scraping:', error);
      }
    }
  }
};
</script>

<style scoped>
/* Add your styles here */
</style>
