import mongoose from "mongoose";

const PlantsSchema = new mongoose.Schema({
    fnfnum: {type: String},
    taxon: {type: String},
    genus: {type: String},
    species: {type: String},
    family: {type: String},
    commonNames: {type: [String]}
});

export default mongoose.model('Plants', PlantsSchema);