import mongoose from 'mongoose'
import bcrypt from 'bcrypt'
const UserSchema = new mongoose.Schema({
    name: {type: String, require: false, default:"User"},
    email: {type: String, require: true, unique: true},
    password: {type: String, require: true},
    sessions: [{type: mongoose.Schema.Types.ObjectId, ref: 'Session'}],
    }, {timestamps: true}
)
UserSchema.pre('save', async function () {
  if (!this.isModified('password')) return;

  const salt = await bcrypt.genSalt(10);
  this.password = await bcrypt.hash(this.password, salt);
});
UserSchema.methods.matchPassword = async function(enteredPassword){
    return await bcrypt.compare(enteredPassword, this.password);
}
const Users = mongoose.model('User', UserSchema);
export default Users;