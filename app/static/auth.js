// ============================================================================
// FIREBASE EMAIL/PASSWORD AUTH GATE
// ----------------------------------------------------------------------------
// Firebase Authentication stores the account (email + securely hashed
// password) for you -- FlashCart's own server/database never sees or stores
// the raw password. Once a person is signed in, this file reveals the main
// app (#appRoot) and starts it exactly once.
// ============================================================================

const auth = firebase.auth();
let flashCartAppStarted = false;

// ---------- Small DOM helpers ----------
function $(id) { return document.getElementById(id); }

function showAuthError(message) {
  const box = $("authErrorBox");
  box.textContent = message;
  box.classList.remove("hidden");
}

function clearAuthError() {
  const box = $("authErrorBox");
  box.classList.add("hidden");
  box.textContent = "";
}

function friendlyAuthError(err) {
  const map = {
    "auth/email-already-in-use": "That email is already registered. Try logging in instead.",
    "auth/invalid-email": "Please enter a valid email address.",
    "auth/weak-password": "Password should be at least 6 characters.",
    "auth/user-not-found": "No account found with that email. Try signing up.",
    "auth/wrong-password": "Incorrect password. Please try again.",
    "auth/invalid-credential": "Incorrect email or password.",
    "auth/too-many-requests": "Too many attempts. Please wait a moment and try again.",
    "auth/missing-password": "Please enter a password."
  };
  return map[err.code] || err.message || "Something went wrong. Please try again.";
}

// ---------- Tab switching (Log In / Sign Up) ----------
function setAuthTab(tab) {
  clearAuthError();
  const isLogin = tab === "login";
  $("authTabLogin").classList.toggle("border-brand-green", isLogin);
  $("authTabLogin").classList.toggle("text-brand-green", isLogin);
  $("authTabLogin").classList.toggle("border-transparent", !isLogin);
  $("authTabLogin").classList.toggle("text-slate-500", !isLogin);

  $("authTabSignup").classList.toggle("border-brand-green", !isLogin);
  $("authTabSignup").classList.toggle("text-brand-green", !isLogin);
  $("authTabSignup").classList.toggle("border-transparent", isLogin);
  $("authTabSignup").classList.toggle("text-slate-500", isLogin);

  $("loginForm").classList.toggle("hidden", !isLogin);
  $("signupForm").classList.toggle("hidden", isLogin);
}

// ---------- Sign Up ----------
async function handleSignup(e) {
  e.preventDefault();
  clearAuthError();

  const name = $("signupNameInput").value.trim();
  const email = $("signupEmailInput").value.trim();
  const password = $("signupPasswordInput").value;
  const confirm = $("signupConfirmInput").value;
  const btn = $("signupSubmitBtn");

  if (!name) return showAuthError("Please enter your name.");
  if (password.length < 6) return showAuthError("Password should be at least 6 characters.");
  if (password !== confirm) return showAuthError("Passwords do not match.");

  btn.disabled = true;
  btn.innerText = "Creating account...";
  try {
    const cred = await auth.createUserWithEmailAndPassword(email, password);
    await cred.user.updateProfile({ displayName: name });
    // Firebase now securely stores this account's email + password.
    // onAuthStateChanged below takes it from here.
  } catch (err) {
    showAuthError(friendlyAuthError(err));
    btn.disabled = false;
    btn.innerText = "Create Account";
  }
}

// ---------- Log In ----------
async function handleLogin(e) {
  e.preventDefault();
  clearAuthError();

  const email = $("loginEmailInput").value.trim();
  const password = $("loginPasswordInput").value;
  const btn = $("loginSubmitBtn");

  btn.disabled = true;
  btn.innerText = "Signing in...";
  try {
    await auth.signInWithEmailAndPassword(email, password);
  } catch (err) {
    showAuthError(friendlyAuthError(err));
    btn.disabled = false;
    btn.innerText = "Log In";
  }
}

// ---------- Forgot Password ----------
async function handleForgotPassword() {
  clearAuthError();
  const email = $("loginEmailInput").value.trim();
  if (!email) return showAuthError("Enter your email above first, then tap 'Forgot password?'.");
  try {
    await auth.sendPasswordResetEmail(email);
    showAuthError("Password reset email sent. Check your inbox.");
  } catch (err) {
    showAuthError(friendlyAuthError(err));
  }
}

// ---------- Log Out (called from the Profile tab in Settings) ----------
async function handleLogout() {
  try {
    await auth.signOut();
    flashCartAppStarted = false;
    location.reload();
  } catch (err) {
    console.error("Logout failed", err);
  }
}

// ---------- Auth state gate ----------
auth.onAuthStateChanged((user) => {
  const authScreen = $("authScreen");
  const appRoot = $("appRoot");

  if (user) {
    authScreen.classList.add("hidden");
    appRoot.classList.remove("hidden");

    // Reflect the signed-in identity in the header immediately.
    const label = user.displayName || (user.email ? user.email.split("@")[0] : "Account");
    const initials = label.split(" ").map(p => p[0]).join("").slice(0, 2).toUpperCase();
    const nameEl = $("navUserName");
    const avatarEl = $("navUserAvatar");
    if (nameEl) nameEl.innerText = label.split(" ")[0];
    if (avatarEl) avatarEl.innerText = initials;

    if (!flashCartAppStarted) {
      flashCartAppStarted = true;
      if (typeof window.startFlashCartApp === "function") {
        window.startFlashCartApp().then(() => {
          // Silently sync the Firebase identity into the app's profile
          // fields/backend record so Settings > Profile shows the real
          // logged-in email (no toast -- this isn't a user-initiated save).
          try {
            const emailInput = $("profileEmailInput");
            const nameInput = $("profileNameInput");
            if (emailInput) emailInput.value = user.email || "";
            if (nameInput && user.displayName) nameInput.value = user.displayName;

            fetch("/api/user/profile", {
              method: "PUT",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ name: user.displayName || undefined, email: user.email || undefined })
            }).catch(() => { /* non-fatal */ });
          } catch (e) { /* non-fatal */ }
        });
      }
    }
  } else {
    appRoot.classList.add("hidden");
    authScreen.classList.remove("hidden");
    if (typeof lucide !== "undefined") lucide.createIcons();
  }
});

// ---------- Wire up form listeners once DOM is ready ----------
document.addEventListener("DOMContentLoaded", () => {
  $("loginForm").addEventListener("submit", handleLogin);
  $("signupForm").addEventListener("submit", handleSignup);
  if (typeof lucide !== "undefined") lucide.createIcons();
});
