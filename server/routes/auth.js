import express from 'express';
import Users from '../model/Users.Model.js';
import jwt from 'jsonwebtoken';
import { protect } from "../middleware/auth.js";

const router = express.Router();

//Register
router.post('/register', async (req, res) => {
    try{
        const { name, email, password } = req.body;

        if(!name || !email || !password){
            return res.status(400).json({ message: "Please provide all required fields" });
        }
        const userExists = await Users.findOne({ email });
        if(userExists){
            return res.status(400).json({ message: "User already exists" });
        }
        const user = await Users.create({ name, email, password });

        const token = generateToken(user._id);
        return res.status(201).json({
            message: "User registered successfully",
            token,
            user: {
                _id: user._id,
                name: user.name,
                email: user.email
            }
        });
    }catch(error){
        return res.status(500).json({ message: "Error registering user", error: error.message });
    }
});

//Login
router.post('/login', async (req, res) => {
    try{
        const { email, password } = req.body;
        if(!email || !password){
            return res.status(400).json({ message: "Please provide email and password" });
        }
        const user = await Users.findOne({ email }).select("+password");
        if(!user){
            return res.status(400).json({ message: "Invalid email or password" });
        }
        const isMatch = await user.matchPassword(password);
        if(!isMatch){
            return res.status(400).json({ message: "Invalid email or password" });
        }
        const token = generateToken(user._id);
        return res.status(200).json({
            message: "Login successful",
            token,
            user: {
                _id: user._id,
                name: user.name,
                email: user.email
            }
        });
    }catch(error){
        return res.status(500).json({ message: "Error logging in", error: error.message });
    }
});
router.get("/me", protect, (req, res) => {
  res.status(200).json({ message: "User profile", user: req.user });
});
const generateToken = (id) => {
  return jwt.sign({ id }, process.env.JWT_SECRET, { expiresIn: "30d" });
};

export default router;