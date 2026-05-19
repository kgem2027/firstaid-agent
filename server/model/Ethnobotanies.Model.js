import mongoose from "mongoose";

const EthnobotaniesSchema = new mongoose.Schema({
    fnfnum: {type: String},
    taxon: {type: String},
    activity : {type: String},
    country: {type: String},
    family: {type: String},
    reference: {type: String}
});

export default mongoose.model('Ethnobotanies', EthnobotaniesSchema);