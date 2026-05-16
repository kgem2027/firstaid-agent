import express from 'express'
import plantService from '../service/Plants.Service.js'
import { protect } from '../middleware/auth.js'

const router = express.Router()

router.get('/nearby', protect, async (req, res) => {
    try {
        const { latitude, longitude } = req.query

        if (!latitude || !longitude) {
            return res.status(400).json({ message: 'Latitude and longitude are required' })
        }

        const plants = await plantService.getNearbyPlants(
            parseFloat(latitude),
            parseFloat(longitude)
        )

        return res.status(200).json({ plants })

    } catch (error) {
        return res.status(500).json({ message: error.message })
    }
})

export default router