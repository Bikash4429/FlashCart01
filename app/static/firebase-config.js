// ============================================================================
// FIREBASE CONFIGURATION
// ----------------------------------------------------------------------------
// 1. Go to https://console.firebase.google.com/ and create a project (free).
// 2. In your project, click the "</>" (Web) icon to register a web app.
// 3. Firebase will show you a config object exactly like the one below.
//    Copy YOUR values and paste them in place of the placeholders here.
// 4. In the left sidebar go to Build -> Authentication -> Get Started ->
//    Sign-in method -> enable "Email/Password".
// ----------------------------------------------------------------------------
// This file only contains PUBLIC identifiers (not secret). It is safe to ship
// this file to the browser -- Firebase web config is designed to be public.
// Real protection comes from Firebase Authentication itself + (optionally)
// Firestore/Realtime Database security rules.
// ============================================================================

const firebaseConfig = {
  apiKey: "AIzaSyAgaNZsrhR-lGrG-X6lYuZNcVGll1W9JXY",
  authDomain: "flashcart-69.firebaseapp.com",
  projectId: "flashcart-69",
  storageBucket: "flashcart-69.firebasestorage.app",
  messagingSenderId: "939993238643",
  appId: "1:939993238643:web:59d09b2964d77251172e06"
};

firebase.initializeApp(firebaseConfig);
