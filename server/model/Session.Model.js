import mongoose from 'mongoose'
const SessionSchema = new mongoose.Schema({
    userID: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    sessionName: {
        type: String,
        default: 'Untitled Session'
    },
    symptomDescription: {
        type: String,
        required: true
    },
    photoUrl: {
        type: String
    },
    location: {
        latitude: Number,
        longitude: Number,
        placeName: String
    },
    results: {
        recommendedPlants: [
        {
            plantName: String,
            soothingCompounds: [String],
            preparationInstructions: String,
            safetyNotes: String
        }
        ],
        harmfulCompoundsFound: [String],
        disclaimer: String
    },
    createdAt: {
        type: Date,
        default: Date.now
    }
    })

export default mongoose.model('Session', SessionSchema);