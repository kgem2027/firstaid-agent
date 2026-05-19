import express from 'express';
import ddPlantsService from '../service/DDPlants.Service.js';
import { protect } from '../middleware/auth.js';
const router = express.Router();

router.get('/chemicals', protect, async (req, res) => {
    try {
        const { taxon } = req.query;
        const result = await ddPlantsService.findPlantChemicals(taxon);
        res.json(result);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

export default router;