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

      <!-- Display Anime Episodes in a Table -->
      <table v-if="results.downloads.length" border="1" cellspacing="0" cellpadding="5">
        <thead>
          <tr>
            <th>Episodes</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(result, index) in results.downloads" :key="index">
            <!---<td>{{ getEpisodeName(result) }}</td>-->
          <td>{{ result.split(" downloaded and saved to:")[0] }}</td>
            <td>Downloaded</td>
          </tr>
        </tbody>
      </table>

      <!--
      <ul>
        <li v-for="(result, index) in results.downloads" :key="index">{{ result }}</li>
      </ul>
      -->


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
    },
    getEpisodeName(result){
      // Assuming the prefix is known and consistent and optional 'Episode' string
      const prefix = 'Episode downloaded and saved to: ';
      // Check if the result contains the prefix
      if (result.includes(prefix)){
        // Remove the combined prefix and suffix from the result
        return result.replace(prefix, '').trim();
    }
          // Return the original result if the prefix is not found
    return result;
      
    }
  }
};
</script>

<style scoped>
/* Add your styles here */
table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 8px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f2f2f2;
}
</style>
