import express from 'express';
import coconutService from '../service/Coconut.Service.js'
import { protect } from '../middleware/auth.js'

const router = express.Router()

router.get('/plant/:scientificName', protect, async (req, res) => {
    try{
        const { scientificName } = req.params
        if (!scientificName) {
            return res.status(400).json({ message: 'Scientific name is required' })
        }
        const compounds = await coconutService.findPlantCompounds(scientificName)
        return res.status(200).json({ compounds })
    } catch (error) {
        return res.status(500).json({ message: error.message })
    }
})

export default router