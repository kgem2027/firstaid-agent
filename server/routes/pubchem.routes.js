import express from 'express'
import pubchemService from '../service/Pubchem.Service.js'
import { protect } from '../middleware/auth.js'
const router = express.Router()

router.get('/plant/:plantName', protect, async (req, res) => {
    try {
        const { plantName } = req.params
        if (!plantName) {
            return res.status(400).json({ message: 'Plant name is required' })
        }
        const compounds = await pubchemService.getPlantCompounds(plantName)
        return res.status(200).json({ compounds })
    } catch (error) {
        return res.status(500).json({ message: error.message })
    }
})

export default router