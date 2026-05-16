import express from 'express'
import mapsService from '../service/Maps.Service.js'
import { protect } from '../middleware/auth.js'

const router = express.Router()

router.post('/geocode', protect, async (req, res) => {
    try {
        const { latitude, longitude } = req.body

        if (!latitude || !longitude) {
            return res.status(400).json({ message: 'Latitude and longitude are required' })
        }

        const location = await mapsService.getLocationName(latitude, longitude)
        return res.status(200).json({ location })

    } catch (error) {
        return res.status(500).json({ message: error.message })
    }
})

export default router