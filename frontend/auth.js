 // Import the functions you need from the SDKs you need
 import { initializeApp } from "https://www.gstatic.com/firebasejs/9.23.0/firebase-app.js";
 import { getAnalytics } from "https://www.gstatic.com/firebasejs/9.23.0/firebase-analytics.js";
 import { getAuth, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/9.23.0/firebase-auth.js";
 import { signInWithEmailAndPassword, GoogleAuthProvider, signInWithPopup , signOut } from "https://www.gstatic.com/firebasejs/9.23.0/firebase-auth.js";

 // TODO: Add SDKs for Firebase products that you want to use
 // https://firebase.google.com/docs/web/setup#available-libraries

 // Your web app's Firebase configuration
 // For Firebase JS SDK v7.20.0 and later, measurementId is optional
 const firebaseConfig = {
   apiKey: "AIzaSyBshjCk64Ba3yD1UCIiCN6SparXE4iwDkw",
   authDomain: "easy-chat-help.firebaseapp.com",
   projectId: "easy-chat-help",
   storageBucket: "easy-chat-help.appspot.com",
   messagingSenderId: "99627717705",
   appId: "1:99627717705:web:6342fa3cdc1ee33445db98",
   measurementId: "G-DHSRZW44FK"
 };

 // Initialize Firebase
 const app = initializeApp(firebaseConfig);
 const analytics = getAnalytics(app);
 const auth = getAuth();

export async function login() {
 const email = document.getElementById("email-field").value;
 const password = document.getElementById("password-field").value;

 try {
     const userCredential = await signInWithEmailAndPassword(auth, email, password);
     // Signed in
     const user = userCredential.user;
    //  updateUserInformation(user);
    //  alert("Successfully logged in!");
 } catch (error) {
     var errorCode = error.code;
     var errorMessage = error.message;
     console.log(errorMessage)
     alert(errorMessage);
 }
}

export async function loginWithGoogle() {
    const provider = new GoogleAuthProvider();

    try {
    const result = await signInWithPopup(auth, provider);
    const user = result.user;
    // updateUserInformation(user);
    } catch (error) {
    var errorCode = error.code;
    var errorMessage = error.message;
    alert(errorMessage);
    }
}

export async function logout() {
    try {
        await signOut(auth);
        console.log("User signed out");
    } catch (error) {
        console.log(error.message);
    }
}

export function updateUserInformation(user) {
// If user's avatar is available
if(user.photoURL) {
 document.getElementById('user-avatar').src = user.photoURL; // Display user avatar
} else {
 // Default avatar
 document.getElementById('user-avatar').src = 'path-to-default-avatar.jpg';
}
}