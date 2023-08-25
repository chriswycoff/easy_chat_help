
import {loginWithGoogle} from './auth.js';
import {login } from './auth.js';
import {logout} from './auth.js';
import { getAuth, onAuthStateChanged, createUserWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/9.23.0/firebase-auth.js";
const auth = getAuth();
onAuthStateChanged(auth, (user) => {
 let modal = document.getElementById("loginModal");
         if (user) {
             try{
             // User is signed in, hide the login button and show the logout button
             document.getElementById('google-login-btn').style.display = 'none';
             // document.getElementById('email-login-div').style.display = 'none';
             document.getElementById('login-btn-avatar').style.display = 'none';
             // document.getElementById('logout-btn').style.display = 'block';
             document.getElementById('logout-btn-avatar').style.display = 'block';
             modal.style.display = "none";
             // attach username above the logout button in the avatar container
             // console.log(user)
             document.getElementById('display-name').innerHTML = user.email;
             } catch (e) {
                 console.log(e)
             }
         } else {
             // User is signed out, show the login button and hide the logout button
             document.getElementById('google-login-btn').style.display = 'block';
             // document.getElementById('email-login-div').style.display = 'block';
             document.getElementById('logout-btn-avatar').style.display = 'none';
             document.getElementById('login-btn-avatar').style.display = 'block';
             // document.getElementById('logout-btn').style.display = 'none';
             document.getElementById('display-name').innerHTML = "";
         }
     });

window.addEventListener('DOMContentLoaded', (event) => {
         document.getElementById("email-login-btn").addEventListener("click", login);
         document.getElementById("google-login-btn").addEventListener("click", loginWithGoogle);
         // document.getElementById("logout-btn").addEventListener("click", logout);
         document.getElementById("logout-btn-avatar").addEventListener("click", logout);

     });

// Get the modal
var modal = document.getElementById("loginModal");

// Get the button that opens the modal
var loginBtn = document.getElementById("login-btn-avatar");

// When the user clicks the button, open the modal
loginBtn.onclick = function() {
modal.style.display = "block";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
if (event.target == modal) {
 console.log("Clicked outside modal")
 modal.style.display = "none";
}
}

// Event handler for logout button in avatar container
var logoutBtnAvatar = document.getElementById("logout-btn-avatar");
logoutBtnAvatar.onclick = function() {
// Add your logout logic here
modal.style.display = "none";
}


const signUpModal = document.getElementById('signUpModal');
const signUpLink = document.getElementById('sign-up-link-button'); //This id should be associated with the 'Sign up' hyperlink
const signUpBackBtn = document.getElementById('signup-back-btn');
const signUpBtn = document.getElementById('signup-btn'); // This is the actual sign up (create account) button
const signupEmailField = document.getElementById('signup-email-field');
const signupPasswordField = document.getElementById('signup-password-field');

signUpLink.addEventListener('click', (e) => {
e.preventDefault();
loginModal.style.display = "none";
signUpModal.style.display = "block";
});

signUpBackBtn.addEventListener('click', () => {
signUpModal.style.display = "none";
loginModal.style.display = "block";
});

signUpBtn.addEventListener('click', () => {
const email = signupEmailField.value;
const password = signupPasswordField.value;

// sign up with Firebase
createUserWithEmailAndPassword(auth, email, password)
.then((userCredential) => {
 // Signed up
 const user = userCredential.user;
 // you can close the sign-up modal here and open the login modal if you like
 signUpModal.style.display = "none";
 loginModal.style.display = "block";
})
.catch((error) => {
 const errorCode = error.code;
 const errorMessage = error.message;
 // Handle errors here, such as displaying a message to the user
});
});

