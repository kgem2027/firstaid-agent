import dotenv from 'dotenv';
dotenv.config();
import express from 'express';
import mongoose from 'mongoose';
import cors from 'cors'
import authRoutes from './routes/auth.js';
const app = express();
app.use(cors())

//middleware
app.use(express.json());
app.use(express.urlencoded({extended: false})); 




//routes
app.use('/api/auth', authRoutes);


mongoose.connect(process.env.MONGO_URI)
  .then(() => {
    console.log("Connected!");
    app.listen(process.env.PORT, () => console.log(`Server running on port ${process.env.PORT}`));
  })
.catch(err => console.log("Connection failed!", err));