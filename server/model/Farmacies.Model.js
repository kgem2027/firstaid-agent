import mongoose from "mongoose";

const FarmaciesSchema = new mongoose.Schema({
    fnfnum: {type: String},
    taxon: {type: String},
    chemId: {type: String},
    chemName: {type: String},
    partCode: {type: String},
    partName: {type: String},
    amtLo: {type: Number},
    amtHi: {type: Number},
    reference : {type: String},
    refYear: {type: String},
});

export default mongoose.model('Farmacies', FarmaciesSchema);