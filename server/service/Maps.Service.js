import axios from 'axios'

const getLocationName = async (latitude, longitude) => {
    try {
        const response = await axios.get(
            `https://maps.googleapis.com/maps/api/geocode/json`, {
                params: {
                    latlng: `${latitude},${longitude}`,
                    key: process.env.GOOGLE_MAPS_API_KEY
                }
            }
        )

        const results = response.data.results
        if (!results || results.length === 0) {
            throw new Error('No location found for these coordinates')
        }

        const placeName = results[0].formatted_address
        return {
            latitude,
            longitude,
            placeName
        }

    } catch (error) {
        throw new Error(`Maps service error: ${error.message}`)
    }
}

export default { getLocationName }