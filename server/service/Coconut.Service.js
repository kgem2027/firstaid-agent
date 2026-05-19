import axios from "axios";
const BASE_URL = "https://coconut.naturalproducts.net"

const getAccessToken = async () => {
    try {
        const response = await axios.post(`${BASE_URL}/api/auth/login`, {
            email: process.env.COCONUT_EMAIL,
            password: process.env.COCONUT_PASSWORD
        })
        return response.data.access_token
    } catch (error) {
        throw new Error(`Coconut service authentication error: ${error.message}`)
    }
}

const findPlantCompounds = async (scientificName) => {
    try {
        const accessToken = await getAccessToken();
        const response = await axios.post(`${BASE_URL}/api/molecules/search`,
            {
                search: {
                    scopes: [],
                    filters: [
                        {
                            field: 'name',
                            operator: 'like',
                            value: `%${scientificName.split(' ')[0]}%`
                        }
                    ],
                    sorts: []
                }
            },
            {
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                    'Content-Type': 'application/json'
                }
            }
        )
        const compounds = response.data.data
        if (!compounds || compounds.length === 0) {
            throw new Error(`No compounds found for ${scientificName}`)
        }
        return compounds.map(c => ({
            identifier: c.identifier,
            name: c.name,
            iupacName: c.iupac_name,
            smiles: c.canonical_smiles,
            status: c.status
        }));
    } catch (error) {
        throw new Error(`Coconut service error: ${error.message}`);
    }
}

export default { findPlantCompounds }