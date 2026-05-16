import axios from 'axios'

const getNearbyPlants = async (latitude, longitude) => {
    try {
        const response = await axios.get('https://api.inaturalist.org/v1/observations', {
            params: {
                lat: latitude,
                lng: longitude,
                radius: 50,              // 50km search radius
                taxon_name: 'Plantae',   // plants only
                quality_grade: 'research', // verified observations only
                per_page: 20,            // limit results
                order_by: 'observed_on'  // most recent first
            }
        })

        const results = response.data.results

        if (!results || results.length === 0) {
            throw new Error('No plants found in this area')
        }

        // Extract only what we need from each observation
        const plants = results
            .filter(obs => obs.taxon) // make sure taxon data exists
            .map(obs => ({
                id: obs.taxon.id,
                scientificName: obs.taxon.name,
                commonName: obs.taxon.preferred_common_name || obs.taxon.name,
                iconicTaxon: obs.taxon.iconic_taxon_name
            }))

        // Remove duplicates by scientific name
        const uniquePlants = plants.filter((plant, index, self) =>
            index === self.findIndex(p => p.scientificName === plant.scientificName)
        )

        return uniquePlants

    } catch (error) {
        throw new Error(`Plant service error: ${error.message}`)
    }
}

export default { getNearbyPlants }