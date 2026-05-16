import dotenv from 'dotenv';
dotenv.config();
import express from 'express';
import mongoose from 'mongoose';
import cors from 'cors'
import authRoutes from './routes/auth.js';
import locationRoutes from './routes/location.routes.js';
import plantRoutes from './routes/plants.routes.js';
import pubchemRoutes from './routes/pubchem.routes.js';
const app = express();
app.use(cors())

//middleware
app.use(express.json());
app.use(express.urlencoded({extended: false})); 




//routes
app.use('/api/auth', authRoutes);
app.use('/api/location', locationRoutes);
app.use('/api/plants', plantRoutes);
app.use('/api/pubchem', pubchemRoutes);


mongoose.connect(process.env.MONGO_URI)
  .then(() => {
    console.log("Connected!");
    app.listen(process.env.PORT, () => console.log(`Server running on port ${process.env.PORT}`));
  })
.catch(err => console.log("Connection failed!", err));