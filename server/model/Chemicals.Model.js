import mongoose from "mongoose";

const ChemicalsSchema = new mongoose.Schema({
    chemId: {type: String},
    name: {type: String},
    casnum: {type: String},
    acticities: {type: [String]}
});

export default mongoose.model('Chemicals', ChemicalsSchema);