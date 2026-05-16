import axios from 'axios'

const BASE_URL = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name'
const CID_URL = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid'

const getPlantCompounds = async (plantName) => {
    try {
        // Step 1 - get the compound data by plant name
        const response = await axios.get(
            `${BASE_URL}/${encodeURIComponent(plantName)}/property/IUPACName,MolecularFormula,MolecularWeight/JSON`
        )

        const compounds = response.data.PropertyTable.Properties

        if (!compounds || compounds.length === 0) {
            return []
        }

        // Step 2 - get the CID (compound ID) to fetch safety data
        const cids = compounds.map(c => c.CID).slice(0, 5) // limit to 5 compounds

        // Step 3 - fetch biological activity / safety data for each compound
        const compoundDetails = await Promise.all(
            cids.map(async (cid) => {
                try {
                    const safetyRes = await axios.get(
                        `${CID_URL}/${cid}/property/IUPACName,MolecularFormula/JSON`
                    )
                    const props = safetyRes.data.PropertyTable.Properties[0]
                    return {
                        cid,
                        name: props.IUPACName || 'Unknown',
                        formula: props.MolecularFormula || 'Unknown'
                    }
                } catch {
                    return null
                }
            })
        )

        return compoundDetails.filter(Boolean) // remove any nulls

    } catch (error) {
        // PubChem returns 404 if plant not found - handle gracefully
        if (error.response?.status === 404) {
            return []
        }
        throw new Error(`PubChem service error: ${error.message}`)
    }
}

export default { getPlantCompounds }