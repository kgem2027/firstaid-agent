import pino from 'pino';
import DDPlants from "../model/DDPlants.Model.js";
import Farmacies from "../model/Farmacies.Model.js";
import Ethnobotanies from "../model/Ethnobotanies.Model.js";

const logger = pino({
    level: 'debug',
    transport: {
        target: 'pino-pretty',
        options: { colorize: true }
    }
});

const findPlantChemicals = async (taxon) => {
    try {
        const [plant, chemicals, ethnobotany] = await Promise.all([
            DDPlants.findOne({ taxon }),
            Farmacies.find({ taxon }),
            Ethnobotanies.find({ taxon })
        ]);

        if (!plant) {
            logger.warn(`No plant found for taxon: ${taxon}`);
            return null;
        }

        logger.debug({ taxon, chemicalsFound: chemicals.length }, 'Plant chemicals fetched');

        return { plant, chemicals, ethnobotany };
    } catch (error) {
        logger.error({ err: error, taxon }, 'Error fetching plant chemicals');
        throw error;
    }
};

export default { findPlantChemicals };
